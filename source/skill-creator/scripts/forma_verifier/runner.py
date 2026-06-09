"""Verifier runner: discover SKILL.md files, classify the bundle, and apply rules."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, List, Union

from forma_verifier.report import Report, RuleResult
from forma_verifier.rules import (
    ALL_RULES,
    PLAN_FIRST_KINDS,
    SkillFile,
    BundleContext,
    plan_first_kind_from_name,
    parse_frontmatter,
)


def discover_skills(root: Path) -> List[SkillFile]:
    """Walk `root` and find every SKILL.md, returning parsed SkillFile records."""
    skills: List[SkillFile] = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        try:
            text = skill_md.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        frontmatter, body = parse_frontmatter(text)
        try:
            relative = skill_md.relative_to(root).as_posix()
        except ValueError:
            relative = str(skill_md)
        skills.append(SkillFile(
            path=skill_md,
            relative_path=relative,
            parent_dir_name=skill_md.parent.name,
            frontmatter=frontmatter,
            body=body,
        ))
    return skills


def classify_bundle(root: Path, skills: List[SkillFile], manifest: Dict[str, object]) -> str:
    """Classify the bundle: plan-first-bundle, creator-skill, or unknown.

    A manifest with emitted skills is authoritative and supports custom
    installable names. Without a manifest, if any skill's parent directory
    matches a plan-first kind (shape/gauge/seal/pour/flow), the current
    default installable Forma stage names (forma-plan/forma-ground/
    forma-lock/forma-execute/forma-showhand), or legacy installable names, the
    bundle is a plan-first-bundle. Otherwise a single SKILL.md is treated as a
    creator-skill; anything else is unknown.
    """
    if manifest.get("bundle_kind") == "plan-first-workflow" or isinstance(
        manifest.get("emitted_skills"), dict
    ):
        return "plan-first-bundle"
    for s in skills:
        if plan_first_kind_from_name(s.parent_dir_name) is not None:
            return "plan-first-bundle"
    # Also: if root itself is a plan-first kind directory and contains SKILL.md.
    if plan_first_kind_from_name(root.name) is not None and any(
        s.parent_dir_name == root.name for s in skills
    ):
        return "plan-first-bundle"
    if len(skills) == 1:
        return "creator-skill"
    return "unknown"


def load_manifest(root: Path) -> Dict[str, object]:
    """Load `.forma-manifest.json` when present, else return an empty mapping."""
    manifest_path = root / ".forma-manifest.json"
    if not manifest_path.is_file():
        return {}
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"_invalid": str(manifest_path)}
    if not isinstance(raw, dict):
        return {"_invalid": str(manifest_path)}
    return raw


def verify(path: Union[str, Path]) -> Report:
    """Verify a workflow bundle at `path`. Returns a Report (errors + warnings)."""
    root = Path(path).resolve()
    if not root.exists():
        report = Report(bundle_path=str(root), bundle_kind="unknown")
        report.results.append(RuleResult(
            "R000", "", "error", f"path does not exist: {root}"
        ))
        return report
    skills = discover_skills(root)
    if not skills:
        report = Report(bundle_path=str(root), bundle_kind="unknown")
        report.results.append(RuleResult(
            "R000", "", "error", "no SKILL.md files found in path"
        ))
        return report
    manifest = load_manifest(root)
    bundle_kind = classify_bundle(root, skills, manifest)
    ctx = BundleContext(
        root=root,
        skills=skills,
        bundle_kind=bundle_kind,
        manifest=manifest,
    )
    report = Report(bundle_path=str(root), bundle_kind=bundle_kind)
    for skill in skills:
        for rule in ALL_RULES:
            report.results.extend(rule(skill, ctx))
    return report


def main(argv: List[str] = None) -> int:
    """Entry point for the `verify.py` script and `python -m forma_verifier.runner`."""
    args = argv if argv is not None else sys.argv[1:]
    json_output = False
    paths: List[str] = []
    for arg in args:
        if arg == "--json":
            json_output = True
        else:
            paths.append(arg)
    if len(paths) != 1:
        print("usage: verify.py [--json] <path>", file=sys.stderr)
        return 2
    path = paths[0]
    report = verify(path)
    if json_output:
        print(report.format_json())
    else:
        print(report.format_human())
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
