"""Compose canonical plan-first fragments with resolved profiles."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Mapping, Sequence, Tuple

from forma.creator.profiles import (
    ConditionalOverlays,
    ConditionalRoute,
    ProfileConfig,
    ResourceSpec,
)


KINDS = ("shape", "gauge", "seal", "pour", "flow")
STAGE_SOURCE_DIR = "stages"
RUNNER_REFERENCE_NAMES = {"plan-template.md", "tasks-template.md"}
METHODOLOGY_RESOURCES: Mapping[str, Tuple[Tuple[str, str, bool], ...]] = {
    "shape": (
        ("resources/shape/references/output-format.md", "references/output-format.md", False),
        (
            "resources/shape/references/plan-issue-rules.md",
            "references/plan-issue-rules.md",
            False,
        ),
        ("resources/shared/script/github_issue_context.py", "script/github_issue_context.py", False),
    ),
    "gauge": (
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
    ),
    "seal": (
        ("resources/shared/references/planning-rules.md", "references/planning-rules.md", False),
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
        ("resources/shared/references/plan-template.md", "references/plan-template.md", False),
        ("resources/shared/references/tasks-template.md", "references/tasks-template.md", False),
        ("resources/shared/scripts/issue-workflow.sh", "scripts/issue-workflow.sh", True),
        ("resources/shared/script/github_issue_context.py", "script/github_issue_context.py", False),
    ),
    "pour": (
        ("resources/shared/references/execution-rules.md", "references/execution-rules.md", False),
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
        ("resources/shared/references/implement-notes.md", "references/implement-notes.md", False),
        ("resources/shared/references/plan-template.md", "references/plan-template.md", False),
        ("resources/shared/references/tasks-template.md", "references/tasks-template.md", False),
        ("resources/shared/scripts/issue-workflow.sh", "scripts/issue-workflow.sh", True),
    ),
    "flow": (
        ("resources/shared/references/execution-rules.md", "references/execution-rules.md", False),
        ("resources/shared/references/output-format.md", "references/output-format.md", False),
        ("resources/shared/references/implement-notes.md", "references/implement-notes.md", False),
        ("resources/shared/scripts/issue-workflow.sh", "scripts/issue-workflow.sh", True),
    ),
}

REQUIRED_STAGE_SECTIONS = (
    "Description",
    "Interaction Semantics",
    "Workflow",
    "Adds",
    "Output",
)
INCLUDE_PREFIX = "{{ include:"
INCLUDE_SUFFIX = "}}"


@dataclass(frozen=True)
class RequirementReferenceSpec:
    source_rel: str
    dest: str
    title: str


@dataclass(frozen=True)
class ResolvedRequirementReference:
    title: str
    resource: ResourceSpec
    bullet_items: Tuple[str, ...]


METHODOLOGY_REQUIREMENT_REFERENCES: Mapping[
    str, Tuple[RequirementReferenceSpec, ...]
] = {
    "shape": (
        RequirementReferenceSpec(
            "fragments/shape/decision-gate-adds.md",
            "references/proposal-decision-gate.md",
            "the proposal decision gate",
        ),
        RequirementReferenceSpec(
            "fragments/shape/handoff-adds.md",
            "references/grounding-handoff.md",
            "grounding handoff selection",
        ),
    ),
    "gauge": (),
    "seal": (
        RequirementReferenceSpec(
            "fragments/seal/decision-gate-adds.md",
            "references/finalization-decision-gate.md",
            "the finalization decision gate",
        ),
        RequirementReferenceSpec(
            "fragments/seal/plan-materialization-adds.md",
            "references/plan-materialization.md",
            "plan materialization",
        ),
        RequirementReferenceSpec(
            "fragments/seal/task-structure-adds.md",
            "references/task-structure.md",
            "task structure",
        ),
    ),
    "pour": (
        RequirementReferenceSpec(
            "fragments/pour/task-runner-adds.md",
            "references/task-runner.md",
            "review-gated task execution",
        ),
    ),
    "flow": (
        RequirementReferenceSpec(
            "fragments/flow/automated-execution-adds.md",
            "references/automated-execution.md",
            "automated execution",
        ),
    ),
}


@dataclass(frozen=True)
class StageSource:
    kind: str
    description: str
    interaction_lines: Tuple[str, ...]
    mode_check_lines: Tuple[str, ...]
    entry_gate_lines: Tuple[str, ...]
    workflow_lines: Tuple[str, ...]
    adds: Tuple[str, ...]
    output_lines: Tuple[str, ...]


@dataclass(frozen=True)
class ComposedSkill:
    kind: str
    description: str
    skill_md: str
    resources: Tuple[ResourceSpec, ...]


@dataclass(frozen=True)
class ComposedSuite:
    skills: Mapping[str, ComposedSkill]


def compose_suite(methodology_dir: Path, profile: ProfileConfig) -> ComposedSuite:
    """Return generated plan-first skill contents without writing files."""
    methodology_dir = methodology_dir.resolve()
    _require_methodology_files(methodology_dir)
    stage_sources = load_stage_sources(methodology_dir)
    skills: Dict[str, ComposedSkill] = {}
    for kind in KINDS:
        stage_source = stage_sources[kind]
        requirement_references = _requirement_references(methodology_dir, kind)
        methodology_resources = (
            *_methodology_resources(methodology_dir, kind),
            *(ref.resource for ref in requirement_references),
        )
        profile_resources = _resources_for_kind(kind, profile.resources)
        normal_resources = (*methodology_resources, *profile_resources)
        conditional_resources = _conditional_resources_for_kind(
            kind,
            profile.conditional_overlays,
        )
        resources = (*normal_resources, *conditional_resources)
        description = profile.skill_descriptions.get(kind, stage_source.description)
        skills[kind] = ComposedSkill(
            kind=kind,
            description=description,
            skill_md=_render_skill(
                kind=kind,
                stage_source=stage_source,
                description=description,
                profile=profile,
                resources=normal_resources,
                requirement_references=requirement_references,
                conditional_overlays=profile.conditional_overlays,
            ),
            resources=resources,
        )
    return ComposedSuite(skills=skills)


def _require_methodology_files(methodology_dir: Path) -> None:
    missing: List[str] = []
    for kind in KINDS:
        stage_rel = f"{STAGE_SOURCE_DIR}/{kind}.md"
        if not (methodology_dir / stage_rel).is_file():
            missing.append(stage_rel)
        for source_rel, _dest, _executable in METHODOLOGY_RESOURCES[kind]:
            if not (methodology_dir / source_rel).is_file():
                missing.append(source_rel)
        for spec in METHODOLOGY_REQUIREMENT_REFERENCES[kind]:
            if not (methodology_dir / spec.source_rel).is_file():
                missing.append(spec.source_rel)
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(
            f"methodology directory is incomplete: {methodology_dir} "
            f"(missing {missing_list})"
        )


def load_stage_sources(methodology_dir: Path) -> Mapping[str, StageSource]:
    """Load canonical stage body sources from `source/methodology/stages`."""
    methodology_dir = methodology_dir.resolve()
    sources: Dict[str, StageSource] = {}
    for kind in KINDS:
        sources[kind] = _load_stage_source(kind, methodology_dir)
    return sources


def _load_stage_source(kind: str, methodology_dir: Path) -> StageSource:
    source_path = methodology_dir / STAGE_SOURCE_DIR / f"{kind}.md"
    sections = _markdown_sections(_read_with_includes(source_path, methodology_dir))
    missing = [
        section for section in REQUIRED_STAGE_SECTIONS if not sections.get(section)
    ]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"{source_path} missing required sections: {missing_list}")
    return StageSource(
        kind=kind,
        description=_paragraph_text(sections["Description"], source_path, "Description"),
        interaction_lines=tuple(_section_lines(sections["Interaction Semantics"])),
        mode_check_lines=tuple(_section_lines(sections.get("Mode Check", []))),
        entry_gate_lines=tuple(_section_lines(sections.get("Entry Gate", []))),
        workflow_lines=tuple(_section_lines(sections["Workflow"])),
        adds=tuple(_bullet_items(sections["Adds"], source_path, "Adds")),
        output_lines=tuple(_section_lines(sections["Output"])),
    )


def _read_with_includes(path: Path, methodology_dir: Path) -> str:
    path = path.resolve()
    methodology_dir = methodology_dir.resolve()
    stack: Tuple[Path, ...] = ()
    return "\n".join(_expanded_lines(path, methodology_dir, stack))


def _expanded_lines(
    path: Path,
    methodology_dir: Path,
    stack: Tuple[Path, ...],
) -> List[str]:
    if path in stack:
        cycle = " -> ".join(item.relative_to(methodology_dir).as_posix() for item in (*stack, path))
        raise ValueError(f"methodology include cycle detected: {cycle}")
    lines: List[str] = []
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
        raise ValueError("methodology include directive must name a file")
    return rel


def _markdown_sections(text: str) -> Dict[str, List[str]]:
    sections: Dict[str, List[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        if line.startswith("## "):
            current = line[3:].strip()
            sections[current] = []
            continue
        if current is not None:
            sections[current].append(line)
    return sections


def _section_lines(lines: Sequence[str]) -> List[str]:
    result = list(lines)
    while result and not result[0].strip():
        result.pop(0)
    while result and not result[-1].strip():
        result.pop()
    return result


def _paragraph_text(lines: Sequence[str], source_path: Path, section: str) -> str:
    text = " ".join(line.strip() for line in _section_lines(lines) if line.strip())
    if not text:
        raise ValueError(f"{source_path} section {section!r} must not be empty")
    return text


def _bullet_items(lines: Sequence[str], source_path: Path, section: str) -> List[str]:
    items: List[str] = []
    for line in _section_lines(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if not stripped.startswith("- "):
            raise ValueError(
                f"{source_path} section {section!r} contains non-bullet line: "
                f"{stripped}"
            )
        items.append(stripped[2:].strip())
    if not items:
        raise ValueError(f"{source_path} section {section!r} must not be empty")
    return items


def _methodology_resources(methodology_dir: Path, kind: str) -> Tuple[ResourceSpec, ...]:
    resources: List[ResourceSpec] = []
    for source_rel, dest, executable in METHODOLOGY_RESOURCES[kind]:
        source = methodology_dir / source_rel
        content = None
        if kind == "flow" and dest == "scripts/issue-workflow.sh":
            text = source.read_text(encoding="utf-8")
            marker = 'ISSUE_WORKFLOW_INIT_DISABLED="0"'
            if marker not in text:
                raise ValueError(f"Runner source missing init-disable marker: {source}")
            content = text.replace(marker, 'ISSUE_WORKFLOW_INIT_DISABLED="1"', 1)
        resources.append(
            ResourceSpec(
                source=source,
                dest=dest,
                executable=executable,
                content=content,
            )
        )
    return tuple(resources)


def _requirement_references(
    methodology_dir: Path,
    kind: str,
) -> Tuple[ResolvedRequirementReference, ...]:
    references: List[ResolvedRequirementReference] = []
    for spec in METHODOLOGY_REQUIREMENT_REFERENCES[kind]:
        source_path = methodology_dir / spec.source_rel
        content = _read_with_includes(source_path, methodology_dir)
        content = _ensure_trailing_newline(content)
        references.append(
            ResolvedRequirementReference(
                title=spec.title,
                resource=ResourceSpec(
                    source=source_path,
                    dest=spec.dest,
                    executable=False,
                    content=content,
                ),
                bullet_items=tuple(
                    _bullet_items(content.splitlines(), source_path, spec.source_rel)
                ),
            )
        )
    return tuple(references)


def _ensure_trailing_newline(text: str) -> str:
    if text.endswith("\n"):
        return text
    return f"{text}\n"


def _render_skill(
    kind: str,
    stage_source: StageSource,
    description: str,
    profile: ProfileConfig,
    resources: Sequence[ResourceSpec],
    requirement_references: Sequence[ResolvedRequirementReference],
    conditional_overlays: ConditionalOverlays | None,
) -> str:
    stage = profile.stages[kind]
    requirements = _requirements_for_kind(
        stage_source,
        profile,
        requirement_references,
    )
    lines = [
        "---",
        f'name: "{stage.name}"',
        f'description: "{description}"',
        "---",
        "",
        f"# {stage.display_name}",
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

    lines.extend(
        [
            "## Workflow",
            "",
            *stage_source.workflow_lines,
            "",
        ]
    )

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
            *[f"- {line}" for line in _unique(requirements)],
            "",
            "## Output",
            "",
            *stage_source.output_lines,
            "",
        ]
    )
    return "\n".join(lines)


def _shape_reference_sections(resources: Sequence[ResourceSpec]) -> List[str]:
    always_names = {
        "output-format.md",
        "plan-issue-rules.md",
        "proposal-decision-gate.md",
        "grounding-handoff.md",
    }
    always_load = _reference_lines(resources, include_names=always_names)
    load_as_needed = _reference_lines(resources, exclude_names=always_names)
    return [
        "## Always Load",
        "",
        *_unique(always_load),
        "",
        "## Load As Needed",
        "",
        *_unique(load_as_needed),
        "",
    ]


def _seal_reference_section(resources: Sequence[ResourceSpec]) -> List[str]:
    return [
        "## Read After Gate",
        "",
        *_unique(_reference_lines(resources, exclude_names={"output-format.md"})),
        "",
    ]


def _execution_reference_sections(resources: Sequence[ResourceSpec]) -> List[str]:
    load_as_needed = _reference_lines(
        resources,
        exclude_names=RUNNER_REFERENCE_NAMES | {"output-format.md"},
    )
    return [
        "Read these files first:",
        "",
        "- `./plans/issue-<id>/plan.md`",
        "- `./plans/issue-<id>/tasks.md`",
        "",
        "## Load As Needed",
        "",
        *_unique(load_as_needed),
        "",
    ]


def _conditional_reference_section(
    kind: str,
    conditional_overlays: ConditionalOverlays,
) -> List[str]:
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


def _load_as_needed_section(lines: Sequence[str]) -> List[str]:
    return ["## Load As Needed", "", *_unique(lines), ""]


def _requirements_for_kind(
    stage_source: StageSource,
    profile: ProfileConfig,
    requirement_references: Sequence[ResolvedRequirementReference],
) -> List[str]:
    moved_items = {
        item
        for reference in requirement_references
        for item in reference.bullet_items
    }
    requirements = [item for item in stage_source.adds if item not in moved_items]
    requirements.extend(
        f"Load and follow `{reference.resource.dest}` for {reference.title}."
        for reference in requirement_references
    )
    kind = stage_source.kind
    requirements.extend(
        item
        for item in _commands_for_kind(kind, profile.constraints)
        if item not in moved_items
    )
    if profile.decision_gate_extras and kind == "shape":
        requirements.extend(
            f"Settle profile decision-gate dimension before proposal-ready: {item}"
            for item in profile.decision_gate_extras
        )
    validation_commands = _commands_for_kind(kind, profile.validation_commands)
    requirements.extend(
        f"Use profile validation command when it applies: `{command}`"
        for command in validation_commands
    )
    requirements.extend(_conditional_requirements(kind, profile.conditional_overlays))
    return requirements


def _conditional_requirements(
    kind: str,
    conditional_overlays: ConditionalOverlays | None,
) -> List[str]:
    if conditional_overlays is None:
        return []
    decision_name = conditional_overlays.decision.name
    if kind == "shape":
        requirements = [
            f"Settle `{decision_name}` as part of the Decision Gate before proposal-ready when conditional overlays are present.",
        ]
    elif kind == "seal":
        requirements = [
            f"Record finalized `{decision_name}` in `plan.md` so execution skills can read the route without re-deciding it.",
        ]
    elif kind in {"pour", "flow"}:
        requirements = [
            f"Read finalized `plan.md` and use recorded `{decision_name}` before applying conditional overlays; if `{decision_name}` is missing, {conditional_overlays.decision.missing_during_execution}.",
        ]
    else:
        requirements = [
            f"Carry recorded `{decision_name}` in the grounding handoff when it is available.",
        ]
    for route in conditional_overlays.routes:
        for overlay_id in route.overlays:
            overlay = conditional_overlays.overlays[overlay_id]
            for item in _items_for_kind(overlay.constraints, kind):
                requirements.append(
                    f"If `{decision_name}` is `{route.id}`, apply `{overlay_id}` overlay constraint: {item}"
                )
            for command in _items_for_kind(overlay.validation_commands, kind):
                requirements.append(
                    f"If `{decision_name}` is `{route.id}`, use `{overlay_id}` overlay validation command when it applies: `{command}`"
                )
    return requirements


def _reference_lines(
    resources: Sequence[ResourceSpec],
    include_names: set[str] | None = None,
    exclude_names: set[str] | None = None,
) -> List[str]:
    lines: List[str] = []
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


def _commands_for_kind(
    kind: str,
    mapping: Mapping[str, List[str]],
) -> List[str]:
    commands: List[str] = []
    commands.extend(mapping.get("default", []))
    commands.extend(mapping.get(kind, []))
    return commands


def _resources_for_kind(
    kind: str,
    resources: Mapping[str, Iterable[ResourceSpec]],
) -> List[ResourceSpec]:
    result: List[ResourceSpec] = []
    seen: set[str] = set()
    for key in ("default", kind):
        for resource in resources.get(key, []):
            if resource.dest in seen:
                result = [item for item in result if item.dest != resource.dest]
            seen.add(resource.dest)
            result.append(resource)
    return result


def _conditional_resources_for_kind(
    kind: str,
    conditional_overlays: ConditionalOverlays | None,
) -> List[ResourceSpec]:
    if conditional_overlays is None:
        return []
    result: List[ResourceSpec] = []
    seen: set[str] = set()
    for overlay in conditional_overlays.overlays.values():
        for resource in (
            *overlay.resources.get("default", ()),
            *overlay.resources.get(kind, ()),
        ):
            if resource.dest in seen:
                result = [item for item in result if item.dest != resource.dest]
            seen.add(resource.dest)
            result.append(resource)
    return result


def _conditional_route_reference_paths(
    kind: str,
    route: ConditionalRoute,
    conditional_overlays: ConditionalOverlays,
) -> List[str]:
    refs: List[str] = []
    for overlay_id in route.overlays:
        overlay = conditional_overlays.overlays[overlay_id]
        for resource in (
            *overlay.resources.get("default", ()),
            *overlay.resources.get(kind, ()),
        ):
            if resource.dest.startswith("references/") and resource.dest not in refs:
                refs.append(resource.dest)
    return refs


def _items_for_kind(
    mapping: Mapping[str, Sequence[str]],
    kind: str,
) -> List[str]:
    result: List[str] = []
    for key in ("default", kind):
        result.extend(mapping.get(key, ()))
    return result


def _unique(lines: Iterable[str]) -> List[str]:
    seen: set[str] = set()
    result: List[str] = []
    for line in lines:
        if line in seen:
            continue
        seen.add(line)
        result.append(line)
    return result
