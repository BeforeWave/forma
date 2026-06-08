"""Emit generated Forma workflow bundles to disk."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Iterable, Mapping, Set

from forma.creator.composer import ComposedSkill, KINDS, compose_bundle
from forma.creator.manifest import (
    build_manifest,
    methodology_dir_context,
)
from forma.creator.profiles import ProfileConfig, ResourceSpec, load_profile
from forma_verifier import verify

TARGETS = ("codex", "claude-code")


def build_bundle(
    profile_file: Path,
    output_dir: Path,
    target_agent: str,
    methodology_dir: Path | None = None,
) -> Path:
    """Create a task-level workflow bundle on disk and return the manifest path."""
    _assert_target(target_agent)
    with methodology_dir_context(methodology_dir) as resolved_methodology_dir:
        profile = load_profile(profile_file)
        bundle = compose_bundle(resolved_methodology_dir, profile)
        manifest = build_manifest(
            methodology_dir=resolved_methodology_dir,
            profile=profile,
            target_agent=target_agent,
        )
        emit_bundle(
            output_dir=output_dir,
            skills=bundle.skills,
            manifest=manifest,
            profile=profile,
            target_agent=target_agent,
        )
    report = verify(output_dir)
    if not report.passed:
        raise ValueError(report.format_human())
    return output_dir / ".forma-manifest.json"


def emit_bundle(
    output_dir: Path,
    skills: Mapping[str, ComposedSkill],
    manifest: Mapping[str, object],
    profile: ProfileConfig,
    target_agent: str,
) -> None:
    """Write a generated workflow bundle, replacing only known Forma output paths."""
    _assert_target(target_agent)
    output_dir = output_dir.resolve()
    enabled_kinds = [kind for kind in KINDS if profile.stages[kind].enabled]
    _prepare_output_dir(
        output_dir,
        {profile.stages[kind].directory for kind in enabled_kinds},
    )
    for kind in enabled_kinds:
        skill = skills[kind]
        stage = profile.stages[kind]
        skill_dir = output_dir / stage.directory
        skill_dir.mkdir(parents=True, exist_ok=True)
        (skill_dir / "SKILL.md").write_text(skill.skill_md, encoding="utf-8")
        _copy_resources(skill_dir, skill.resources)
        if target_agent == "codex":
            agents_dir = skill_dir / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            (agents_dir / "openai.yaml").write_text(
                _openai_yaml(skill, profile),
                encoding="utf-8",
            )
    (output_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _assert_target(target_agent: str) -> None:
    if target_agent not in TARGETS:
        allowed = ", ".join(TARGETS)
        raise ValueError(f"unsupported target {target_agent!r}; use {allowed}")


def _openai_yaml(skill: ComposedSkill, profile: ProfileConfig) -> str:
    stage = profile.stages[skill.kind]
    description = skill.description
    short_description = stage.short_description or description
    default_prompt = (
        stage.default_prompt
        or f"Use ${stage.name} for this plan-first workflow stage."
    )
    return "\n".join(
        [
            "interface:",
            f'  display_name: "{stage.display_name}"',
            f'  short_description: "{short_description}"',
            f'  default_prompt: "{default_prompt}"',
            "",
        ]
    )


def _copy_resources(skill_dir: Path, resources: Iterable[ResourceSpec]) -> None:
    for resource in resources:
        dest = skill_dir / resource.dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        if resource.content is None:
            shutil.copy2(resource.source, dest)
        else:
            dest.write_text(resource.content, encoding="utf-8")
        if resource.executable:
            dest.chmod(dest.stat().st_mode | 0o111)


def _prepare_output_dir(output_dir: Path, skill_dirs: Set[str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed = set(skill_dirs) | {".forma-manifest.json"}
    unexpected = _unexpected_children(output_dir, allowed)
    if unexpected:
        unexpected_list = ", ".join(sorted(unexpected))
        raise ValueError(
            f"output directory contains non-Forma files: {unexpected_list}; "
            "choose an empty directory or remove those files"
        )
    for skill_dir in skill_dirs:
        path = output_dir / skill_dir
        if path.exists():
            shutil.rmtree(path)
    manifest_path = output_dir / ".forma-manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()


def _unexpected_children(output_dir: Path, allowed: Set[str]) -> Iterable[str]:
    return [
        path.name
        for path in output_dir.iterdir()
        if path.name not in allowed
    ]
