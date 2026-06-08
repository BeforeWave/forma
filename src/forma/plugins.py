"""Build local Codex plugin artifacts from Forma workflow bundles."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Mapping

from forma.creator import build_bundle
from forma.creator.profiles import ProfileConfig, load_profile
from forma_verifier import verify
from forma_verifier.rules import parse_frontmatter


CODEX_PLUGIN_DESCRIPTION = (
    "Forma provides Plan-First workflow skills for grounded planning, locked task contracts, and evidence-backed execution."
)
STAGE_ORDER = ("shape", "gauge", "seal", "pour", "flow")
PLUGIN_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def build_codex_plugin(
    profile_file: Path,
    output_dir: Path,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a Codex plugin rooted at `output_dir` and return plugin.json."""
    output_dir = output_dir.resolve()
    _prepare_plugin_output_dir(output_dir)
    skills_dir = output_dir / "skills"
    manifest_path = build_bundle(
        profile_file=profile_file,
        output_dir=skills_dir,
        target_agent="codex",
        methodology_dir=methodology_dir,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path.unlink()
    (output_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    plugin_dir = output_dir / ".codex-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    profile = load_profile(profile_file)
    plugin_json = plugin_dir / "plugin.json"
    plugin_json.write_text(
        json.dumps(
            _plugin_manifest(profile, manifest, skills_dir),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report = verify(output_dir)
    if not report.passed:
        raise ValueError(report.format_human())
    return plugin_json


def _prepare_plugin_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed = {".codex-plugin", ".forma-manifest.json", "skills"}
    unexpected = [
        path.name
        for path in output_dir.iterdir()
        if path.name not in allowed
    ]
    if unexpected:
        unexpected_list = ", ".join(sorted(unexpected))
        raise ValueError(
            f"output directory contains non-Forma files: {unexpected_list}; "
            "choose an empty directory or remove those files"
        )
    for child in (output_dir / ".codex-plugin", output_dir / "skills"):
        if child.exists():
            shutil.rmtree(child)
    manifest_path = output_dir / ".forma-manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()


def _plugin_manifest(
    profile: ProfileConfig,
    manifest: Mapping[str, object],
    skills_dir: Path,
) -> dict[str, object]:
    plugin_id = _plugin_id(profile.bundle_name)
    skills = _plugin_skills(manifest, skills_dir)
    return {
        "id": plugin_id,
        "name": _plugin_display_name(plugin_id),
        "description": profile.bundle_description or CODEX_PLUGIN_DESCRIPTION,
        "skills": skills,
    }


def _plugin_id(bundle_name: str) -> str:
    value = bundle_name.strip()
    if not PLUGIN_ID_PATTERN.fullmatch(value):
        raise ValueError(
            f"bundle.name must be lower kebab-case for Codex plugin id: {bundle_name!r}"
        )
    return value


def _plugin_display_name(plugin_id: str) -> str:
    return " ".join(part.capitalize() for part in plugin_id.split("-"))


def _plugin_skills(
    manifest: Mapping[str, object],
    skills_dir: Path,
) -> list[dict[str, str]]:
    emitted = manifest.get("emitted_skills")
    if not isinstance(emitted, Mapping):
        raise ValueError(
            "bundle manifest must include emitted_skills for Codex plugin metadata"
        )
    skills: list[dict[str, str]] = []
    for kind in STAGE_ORDER:
        raw = emitted.get(kind)
        if raw is None:
            continue
        if not isinstance(raw, Mapping):
            raise ValueError(f"bundle manifest emitted_skills.{kind} must be an object")
        skill_id = _manifest_string(raw, "name", f"emitted_skills.{kind}.name")
        skill_dir = _manifest_string(
            raw,
            "directory",
            f"emitted_skills.{kind}.directory",
        )
        skill_file = skills_dir / skill_dir / "SKILL.md"
        if not skill_file.is_file():
            raise ValueError(
                f"emitted skill is missing SKILL.md: skills/{skill_dir}/SKILL.md"
            )
        frontmatter, _body = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
        description = frontmatter.get("description")
        skills.append(
            {
                "id": skill_id,
                "description": description if isinstance(description, str) else "",
            }
        )
    return skills


def _manifest_string(raw: Mapping[str, Any], key: str, field_name: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"bundle manifest {field_name} must be a non-empty string")
    return value.strip()
