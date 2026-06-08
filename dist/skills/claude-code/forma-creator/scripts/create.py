#!/usr/bin/env python3
"""Standalone installed Forma creator builder.

This script is bundled inside the installed `forma-creator` skill. It does not
load Layer 3 profiles. Agents convert the current conversation's one-off
natural-language injection into a temporary JSON file, then this script renders
the fixed target workflow bundle from bundled methodology resources and verifies it.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

from forma_verifier import verify


KINDS = ("shape", "gauge", "seal", "pour", "flow")
DEFAULT_SKILL_NAMES: Mapping[str, str] = {
    "shape": "forma-plan",
    "gauge": "forma-ground",
    "seal": "forma-lock",
    "pour": "forma-execute",
    "flow": "forma-showhand",
}
DEFAULT_PREFIX_SUFFIXES: Mapping[str, str] = {
    "shape": "plan",
    "gauge": "ground",
    "seal": "lock",
    "pour": "execute",
    "flow": "showhand",
}
FORMA_GENERATOR_NAME = "forma"
FORMA_GENERATOR_VERSION_FALLBACK = "0+unknown"
FORMA_GENERATOR_REPOSITORY_URL = "https://github.com/BeforeWave/forma"
STAGE_KEYS = ("default", *KINDS)
TARGETS = ("codex", "claude-code")
ARTIFACTS = ("bundle", "plugin")
DEFAULT_CODEX_PLUGIN_ID = "forma"
CODEX_PLUGIN_DESCRIPTION = (
    "Forma provides Plan-First workflow skills for grounded planning, locked task contracts, and evidence-backed execution."
)
CODEX_PLUGIN_VERSION = "0.1.0"
CODEX_PLUGIN_DEVELOPER = "Forma"
KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
REQUIRED_STAGE_SECTIONS = (
    "Description",
    "Interaction Semantics",
    "Workflow",
    "Adds",
    "Output",
)
INCLUDE_PREFIX = "{{ include:"
INCLUDE_SUFFIX = "}}"
RUNNER_REFERENCE_NAMES = {"plan-template.md", "tasks-template.md"}
ALLOWED_TOP_LEVEL_KEYS = {
    "rename",
    "stages",
    "resources",
    "skills",
    "validation_commands",
    "decision_gate_extras",
    "constraints",
    "conditional_overlays",
}
ALLOWED_RENAME_KEYS = {"prefix", "stages"}
ALLOWED_STAGE_CONFIG_KEYS = {"display_name", "short_description", "default_prompt"}
ALLOWED_SKILL_FIELD_KEYS = {"description"}
ALLOWED_RESOURCE_BUCKET_KEYS = {"references", "scripts", "files"}
ALLOWED_RESOURCE_ITEM_KEYS = {"source", "dest", "executable"}
ALLOWED_CONDITIONAL_KEYS = {"decision", "routes", "overlays"}
ALLOWED_CONDITIONAL_DECISION_KEYS = {
    "name",
    "must_record_in_plan",
    "missing_during_execution",
}
ALLOWED_CONDITIONAL_ROUTE_KEYS = {"id", "description", "overlays"}
ALLOWED_CONDITIONAL_OVERLAY_KEYS = {
    "description",
    "constraints",
    "resources",
    "validation_commands",
}


METHODOLOGY_RESOURCES: Mapping[str, tuple[tuple[str, str, bool], ...]] = {
    "shape": (
        ("resources/shape/references/output-format.md", "references/output-format.md", False),
        ("resources/shape/references/plan-issue-rules.md", "references/plan-issue-rules.md", False),
    ),
    "gauge": (
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
    ),
    "seal": (
        ("resources/shared/references/planning-rules.md", "references/planning-rules.md", False),
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
        ("resources/shared/references/plan-template.md", "references/plan-template.md", False),
        ("resources/shared/references/tasks-template.md", "references/tasks-template.md", False),
        ("resources/shared/scripts/forma-workflow.sh", "scripts/forma-workflow.sh", True),
    ),
    "pour": (
        ("resources/shared/references/execution-rules.md", "references/execution-rules.md", False),
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
        ("resources/shared/references/implement-notes.md", "references/implement-notes.md", False),
        ("resources/shared/references/plan-template.md", "references/plan-template.md", False),
        ("resources/shared/references/tasks-template.md", "references/tasks-template.md", False),
        ("resources/shared/scripts/forma-workflow.sh", "scripts/forma-workflow.sh", True),
    ),
    "flow": (
        ("resources/shared/references/execution-rules.md", "references/execution-rules.md", False),
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
        ("resources/shared/references/implement-notes.md", "references/implement-notes.md", False),
        ("resources/shared/scripts/forma-workflow.sh", "scripts/forma-workflow.sh", True),
    ),
}


REQUIREMENT_REFERENCES: Mapping[str, tuple[tuple[str, str, str], ...]] = {
    "shape": (
        (
            "fragments/shape/decision-gate-adds.md",
            "references/proposal-decision-gate.md",
            "the proposal decision gate",
        ),
        (
            "fragments/shape/handoff-adds.md",
            "references/grounding-handoff.md",
            "grounding handoff selection",
        ),
    ),
    "gauge": (),
    "seal": (
        (
            "fragments/seal/decision-gate-adds.md",
            "references/finalization-decision-gate.md",
            "the finalization decision gate",
        ),
        (
            "fragments/seal/plan-materialization-adds.md",
            "references/plan-materialization.md",
            "plan materialization",
        ),
        (
            "fragments/seal/task-structure-adds.md",
            "references/task-structure.md",
            "task structure",
        ),
    ),
    "pour": (
        (
            "fragments/pour/task-runner-adds.md",
            "references/task-runner.md",
            "review-gated task execution",
        ),
    ),
    "flow": (
        (
            "fragments/flow/automated-execution-adds.md",
            "references/automated-execution.md",
            "automated execution",
        ),
    ),
}


@dataclass(frozen=True)
class Resource:
    source: Path
    dest: str
    executable: bool
    content: str | None = None


@dataclass(frozen=True)
class StageSource:
    description: str
    interaction_lines: tuple[str, ...]
    mode_check_lines: tuple[str, ...]
    entry_gate_lines: tuple[str, ...]
    workflow_lines: tuple[str, ...]
    adds: tuple[str, ...]
    output_lines: tuple[str, ...]


@dataclass(frozen=True)
class RequirementReference:
    title: str
    resource: Resource
    bullet_items: tuple[str, ...]


@dataclass(frozen=True)
class ConditionalDecision:
    name: str
    must_record_in_plan: bool
    missing_during_execution: str


@dataclass(frozen=True)
class ConditionalRoute:
    id: str
    description: str
    overlays: tuple[str, ...]


@dataclass(frozen=True)
class ConditionalOverlay:
    id: str
    description: str
    constraints: Mapping[str, tuple[str, ...]]
    resources: Mapping[str, tuple[Resource, ...]]
    validation_commands: Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class ConditionalOverlays:
    decision: ConditionalDecision
    routes: tuple[ConditionalRoute, ...]
    overlays: Mapping[str, ConditionalOverlay]


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    creator_root = Path(__file__).resolve().parents[1]
    target = args.target or _detect_fixed_target(creator_root)
    methodology_dir = (
        args.methodology.resolve()
        if args.methodology
        else creator_root / "resources" / "plan-first" / "methodology"
    )
    injection = _load_injection(args.injection_json)
    creator_manifest = _load_creator_manifest(creator_root)
    if args.artifact == "plugin":
        if target != "codex":
            print(
                "error: plugin artifact is only supported for codex-targeted creators",
                file=sys.stderr,
            )
            return 2
        build_plugin(
            methodology_dir=methodology_dir,
            output_dir=args.output.resolve(),
            injection=injection,
            creator_manifest=creator_manifest,
        )
    else:
        build_bundle(
            methodology_dir=methodology_dir,
            output_dir=args.output.resolve(),
            target=target,
            injection=injection,
            creator_manifest=creator_manifest,
        )
    output_dir = args.output.resolve()
    report = verify(output_dir)
    print(report.format_human())
    if not report.passed:
        return 1
    if args.artifact == "plugin":
        print(f"forma creator build-plugin: wrote {args.output}")
        print(f"plugin manifest: {output_dir / '.codex-plugin' / 'plugin.json'}")
        print(
            "install hint: use `forma install --target codex --scope "
            f"<user|project> {output_dir}` or give this plugin path to the agent"
        )
    else:
        print(f"forma creator build-bundle: wrote {args.output}")
        print(
            "install hint: use `forma install --target "
            f"{target} --scope <user|project> {output_dir}` or give this bundle path to the agent"
        )
    return 0


def _parse_args(argv: Sequence[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a target-fixed Forma Plan-First workflow bundle from one-off injection JSON."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--artifact",
        choices=ARTIFACTS,
        default="bundle",
        help="Artifact to write. `bundle` is the default; `plugin` is Codex-only.",
    )
    parser.add_argument(
        "--injection-json",
        type=Path,
        help="Temporary JSON generated from the current conversation; not a tracked profile.",
    )
    parser.add_argument("--target", choices=TARGETS)
    parser.add_argument(
        "--methodology",
        type=Path,
        help="Bundled methodology override for tests. Defaults to the installed creator resources.",
    )
    return parser.parse_args(argv)


def _detect_fixed_target(creator_root: Path) -> str:
    text = (creator_root / "references" / "agent-target.md").read_text(encoding="utf-8")
    for target in TARGETS:
        if f"fixed to `{target}`" in text:
            return target
    raise ValueError("cannot detect fixed creator target from references/agent-target.md")


def _load_creator_manifest(creator_root: Path) -> dict[str, Any]:
    manifest_path = creator_root / ".forma-manifest.json"
    if not manifest_path.is_file():
        return {}
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return {}
    return raw


def _load_injection(path: Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("injection JSON must be an object")
    unknown = set(raw) - ALLOWED_TOP_LEVEL_KEYS
    if unknown:
        raise ValueError(f"injection JSON has unknown top-level keys: {', '.join(sorted(unknown))}")
    _validate_injection(raw, path)
    return raw


def _validate_injection(raw: Mapping[str, Any], path: Path) -> None:
    _validate_rename(raw.get("rename", {}))
    _validate_stage_mapping(raw.get("constraints", {}), "constraints", path)
    _validate_stage_mapping(raw.get("validation_commands", {}), "validation_commands", path)
    extras = raw.get("decision_gate_extras", [])
    if extras and not _is_string_list(extras):
        raise ValueError("decision_gate_extras must be a list of strings")
    stages = raw.get("stages", {})
    if stages:
        if not isinstance(stages, dict):
            raise ValueError("stages must be an object")
        _validate_stage_keys(stages, "stages")
        for kind, config in stages.items():
            if not isinstance(config, dict):
                raise ValueError(f"stages.{kind} must be an object")
            unknown = set(config) - ALLOWED_STAGE_CONFIG_KEYS
            if unknown:
                raise ValueError(
                    f"stages.{kind} has unsupported creator keys: {', '.join(sorted(unknown))}"
                )
    skills = raw.get("skills", {})
    if skills:
        if not isinstance(skills, dict):
            raise ValueError("skills must be an object")
        _validate_stage_keys(skills, "skills")
        for kind, config in skills.items():
            if not isinstance(config, dict):
                raise ValueError(f"skills.{kind} must be an object")
            unknown = set(config) - ALLOWED_SKILL_FIELD_KEYS
            if unknown:
                raise ValueError(f"skills.{kind} has unknown keys: {', '.join(sorted(unknown))}")
    _load_injected_resources(raw.get("resources", {}), path)
    _load_conditional_overlays(raw.get("conditional_overlays"), path)
    _validate_skill_names(_skill_names(raw))


def _validate_rename(value: Any) -> None:
    if not value:
        return
    if not isinstance(value, dict):
        raise ValueError("rename must be an object")
    unknown = set(value) - ALLOWED_RENAME_KEYS
    if unknown:
        raise ValueError(f"rename has unknown keys: {', '.join(sorted(unknown))}")
    prefix = value.get("prefix")
    if prefix is not None and (not isinstance(prefix, str) or not prefix.strip()):
        raise ValueError("rename.prefix must be a non-empty kebab-case string")
    if isinstance(prefix, str) and not KEBAB_CASE_RE.match(prefix.strip()):
        raise ValueError("rename.prefix must be kebab-case")
    stages = value.get("stages", {})
    if stages:
        if not isinstance(stages, dict):
            raise ValueError("rename.stages must be an object")
        _validate_stage_keys(stages, "rename.stages")
        seen: set[str] = set()
        for kind, name in stages.items():
            if not isinstance(name, str) or not name.strip():
                raise ValueError(f"rename.stages.{kind} must be a non-empty kebab-case string")
            name = name.strip()
            if not KEBAB_CASE_RE.match(name):
                raise ValueError(f"rename.stages.{kind} must be kebab-case")
            if name in KINDS:
                raise ValueError(f"rename.stages.{kind} must not use bare stage name `{name}`")
            if name in seen:
                raise ValueError(f"rename.stages has duplicate skill name: {name}")
            seen.add(name)


def _validate_skill_names(skill_names: Mapping[str, str]) -> None:
    seen: set[str] = set()
    for kind in KINDS:
        name = skill_names[kind]
        if name in KINDS:
            raise ValueError(f"generated skill name for {kind} must not use bare stage name `{name}`")
        if name in seen:
            raise ValueError(f"generated skill names must be unique; duplicate: {name}")
        seen.add(name)


def build_bundle(
    methodology_dir: Path,
    output_dir: Path,
    target: str,
    injection: Mapping[str, Any],
    creator_manifest: Mapping[str, Any] | None = None,
) -> None:
    if target not in TARGETS:
        raise ValueError(f"unsupported target: {target}")
    methodology_dir = methodology_dir.resolve()
    _require_methodology(methodology_dir)
    stage_sources = {
        kind: _load_stage_source(kind, methodology_dir)
        for kind in KINDS
    }
    skill_names = _skill_names(injection)
    _prepare_output_dir(output_dir, skill_names)
    injected_resources = _load_injected_resources(injection.get("resources", {}), None)
    conditional_overlays = _load_conditional_overlays(
        injection.get("conditional_overlays"),
        None,
    )
    for kind in KINDS:
        skill_name = skill_names[kind]
        stage_dir = output_dir / skill_name
        stage_dir.mkdir(parents=True, exist_ok=True)
        requirement_refs = _requirement_references(methodology_dir, kind)
        normal_resources = [
            *_methodology_resources(methodology_dir, kind),
            *(ref.resource for ref in requirement_refs),
            *injected_resources.get("default", []),
            *injected_resources.get(kind, []),
        ]
        conditional_resources = _conditional_resources_for_kind(kind, conditional_overlays)
        resources = [*normal_resources, *conditional_resources]
        description = _stage_description(kind, stage_sources[kind], injection)
        (stage_dir / "SKILL.md").write_text(
            _render_skill(
                kind=kind,
                skill_name=skill_name,
                stage_source=stage_sources[kind],
                description=description,
                injection=injection,
                resources=normal_resources,
                requirement_refs=requirement_refs,
                conditional_overlays=conditional_overlays,
            ),
            encoding="utf-8",
        )
        _copy_resources(stage_dir, resources)
        if target == "codex":
            agents_dir = stage_dir / "agents"
            agents_dir.mkdir(parents=True, exist_ok=True)
            (agents_dir / "openai.yaml").write_text(
                _openai_yaml(kind, description, injection, skill_names),
                encoding="utf-8",
            )
    _write_manifest(
        output_dir,
        target,
        skill_names,
        conditional_overlays,
        creator_manifest,
    )


def build_plugin(
    methodology_dir: Path,
    output_dir: Path,
    injection: Mapping[str, Any],
    creator_manifest: Mapping[str, Any] | None = None,
) -> None:
    """Build a Codex plugin artifact from the target-fixed creator source."""
    methodology_dir = methodology_dir.resolve()
    _require_methodology(methodology_dir)
    output_dir = output_dir.resolve()
    skill_names = _skill_names(injection)
    _prepare_plugin_output_dir(output_dir)
    skills_dir = output_dir / "skills"
    build_bundle(
        methodology_dir=methodology_dir,
        output_dir=skills_dir,
        target="codex",
        injection=injection,
        creator_manifest=creator_manifest,
    )
    nested_manifest = skills_dir / ".forma-manifest.json"
    manifest = json.loads(nested_manifest.read_text(encoding="utf-8"))
    nested_manifest.unlink()
    (output_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    plugin_dir = output_dir / ".codex-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            _plugin_manifest(
                injection=injection,
                skill_names=skill_names,
                descriptions=_skill_descriptions(methodology_dir, injection),
            ),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )


def _skill_names(injection: Mapping[str, Any]) -> dict[str, str]:
    rename = injection.get("rename", {})
    prefix: str | None = None
    overrides: Mapping[str, Any] = {}
    if isinstance(rename, dict):
        raw_prefix = rename.get("prefix")
        if isinstance(raw_prefix, str) and raw_prefix.strip():
            prefix = raw_prefix.strip()
        raw_overrides = rename.get("stages", {})
        if isinstance(raw_overrides, dict):
            overrides = raw_overrides
    names: dict[str, str] = {}
    for kind in KINDS:
        if overrides.get(kind):
            names[kind] = str(overrides[kind]).strip()
        elif prefix:
            names[kind] = f"{prefix}-{DEFAULT_PREFIX_SUFFIXES[kind]}"
        else:
            names[kind] = DEFAULT_SKILL_NAMES[kind]
    return names


def _skill_descriptions(
    methodology_dir: Path,
    injection: Mapping[str, Any],
) -> dict[str, str]:
    return {
        kind: _stage_description(kind, _load_stage_source(kind, methodology_dir), injection)
        for kind in KINDS
    }


def _plugin_manifest(
    injection: Mapping[str, Any],
    skill_names: Mapping[str, str],
    descriptions: Mapping[str, str],
) -> dict[str, object]:
    plugin_id = _plugin_id(injection)
    display_name = _plugin_display_name(plugin_id)
    return {
        "id": plugin_id,
        "name": plugin_id,
        "version": CODEX_PLUGIN_VERSION,
        "description": CODEX_PLUGIN_DESCRIPTION,
        "author": {
            "name": CODEX_PLUGIN_DEVELOPER,
        },
        "skills": "./skills/",
        "interface": {
            "displayName": display_name,
            "shortDescription": CODEX_PLUGIN_DESCRIPTION,
            "longDescription": CODEX_PLUGIN_DESCRIPTION,
            "developerName": CODEX_PLUGIN_DEVELOPER,
            "category": "Productivity",
            "capabilities": ["Read", "Write"],
            "defaultPrompt": _default_prompts(display_name),
            "brandColor": "#10A37F",
        },
    }


def _plugin_id(injection: Mapping[str, Any]) -> str:
    rename = injection.get("rename", {})
    if isinstance(rename, Mapping):
        raw_prefix = rename.get("prefix")
        if isinstance(raw_prefix, str) and raw_prefix.strip():
            return raw_prefix.strip()
    return DEFAULT_CODEX_PLUGIN_ID


def _plugin_display_name(plugin_id: str) -> str:
    return " ".join(part.capitalize() for part in plugin_id.split("-"))


def _default_prompts(display_name: str) -> list[str]:
    return [
        f"Use {display_name} to shape a plan-first issue.",
        f"Use {display_name} to execute the finalized plan.",
    ]


def _write_manifest(
    output_dir: Path,
    target: str,
    skill_names: Mapping[str, str],
    conditional_overlays: ConditionalOverlays | None,
    creator_manifest: Mapping[str, Any] | None,
) -> None:
    emitted = {
        kind: {
            "name": skill_names[kind],
            "directory": skill_names[kind],
        }
        for kind in KINDS
    }
    generator = _forma_generator_metadata(creator_manifest)
    manifest = {
        "format": "forma-bundle-manifest-v1",
        "mode": "solo",
        "bundle_kind": "plan-first-workflow",
        "target": target,
        "generator": generator,
        "generator_version": generator["version"],
        "emitted_order": list(KINDS),
        "emitted_skills": emitted,
    }
    creator_bundle = _creator_bundle_metadata(creator_manifest)
    if creator_bundle:
        manifest["creator_bundle"] = creator_bundle
    if conditional_overlays is not None:
        manifest["conditional_overlays"] = _conditional_manifest(conditional_overlays)
    (output_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _forma_generator_metadata(
    creator_manifest: Mapping[str, Any] | None,
) -> dict[str, str]:
    if creator_manifest:
        raw = creator_manifest.get("generator")
        if isinstance(raw, dict):
            name = raw.get("name")
            version = raw.get("version")
            repository_url = raw.get("repository_url")
            if isinstance(name, str) and isinstance(version, str):
                metadata = {"name": name, "version": version}
                if isinstance(repository_url, str):
                    metadata["repository_url"] = repository_url
                return metadata
    return {
        "name": FORMA_GENERATOR_NAME,
        "version": FORMA_GENERATOR_VERSION_FALLBACK,
        "repository_url": FORMA_GENERATOR_REPOSITORY_URL,
    }


def _creator_bundle_metadata(
    creator_manifest: Mapping[str, Any] | None,
) -> dict[str, Any]:
    if not creator_manifest:
        return {}
    result: dict[str, Any] = {}
    for key in (
        "format",
        "bundle_kind",
        "target",
        "generator",
        "generator_version",
        "generated_at",
    ):
        value = creator_manifest.get(key)
        if value is not None:
            result[key] = value
    creator = creator_manifest.get("creator")
    if isinstance(creator, dict):
        result["creator"] = {
            key: value
            for key in (
                "name",
                "directory",
                "source_revision",
                "source_revision_type",
                "source_tree_digest",
            )
            if (value := creator.get(key)) is not None
        }
    return result


def _require_methodology(methodology_dir: Path) -> None:
    missing: list[str] = []
    for kind in KINDS:
        if not (methodology_dir / "stages" / f"{kind}.md").is_file():
            missing.append(f"stages/{kind}.md")
        for source_rel, _dest, _executable in METHODOLOGY_RESOURCES[kind]:
            if not (methodology_dir / source_rel).is_file():
                missing.append(source_rel)
        for source_rel, _dest, _title in REQUIREMENT_REFERENCES[kind]:
            if not (methodology_dir / source_rel).is_file():
                missing.append(source_rel)
    if missing:
        raise ValueError(f"methodology is incomplete; missing {', '.join(missing)}")


def _load_stage_source(kind: str, methodology_dir: Path) -> StageSource:
    source_path = methodology_dir / "stages" / f"{kind}.md"
    sections = _markdown_sections(_read_with_includes(source_path, methodology_dir))
    missing = [name for name in REQUIRED_STAGE_SECTIONS if not sections.get(name)]
    if missing:
        raise ValueError(f"{source_path} missing required sections: {', '.join(missing)}")
    return StageSource(
        description=_paragraph_text(sections["Description"]),
        interaction_lines=tuple(_section_lines(sections["Interaction Semantics"])),
        mode_check_lines=tuple(_section_lines(sections.get("Mode Check", []))),
        entry_gate_lines=tuple(_section_lines(sections.get("Entry Gate", []))),
        workflow_lines=tuple(_section_lines(sections["Workflow"])),
        adds=tuple(_bullet_items(sections["Adds"], source_path)),
        output_lines=tuple(_section_lines(sections["Output"])),
    )


def _read_with_includes(path: Path, methodology_dir: Path) -> str:
    return "\n".join(_expanded_lines(path.resolve(), methodology_dir.resolve(), ()))


def _expanded_lines(path: Path, methodology_dir: Path, stack: tuple[Path, ...]) -> list[str]:
    if path in stack:
        cycle = " -> ".join(item.relative_to(methodology_dir).as_posix() for item in (*stack, path))
        raise ValueError(f"methodology include cycle detected: {cycle}")
    lines: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        rel = _include_path(line)
        if rel is None:
            lines.append(line)
            continue
        include_path = (methodology_dir / rel).resolve()
        if not include_path.is_relative_to(methodology_dir):
            raise ValueError(f"{path} include escapes methodology directory: {rel}")
        if not include_path.is_file():
            raise ValueError(f"{path} includes missing methodology fragment: {rel}")
        lines.extend(_expanded_lines(include_path, methodology_dir, (*stack, path)))
    return lines


def _include_path(line: str) -> str | None:
    stripped = line.strip()
    if not stripped.startswith(INCLUDE_PREFIX) or not stripped.endswith(INCLUDE_SUFFIX):
        return None
    rel = stripped[len(INCLUDE_PREFIX):-len(INCLUDE_SUFFIX)].strip()
    if not rel:
        raise ValueError("include directive must name a file")
    return rel


def _markdown_sections(text: str) -> dict[str, list[str]]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def _section_lines(lines: Sequence[str]) -> list[str]:
    result = list(lines)
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return result


def _paragraph_text(lines: Sequence[str]) -> str:
    return " ".join(line.strip() for line in _section_lines(lines) if line.strip())


def _bullet_items(lines: Sequence[str], source_path: Path) -> list[str]:
    items: list[str] = []
    for line in _section_lines(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("- "):
            raise ValueError(f"{source_path} contains non-bullet Adds line: {stripped}")
        items.append(stripped[2:].strip())
    if not items:
        raise ValueError(f"{source_path} Adds section must not be empty")
    return items


def _methodology_resources(methodology_dir: Path, kind: str) -> list[Resource]:
    resources: list[Resource] = []
    for source_rel, dest, executable in METHODOLOGY_RESOURCES[kind]:
        source = methodology_dir / source_rel
        content = None
        if kind == "flow" and dest == "scripts/forma-workflow.sh":
            text = source.read_text(encoding="utf-8")
            marker = 'ISSUE_WORKFLOW_INIT_DISABLED="0"'
            if marker not in text:
                raise ValueError(f"runner source missing init-disable marker: {source}")
            content = text.replace(marker, 'ISSUE_WORKFLOW_INIT_DISABLED="1"', 1)
        resources.append(Resource(source=source, dest=dest, executable=executable, content=content))
    return resources


def _requirement_references(methodology_dir: Path, kind: str) -> list[RequirementReference]:
    refs: list[RequirementReference] = []
    for source_rel, dest, title in REQUIREMENT_REFERENCES[kind]:
        source = methodology_dir / source_rel
        content = _read_with_includes(source, methodology_dir)
        if not content.endswith("\n"):
            content += "\n"
        refs.append(
            RequirementReference(
                title=title,
                resource=Resource(source=source, dest=dest, executable=False, content=content),
                bullet_items=tuple(_bullet_items(content.splitlines(), source)),
            )
        )
    return refs


def _stage_description(kind: str, stage_source: StageSource, injection: Mapping[str, Any]) -> str:
    skills = injection.get("skills", {})
    if isinstance(skills, dict):
        config = skills.get(kind, {})
        if isinstance(config, dict) and config.get("description"):
            return str(config["description"])
    return stage_source.description


def _stage_config(kind: str, injection: Mapping[str, Any]) -> Mapping[str, str]:
    stages = injection.get("stages", {})
    if isinstance(stages, dict) and isinstance(stages.get(kind), dict):
        return stages[kind]
    return {}


def _render_skill(
    kind: str,
    skill_name: str,
    stage_source: StageSource,
    description: str,
    injection: Mapping[str, Any],
    resources: Sequence[Resource],
    requirement_refs: Sequence[RequirementReference],
    conditional_overlays: ConditionalOverlays | None,
) -> str:
    stage_config = _stage_config(kind, injection)
    display_name = str(stage_config.get("display_name") or kind.replace("-", " ").title())
    lines = [
        "---",
        f'name: "{skill_name}"',
        f'description: "{description}"',
        "---",
        "",
        f"# {display_name}",
        "",
        description,
        "",
        "## Interaction Semantics",
        "",
        *stage_source.interaction_lines,
        "",
    ]
    if stage_source.mode_check_lines:
        lines.extend(["## Mode Check", "", *stage_source.mode_check_lines, ""])
    if stage_source.entry_gate_lines:
        lines.extend(["## Entry Gate", "", *stage_source.entry_gate_lines, ""])
    lines.extend(["## Workflow", "", *stage_source.workflow_lines, ""])
    if kind == "shape":
        lines.extend(_shape_reference_sections(resources))
    elif kind == "seal":
        lines.extend(_seal_reference_section(resources))
    elif kind in {"pour", "flow"}:
        lines.extend(_execution_reference_sections(resources))
    else:
        lines.extend(_load_as_needed_section(_reference_lines(resources, exclude_names={"output-format.md"})))
    if conditional_overlays is not None:
        lines.extend(_conditional_reference_section(kind, conditional_overlays))
    lines.extend(
        [
            "## Requirements",
            "",
            *[
                f"- {item}"
                for item in _requirements(
                    kind,
                    stage_source,
                    injection,
                    requirement_refs,
                    conditional_overlays,
                )
            ],
            "",
            "## Output",
            "",
            *stage_source.output_lines,
            "",
        ]
    )
    return "\n".join(lines)


def _requirements(
    kind: str,
    stage_source: StageSource,
    injection: Mapping[str, Any],
    requirement_refs: Sequence[RequirementReference],
    conditional_overlays: ConditionalOverlays | None,
) -> list[str]:
    moved = {item for ref in requirement_refs for item in ref.bullet_items}
    result = [item for item in stage_source.adds if item not in moved]
    result.extend(
        f"Load and follow `{ref.resource.dest}` for {ref.title}."
        for ref in requirement_refs
    )
    for item in _stage_items(injection.get("constraints", {}), kind):
        if item not in moved:
            result.append(item)
    if kind == "shape":
        for item in injection.get("decision_gate_extras", []) or []:
            result.append(f"Settle injected decision-gate dimension before proposal-ready: {item}")
    for command in _stage_items(injection.get("validation_commands", {}), kind):
        result.append(
            f"Apply workflow validation gate when it is relevant to the current task: `{command}`"
        )
    result.extend(_conditional_requirements(kind, conditional_overlays))
    return _unique(result)


def _conditional_reference_section(
    kind: str,
    conditional_overlays: ConditionalOverlays,
) -> list[str]:
    decision_name = conditional_overlays.decision.name
    lines = [
        "## Conditional References",
        "",
        f"Use the recorded `{decision_name}` before loading overlay references.",
        "",
    ]
    for route in conditional_overlays.routes:
        refs = _conditional_route_reference_paths(kind, route, conditional_overlays)
        if not refs:
            lines.append(
                f"- If `{decision_name}` is `{route.id}`, do not load overlay references."
            )
            continue
        lines.append(f"- If `{decision_name}` is `{route.id}`, load:")
        lines.extend(f"  - `{ref}`" for ref in refs)
    lines.append("")
    return lines


def _conditional_requirements(
    kind: str,
    conditional_overlays: ConditionalOverlays | None,
) -> list[str]:
    if conditional_overlays is None:
        return []
    decision_name = conditional_overlays.decision.name
    if kind == "shape":
        result = [
            f"Settle `{decision_name}` as part of the Decision Gate before proposal-ready when conditional overlays are present.",
        ]
    elif kind == "seal":
        result = [
            f"Record finalized `{decision_name}` in `plan.md` so execution skills can read the route without re-deciding it.",
        ]
    elif kind in {"pour", "flow"}:
        result = [
            f"Read finalized `plan.md` and use recorded `{decision_name}` before applying conditional overlays; if `{decision_name}` is missing, {conditional_overlays.decision.missing_during_execution}.",
        ]
    else:
        result = [
            f"Carry recorded `{decision_name}` in the grounding handoff when it is available.",
        ]
    for route in conditional_overlays.routes:
        for overlay_id in route.overlays:
            overlay = conditional_overlays.overlays[overlay_id]
            for item in _items_for_kind(overlay.constraints, kind):
                result.append(
                    f"If `{decision_name}` is `{route.id}`, apply `{overlay_id}` overlay constraint: {item}"
                )
            for command in _items_for_kind(overlay.validation_commands, kind):
                result.append(
                    f"If `{decision_name}` is `{route.id}`, apply `{overlay_id}` overlay validation gate when it is relevant to the current task: `{command}`"
                )
    return result


def _shape_reference_sections(resources: Sequence[Resource]) -> list[str]:
    always_names = {
        "output-format.md",
        "plan-issue-rules.md",
        "proposal-decision-gate.md",
        "grounding-handoff.md",
    }
    return [
        "## Always Load",
        "",
        *_unique(_reference_lines(resources, include_names=always_names)),
        "",
        "## Load As Needed",
        "",
        *_unique(_reference_lines(resources, exclude_names=always_names)),
        "",
    ]


def _seal_reference_section(resources: Sequence[Resource]) -> list[str]:
    return [
        "## Read After Gate",
        "",
        *_unique(_reference_lines(resources, exclude_names={"output-format.md"})),
        "",
    ]


def _execution_reference_sections(resources: Sequence[Resource]) -> list[str]:
    return [
        "Read these files first:",
        "",
        "- `./plans/issue-<id>/plan.md`",
        "- `./plans/issue-<id>/tasks.md`",
        "",
        "## Load As Needed",
        "",
        *_unique(
            _reference_lines(
                resources,
                exclude_names=RUNNER_REFERENCE_NAMES | {"output-format.md"},
            )
        ),
        "",
    ]


def _load_as_needed_section(lines: Sequence[str]) -> list[str]:
    return ["## Load As Needed", "", *_unique(lines), ""]


def _reference_lines(
    resources: Sequence[Resource],
    include_names: set[str] | None = None,
    exclude_names: set[str] | None = None,
) -> list[str]:
    lines: list[str] = []
    for resource in resources:
        if not resource.dest.startswith("references/"):
            continue
        name = Path(resource.dest).name
        if include_names is not None and name not in include_names:
            continue
        if exclude_names is not None and name in exclude_names:
            continue
        lines.append(f"- `{resource.dest}`")
    return lines


def _openai_yaml(
    kind: str,
    description: str,
    injection: Mapping[str, Any],
    skill_names: Mapping[str, str],
) -> str:
    stage_config = _stage_config(kind, injection)
    display_name = str(stage_config.get("display_name") or kind.replace("-", " ").title())
    short_description = str(stage_config.get("short_description") or description)
    default_prompt = str(
        stage_config.get("default_prompt")
        or f"Use ${skill_names[kind]} for this plan-first workflow stage."
    )
    return "\n".join(
        [
            "interface:",
            f'  display_name: "{display_name}"',
            f'  short_description: "{short_description}"',
            f'  default_prompt: "{default_prompt}"',
            "",
        ]
    )


def _copy_resources(skill_dir: Path, resources: Iterable[Resource]) -> None:
    for resource in resources:
        dest = skill_dir / resource.dest
        dest.parent.mkdir(parents=True, exist_ok=True)
        if resource.content is None:
            shutil.copy2(resource.source, dest)
        else:
            dest.write_text(resource.content, encoding="utf-8")
        if resource.executable:
            dest.chmod(dest.stat().st_mode | 0o111)


def _load_injected_resources(value: Any, path: Path | None) -> dict[str, list[Resource]]:
    if not value:
        return {}
    if not isinstance(value, dict):
        raise ValueError("resources must be an object")
    _validate_stage_keys(value, "resources")
    result: dict[str, list[Resource]] = {}
    for stage, buckets in value.items():
        if not isinstance(buckets, dict):
            raise ValueError(f"resources.{stage} must be an object")
        unknown = set(buckets) - ALLOWED_RESOURCE_BUCKET_KEYS
        if unknown:
            raise ValueError(f"resources.{stage} has unknown buckets: {', '.join(sorted(unknown))}")
        stage_resources: list[Resource] = []
        for bucket, items in buckets.items():
            if not isinstance(items, list):
                raise ValueError(f"resources.{stage}.{bucket} must be a list")
            for index, item in enumerate(items):
                stage_resources.append(_load_resource_item(item, bucket, f"resources.{stage}.{bucket}[{index}]", path))
        result[stage] = stage_resources
    return result


def _load_conditional_overlays(
    value: Any,
    path: Path | None,
) -> ConditionalOverlays | None:
    if value is None or value == {}:
        return None
    if not isinstance(value, dict):
        raise ValueError("conditional_overlays must be an object")
    unknown = set(value) - ALLOWED_CONDITIONAL_KEYS
    if unknown:
        raise ValueError(
            "conditional_overlays has unknown keys: "
            f"{', '.join(sorted(unknown))}"
        )
    decision = _load_conditional_decision(value.get("decision"))
    routes = _load_conditional_routes(value.get("routes"))
    overlays = _load_conditional_overlay_specs(value.get("overlays", {}), path)
    overlay_ids = set(overlays)
    for route in routes:
        for overlay_id in route.overlays:
            if overlay_id not in overlay_ids:
                raise ValueError(
                    "conditional_overlays.routes references missing overlay: "
                    f"{route.id}.{overlay_id}"
                )
    return ConditionalOverlays(
        decision=decision,
        routes=tuple(routes),
        overlays=overlays,
    )


def _load_conditional_decision(value: Any) -> ConditionalDecision:
    if not isinstance(value, dict):
        raise ValueError("conditional_overlays.decision must be an object")
    unknown = set(value) - ALLOWED_CONDITIONAL_DECISION_KEYS
    if unknown:
        raise ValueError(
            "conditional_overlays.decision has unknown keys: "
            f"{', '.join(sorted(unknown))}"
        )
    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("conditional_overlays.decision.name must be a non-empty string")
    must_record = value.get("must_record_in_plan", True)
    if not isinstance(must_record, bool):
        raise ValueError("conditional_overlays.decision.must_record_in_plan must be boolean")
    if not must_record:
        raise ValueError("conditional_overlays.decision.must_record_in_plan must be true")
    missing = value.get("missing_during_execution", "stop-for-plan-correction")
    if not isinstance(missing, str) or not missing.strip():
        raise ValueError(
            "conditional_overlays.decision.missing_during_execution must be a non-empty string"
        )
    if missing.strip() != "stop-for-plan-correction":
        raise ValueError(
            "conditional_overlays.decision.missing_during_execution must be stop-for-plan-correction"
        )
    return ConditionalDecision(
        name=name.strip(),
        must_record_in_plan=must_record,
        missing_during_execution=missing.strip(),
    )


def _load_conditional_routes(value: Any) -> list[ConditionalRoute]:
    if not isinstance(value, list) or not value:
        raise ValueError("conditional_overlays.routes must be a non-empty list")
    routes: list[ConditionalRoute] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        field = f"conditional_overlays.routes[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{field} must be an object")
        unknown = set(item) - ALLOWED_CONDITIONAL_ROUTE_KEYS
        if unknown:
            raise ValueError(f"{field} has unknown keys: {', '.join(sorted(unknown))}")
        route_id = item.get("id")
        if not isinstance(route_id, str) or not route_id.strip():
            raise ValueError(f"{field}.id must be a non-empty kebab-case string")
        route_id = route_id.strip()
        if not KEBAB_CASE_RE.match(route_id):
            raise ValueError(f"{field}.id must be kebab-case")
        if route_id in seen:
            raise ValueError(f"conditional_overlays.routes has duplicate id: {route_id}")
        seen.add(route_id)
        description = item.get("description", "")
        if description is not None and not isinstance(description, str):
            raise ValueError(f"{field}.description must be a string")
        overlays = item.get("overlays", [])
        if not isinstance(overlays, list):
            raise ValueError(f"{field}.overlays must be a list")
        overlay_ids: list[str] = []
        overlay_seen: set[str] = set()
        for overlay_index, overlay_id in enumerate(overlays):
            if not isinstance(overlay_id, str) or not overlay_id.strip():
                raise ValueError(
                    f"{field}.overlays[{overlay_index}] must be a non-empty string"
                )
            overlay_id = overlay_id.strip()
            if not KEBAB_CASE_RE.match(overlay_id):
                raise ValueError(f"{field}.overlays[{overlay_index}] must be kebab-case")
            if overlay_id in overlay_seen:
                raise ValueError(f"{field}.overlays has duplicate id: {overlay_id}")
            overlay_seen.add(overlay_id)
            overlay_ids.append(overlay_id)
        routes.append(
            ConditionalRoute(
                id=route_id,
                description=(description or "").strip(),
                overlays=tuple(overlay_ids),
            )
        )
    return routes


def _load_conditional_overlay_specs(
    value: Any,
    path: Path | None,
) -> dict[str, ConditionalOverlay]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError("conditional_overlays.overlays must be an object")
    result: dict[str, ConditionalOverlay] = {}
    for overlay_id, item in value.items():
        if not isinstance(overlay_id, str) or not overlay_id.strip():
            raise ValueError("conditional_overlays.overlays keys must be non-empty")
        overlay_id = overlay_id.strip()
        if not KEBAB_CASE_RE.match(overlay_id):
            raise ValueError(f"conditional_overlays.overlays.{overlay_id} must be kebab-case")
        field = f"conditional_overlays.overlays.{overlay_id}"
        if not isinstance(item, dict):
            raise ValueError(f"{field} must be an object")
        unknown = set(item) - ALLOWED_CONDITIONAL_OVERLAY_KEYS
        if unknown:
            raise ValueError(f"{field} has unknown keys: {', '.join(sorted(unknown))}")
        description = item.get("description", "")
        if description is not None and not isinstance(description, str):
            raise ValueError(f"{field}.description must be a string")
        result[overlay_id] = ConditionalOverlay(
            id=overlay_id,
            description=(description or "").strip(),
            constraints=_stage_string_mapping(item.get("constraints", {}), f"{field}.constraints", path),
            resources=_tuple_resource_mapping(
                _load_injected_resources(item.get("resources", {}), path)
            ),
            validation_commands=_stage_string_mapping(
                item.get("validation_commands", {}),
                f"{field}.validation_commands",
                path,
            ),
        )
    return result


def _stage_string_mapping(
    value: Any,
    name: str,
    path: Path | None,
) -> dict[str, tuple[str, ...]]:
    if not value:
        return {}
    _validate_stage_mapping(value, name, path or Path("<injection>"))
    if isinstance(value, list):
        return {"default": tuple(item.strip() for item in value)}
    result: dict[str, tuple[str, ...]] = {}
    for stage, items in value.items():
        result[stage] = tuple(item.strip() for item in items)
    return result


def _tuple_resource_mapping(
    value: Mapping[str, Sequence[Resource]],
) -> dict[str, tuple[Resource, ...]]:
    return {stage: tuple(resources) for stage, resources in value.items()}


def _conditional_resources_for_kind(
    kind: str,
    conditional_overlays: ConditionalOverlays | None,
) -> list[Resource]:
    if conditional_overlays is None:
        return []
    resources: list[Resource] = []
    for overlay in conditional_overlays.overlays.values():
        resources = _replace_resources_by_dest(
            resources,
            [
                *overlay.resources.get("default", ()),
                *overlay.resources.get(kind, ()),
            ],
        )
    return resources


def _conditional_route_reference_paths(
    kind: str,
    route: ConditionalRoute,
    conditional_overlays: ConditionalOverlays,
) -> list[str]:
    refs: list[str] = []
    for overlay_id in route.overlays:
        overlay = conditional_overlays.overlays[overlay_id]
        for resource in (
            *overlay.resources.get("default", ()),
            *overlay.resources.get(kind, ()),
        ):
            if resource.dest.startswith("references/") and resource.dest not in refs:
                refs.append(resource.dest)
    return refs


def _replace_resources_by_dest(
    existing: Sequence[Resource],
    incoming: Sequence[Resource],
) -> list[Resource]:
    result = list(existing)
    for resource in incoming:
        for index, item in enumerate(result):
            if item.dest == resource.dest:
                result[index] = resource
                break
        else:
            result.append(resource)
    return result


def _items_for_kind(
    mapping: Mapping[str, Sequence[str]],
    kind: str,
) -> list[str]:
    result: list[str] = []
    for key in ("default", kind):
        result.extend(mapping.get(key, ()))
    return result


def _conditional_manifest(
    conditional_overlays: ConditionalOverlays,
) -> dict[str, object]:
    return {
        "decision": {
            "name": conditional_overlays.decision.name,
            "must_record_in_plan": conditional_overlays.decision.must_record_in_plan,
            "missing_during_execution": conditional_overlays.decision.missing_during_execution,
        },
        "routes": [
            {
                "id": route.id,
                "description": route.description,
                "overlays": list(route.overlays),
                "references": {
                    kind: _conditional_route_reference_paths(kind, route, conditional_overlays)
                    for kind in KINDS
                    if _conditional_route_reference_paths(kind, route, conditional_overlays)
                },
            }
            for route in conditional_overlays.routes
        ],
        "overlays": {
            overlay_id: {
                "description": overlay.description,
                "constraints": {
                    stage: list(items)
                    for stage, items in sorted(overlay.constraints.items())
                },
                "resources": {
                    stage: [resource.dest for resource in resources]
                    for stage, resources in sorted(overlay.resources.items())
                },
                "validation_commands": {
                    stage: list(items)
                    for stage, items in sorted(overlay.validation_commands.items())
                },
            }
            for overlay_id, overlay in sorted(conditional_overlays.overlays.items())
        },
    }


def _load_resource_item(value: Any, bucket: str, field: str, injection_path: Path | None) -> Resource:
    if not isinstance(value, dict):
        raise ValueError(f"{field} must be an object")
    unknown = set(value) - ALLOWED_RESOURCE_ITEM_KEYS
    if unknown:
        raise ValueError(f"{field} has unknown keys: {', '.join(sorted(unknown))}")
    raw_source = value.get("source")
    if not isinstance(raw_source, str) or not raw_source.strip():
        raise ValueError(f"{field}.source must be a non-empty string")
    source_path = Path(raw_source.strip()).expanduser()
    if not source_path.is_absolute():
        if injection_path is None:
            raise ValueError(f"{field}.source must be absolute when no injection file is provided")
        source_path = injection_path.parent / source_path
    source = source_path.resolve()
    if not source.is_file():
        raise ValueError(f"{field}.source does not exist: {raw_source}")
    raw_dest = value.get("dest")
    dest_text = source.name if raw_dest is None else str(raw_dest).strip()
    if not dest_text:
        raise ValueError(f"{field}.dest must be a non-empty string")
    _validate_relative_path(dest_text, f"{field}.dest")
    if bucket == "references":
        dest = f"references/{dest_text}"
    elif bucket == "scripts":
        dest = f"scripts/{dest_text}"
    else:
        dest = dest_text
    raw_executable = value.get("executable")
    executable = bucket == "scripts" if raw_executable is None else bool(raw_executable)
    return Resource(source=source, dest=dest, executable=executable)


def _prepare_output_dir(output_dir: Path, skill_names: Mapping[str, str]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed = {".forma-manifest.json", *skill_names.values()}
    unexpected = [path.name for path in output_dir.iterdir() if path.name not in allowed]
    if unexpected:
        raise ValueError(
            "output directory contains non-Forma files: "
            f"{', '.join(sorted(unexpected))}; choose an empty directory"
        )
    for kind in KINDS:
        path = output_dir / skill_names[kind]
        if path.exists():
            shutil.rmtree(path)


def _prepare_plugin_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed = {".codex-plugin", ".forma-manifest.json", "skills"}
    unexpected = [path.name for path in output_dir.iterdir() if path.name not in allowed]
    if unexpected:
        raise ValueError(
            "plugin output directory contains non-Forma files: "
            f"{', '.join(sorted(unexpected))}; choose an empty directory"
        )
    for child in (output_dir / ".codex-plugin", output_dir / "skills"):
        if child.exists():
            shutil.rmtree(child)
    manifest_path = output_dir / ".forma-manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()


def _validate_stage_mapping(value: Any, name: str, path: Path) -> None:
    if not value:
        return
    if isinstance(value, list):
        if not _is_string_list(value):
            raise ValueError(f"{name} list must contain only strings")
        return
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object or list")
    _validate_stage_keys(value, name)
    for stage, items in value.items():
        if not _is_string_list(items):
            raise ValueError(f"{name}.{stage} must be a list of strings")


def _validate_stage_keys(value: Mapping[str, Any], name: str) -> None:
    unknown = set(value) - set(STAGE_KEYS)
    if unknown:
        raise ValueError(f"{name} has unknown stage keys: {', '.join(sorted(unknown))}")


def _stage_items(value: Any, kind: str) -> list[str]:
    if isinstance(value, list):
        return [item.strip() for item in value if item.strip()]
    if not isinstance(value, dict):
        return []
    result: list[str] = []
    for key in ("default", kind):
        items = value.get(key, [])
        if isinstance(items, list):
            result.extend(item.strip() for item in items if isinstance(item, str) and item.strip())
    return result


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item.strip() for item in value)


def _validate_relative_path(value: str, field: str) -> None:
    path = Path(value)
    if path.is_absolute() or ".." in path.parts:
        raise ValueError(f"{field} must be a relative path that does not escape the skill")


def _unique(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2)
