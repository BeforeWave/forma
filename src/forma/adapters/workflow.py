"""Target adapters for generated workflow bundles and plugins."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from forma.creator.composer import ComposedSkill
from forma.creator.profiles import ProfileConfig
from forma_verifier.rules import parse_frontmatter


WORKFLOW_TARGETS = ("codex", "claude-code", "opencode")
PLUGIN_TARGETS = ("codex", "claude-code")
STAGE_ORDER = ("shape", "gauge", "seal", "pour", "flow", "hone")
PLUGIN_ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CODEX_PLUGIN_DESCRIPTION = (
    "Forma provides Plan-First workflow skills for grounded planning, locked task contracts, and evidence-backed execution."
)
CODEX_PLUGIN_VERSION = "0.1.2"
CODEX_PLUGIN_DEVELOPER = "Forma"


def workflow_adapter(target_agent: str) -> "WorkflowTargetAdapter":
    assert_workflow_target(target_agent)
    return WorkflowTargetAdapter(target_agent)


def assert_workflow_target(target_agent: str) -> None:
    if target_agent not in WORKFLOW_TARGETS:
        allowed = ", ".join(WORKFLOW_TARGETS)
        raise ValueError(f"unsupported target {target_agent!r}; use {allowed}")


def plugin_id(bundle_name: str) -> str:
    value = bundle_name.strip()
    if not PLUGIN_ID_PATTERN.fullmatch(value):
        raise ValueError(
            f"bundle.name must be lower kebab-case for plugin id: {bundle_name!r}"
        )
    return value


class WorkflowTargetAdapter:
    """Encapsulate target-specific workflow artifact behavior."""

    def __init__(self, target_agent: str) -> None:
        assert_workflow_target(target_agent)
        self.target_agent = target_agent

    def assert_plugin_supported(self) -> None:
        if self.target_agent not in PLUGIN_TARGETS:
            raise ValueError(f"unsupported plugin target: {self.target_agent}")

    def skill_bundle_artifact_kind(self) -> str:
        return "skill-bundle"

    def plugin_artifact_kind(self) -> str:
        self.assert_plugin_supported()
        if self.target_agent == "codex":
            return "codex-plugin"
        if self.target_agent == "claude-code":
            return "claude-code-plugin"
        raise ValueError(f"unsupported plugin target: {self.target_agent}")

    def plugin_dir_name(self) -> str:
        self.assert_plugin_supported()
        if self.target_agent == "codex":
            return ".codex-plugin"
        if self.target_agent == "claude-code":
            return ".claude-plugin"
        raise ValueError(f"unsupported plugin target: {self.target_agent}")

    def decorate_skill_md(self, text: str, kind: str) -> str:
        if self.target_agent != "opencode":
            return text
        marker = "---\n\n"
        metadata = "\n".join(
            [
                "compatibility: opencode",
                "metadata:",
                f'  forma.stage: "{kind}"',
                '  forma.target: "opencode"',
            ]
        )
        if marker not in text:
            raise ValueError("generated SKILL.md is missing YAML frontmatter")
        return text.replace(marker, f"{metadata}\n---\n\n", 1)

    def write_skill_interface(
        self,
        skill_dir: Path,
        skill: ComposedSkill,
        profile: ProfileConfig,
    ) -> None:
        if self.target_agent != "codex":
            return
        agents_dir = skill_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        (agents_dir / "openai.yaml").write_text(
            self.openai_yaml(skill, profile),
            encoding="utf-8",
        )

    def openai_yaml(self, skill: ComposedSkill, profile: ProfileConfig) -> str:
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

    def localize_plugin_skills(
        self,
        manifest: Mapping[str, object],
        skills_dir: Path,
        plugin_name: str,
    ) -> dict[str, object]:
        self.assert_plugin_supported()
        localized = json.loads(json.dumps(manifest))
        emitted = localized.get("emitted_skills")
        if not isinstance(emitted, dict):
            raise ValueError(
                f"bundle manifest must include emitted_skills for {self.target_agent} plugin metadata"
            )
        prefix = f"{plugin_name}-"
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
                raise ValueError(f"{self.target_agent} plugin skill name for {kind} is empty")
            if not PLUGIN_ID_PATTERN.fullmatch(local_name):
                raise ValueError(
                    f"{self.target_agent} plugin skill name for {kind} is not kebab-case: "
                    f"{local_name!r}"
                )
            if local_name in used_names:
                raise ValueError(f"duplicate {self.target_agent} plugin skill name: {local_name}")
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
            if self.target_agent == "codex":
                qualified_name = f"{plugin_name}:{local_name}"
                _rewrite_codex_openai_prompt(
                    new_path / "agents" / "openai.yaml",
                    old_name,
                    local_name,
                    qualified_name,
                )
                raw["qualified_name"] = qualified_name
        return localized

    def plugin_manifest(
        self,
        profile: ProfileConfig,
        manifest: Mapping[str, object],
        skills_dir: Path,
    ) -> dict[str, object]:
        self.assert_plugin_supported()
        plugin_name = plugin_id(profile.bundle_name)
        _validate_plugin_skills(manifest, skills_dir)
        description = profile.bundle_description or CODEX_PLUGIN_DESCRIPTION
        if self.target_agent == "claude-code":
            return {
                "name": plugin_name,
                "version": CODEX_PLUGIN_VERSION,
                "description": description,
                "author": {
                    "name": CODEX_PLUGIN_DEVELOPER,
                },
                "skills": "./skills/",
            }
        display_name = profile.plugin_display_name or _plugin_display_name(plugin_name)
        return {
            "id": plugin_name,
            "name": plugin_name,
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


def _rewrite_codex_openai_prompt(
    openai_yaml: Path,
    old_name: str,
    local_name: str,
    qualified_name: str,
) -> None:
    if not openai_yaml.is_file():
        return
    text = openai_yaml.read_text(encoding="utf-8")
    updated = text.replace(f"${old_name}", f"${qualified_name}")
    updated = updated.replace(f"${local_name}", f"${qualified_name}")
    if updated != text:
        openai_yaml.write_text(updated, encoding="utf-8")


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


def _plugin_display_name(plugin_name: str) -> str:
    return " ".join(part.capitalize() for part in plugin_name.split("-"))


def _default_prompts(_display_name: str) -> list[str]:
    return [
        "Draft a scoped plan for this change.",
        "Execute the locked task plan.",
    ]


def _validate_plugin_skills(
    manifest: Mapping[str, object],
    skills_dir: Path,
) -> None:
    emitted = manifest.get("emitted_skills")
    if not isinstance(emitted, Mapping):
        raise ValueError(
            "bundle manifest must include emitted_skills for plugin metadata"
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
