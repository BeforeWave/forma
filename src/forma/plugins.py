"""Build local plugin artifacts from Forma workflow bundles."""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any, Mapping

from forma.base_origin import creator_base_origin
from forma.creator import build_bundle
from forma.creator.manifest import methodology_dir_context
from forma.creator.profiles import ProfileConfig, load_profile
from forma_verifier import verify
from forma_verifier.rules import parse_frontmatter


CODEX_PLUGIN_DESCRIPTION = (
    "Forma provides Plan-First workflow skills for grounded planning, locked task contracts, and evidence-backed execution."
)
CODEX_PLUGIN_VERSION = "0.1.1"
CODEX_PLUGIN_DEVELOPER = "Forma"
STAGE_ORDER = ("shape", "gauge", "seal", "pour", "flow", "hone")
PLUGIN_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def build_plugin(
    profile_file: Path,
    output_dir: Path,
    target_agent: str,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a target-specific plugin rooted at `output_dir` and return plugin.json."""
    if target_agent not in {"codex", "claude-code"}:
        raise ValueError(f"unsupported plugin target: {target_agent}")
    output_dir = output_dir.resolve()
    _prepare_plugin_output_dir(output_dir)
    skills_dir = output_dir / "skills"
    manifest_path = build_bundle(
        profile_file=profile_file,
        output_dir=skills_dir,
        target_agent=target_agent,
        methodology_dir=methodology_dir,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path.unlink()
    profile = load_profile(profile_file)
    plugin_id = _plugin_id(profile.bundle_name)
    if target_agent == "claude-code":
        manifest = _localize_claude_code_plugin_skills(
            manifest=manifest,
            skills_dir=skills_dir,
            plugin_id=plugin_id,
        )
    plugin_dir = output_dir / _plugin_dir_name(target_agent)
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin_json = plugin_dir / "plugin.json"
    plugin_json.write_text(
        json.dumps(
            _plugin_manifest(profile, manifest, skills_dir, target_agent),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    with methodology_dir_context(methodology_dir) as resolved_methodology_dir:
        base_origin = creator_base_origin(
            target_agent,
            _plugin_artifact_kind(target_agent),
            methodology_dir=resolved_methodology_dir,
        )
    manifest_with_origin = dict(manifest)
    manifest_with_origin["base_origin"] = base_origin
    (output_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest_with_origin, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = verify(output_dir)
    if not report.passed:
        raise ValueError(report.format_human())
    return plugin_json


def build_codex_plugin(
    profile_file: Path,
    output_dir: Path,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a Codex plugin rooted at `output_dir` and return plugin.json."""
    return build_plugin(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=methodology_dir,
    )


def build_claude_code_plugin(
    profile_file: Path,
    output_dir: Path,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a Claude Code plugin rooted at `output_dir` and return plugin.json."""
    return build_plugin(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="claude-code",
        methodology_dir=methodology_dir,
    )


def _prepare_plugin_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed = {".codex-plugin", ".claude-plugin", ".forma-manifest.json", "skills"}
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
    for child in (
        output_dir / ".codex-plugin",
        output_dir / ".claude-plugin",
        output_dir / "skills",
    ):
        if child.exists():
            shutil.rmtree(child)
    manifest_path = output_dir / ".forma-manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()


def _plugin_manifest(
    profile: ProfileConfig,
    manifest: Mapping[str, object],
    skills_dir: Path,
    target_agent: str,
) -> dict[str, object]:
    plugin_id = _plugin_id(profile.bundle_name)
    _validate_plugin_skills(manifest, skills_dir)
    description = profile.bundle_description or CODEX_PLUGIN_DESCRIPTION
    if target_agent == "claude-code":
        return {
            "name": plugin_id,
            "version": CODEX_PLUGIN_VERSION,
            "description": description,
            "author": {
                "name": CODEX_PLUGIN_DEVELOPER,
            },
            "skills": "./skills/",
        }
    display_name = _plugin_display_name(plugin_id)
    return {
        "id": plugin_id,
        "name": plugin_id,
        "version": CODEX_PLUGIN_VERSION,
        "description": description,
        "author": {
            "name": CODEX_PLUGIN_DEVELOPER,
        },
        "skills": "./skills/",
        "interface": {
            "displayName": display_name,
            "shortDescription": description,
            "longDescription": description,
            "developerName": CODEX_PLUGIN_DEVELOPER,
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "defaultPrompt": _default_prompts(display_name),
            "brandColor": "#10A37F",
        },
    }


def _plugin_id(bundle_name: str) -> str:
    value = bundle_name.strip()
    if not PLUGIN_ID_PATTERN.fullmatch(value):
        raise ValueError(
            f"bundle.name must be lower kebab-case for plugin id: {bundle_name!r}"
        )
    return value


def _plugin_dir_name(target_agent: str) -> str:
    if target_agent == "codex":
        return ".codex-plugin"
    if target_agent == "claude-code":
        return ".claude-plugin"
    raise ValueError(f"unsupported plugin target: {target_agent}")


def _plugin_artifact_kind(target_agent: str) -> str:
    if target_agent == "codex":
        return "codex-plugin"
    if target_agent == "claude-code":
        return "claude-code-plugin"
    raise ValueError(f"unsupported plugin target: {target_agent}")


def _localize_claude_code_plugin_skills(
    manifest: Mapping[str, object],
    skills_dir: Path,
    plugin_id: str,
) -> dict[str, object]:
    localized = json.loads(json.dumps(manifest))
    emitted = localized.get("emitted_skills")
    if not isinstance(emitted, dict):
        raise ValueError(
            "bundle manifest must include emitted_skills for Claude Code plugin metadata"
        )
    prefix = f"{plugin_id}-"
    used_names: set[str] = set()
    for kind in STAGE_ORDER:
        raw = emitted.get(kind)
        if raw is None:
            continue
        if not isinstance(raw, dict):
            raise ValueError(f"bundle manifest emitted_skills.{kind} must be an object")
        old_name = _manifest_string(raw, "name", f"emitted_skills.{kind}.name")
        old_dir = _manifest_string(raw, "directory", f"emitted_skills.{kind}.directory")
        local_name = old_name[len(prefix):] if old_name.startswith(prefix) else old_name
        if not local_name:
            raise ValueError(f"Claude Code plugin skill name for {kind} is empty")
        if not PLUGIN_ID_PATTERN.fullmatch(local_name):
            raise ValueError(
                f"Claude Code plugin skill name for {kind} is not kebab-case: "
                f"{local_name!r}"
            )
        if local_name in used_names:
            raise ValueError(f"duplicate Claude Code plugin skill name: {local_name}")
        used_names.add(local_name)
        old_path = skills_dir / old_dir
        new_path = skills_dir / local_name
        if not old_path.is_dir():
            raise ValueError(f"emitted skill directory is missing: skills/{old_dir}")
        if old_path != new_path:
            if new_path.exists():
                raise ValueError(
                    f"cannot rename skills/{old_dir} to skills/{local_name}; "
                    "destination already exists"
                )
            old_path.rename(new_path)
        _rewrite_skill_frontmatter_name(new_path / "SKILL.md", local_name)
        raw["name"] = local_name
        raw["directory"] = local_name
    return localized


def _rewrite_skill_frontmatter_name(skill_file: Path, name: str) -> None:
    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{skill_file} has no YAML frontmatter")
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            break
        key = lines[index].split(":", 1)[0].strip()
        if key == "name":
            lines[index] = f"name: {name}"
            skill_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
            return
    raise ValueError(f"{skill_file} frontmatter has no name")


def _plugin_display_name(plugin_id: str) -> str:
    return " ".join(part.capitalize() for part in plugin_id.split("-"))


def _default_prompts(_display_name: str) -> list[str]:
    return [
        "Draft a scoped plan for this change.",
        "Execute the finalized task plan.",
    ]


def _validate_plugin_skills(
    manifest: Mapping[str, object],
    skills_dir: Path,
) -> None:
    emitted = manifest.get("emitted_skills")
    if not isinstance(emitted, Mapping):
        raise ValueError(
            "bundle manifest must include emitted_skills for Codex plugin metadata"
        )
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
        if frontmatter.get("name") != skill_id:
            raise ValueError(
                f"emitted skill name {skill_id!r} must match "
                f"skills/{skill_dir}/SKILL.md frontmatter name"
            )


def _manifest_string(raw: Mapping[str, Any], key: str, field_name: str) -> str:
    value = raw.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"bundle manifest {field_name} must be a non-empty string")
    return value.strip()
