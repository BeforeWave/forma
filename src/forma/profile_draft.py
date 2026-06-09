"""Draft reviewable Forma profiles from explicit local rule sources."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import shutil
from typing import Iterable, List, Mapping, Sequence

import yaml

from forma.creator import load_profile


SUPPORTED_SOURCE_SUFFIXES = {".md", ".txt", ".yaml", ".yml"}
SKIPPED_DIRECTORY_NAMES = {".git", ".forma-workflow", "__pycache__", "dist"}
DRAFT_FILE_NAMES = ("profile.draft.yaml", "missing-decisions.md", "agent-review.md")
STAGE_KEYS = ("default", "shape", "gauge", "seal", "pour", "flow")

KEBAB_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CODE_SPAN_RE = re.compile(r"`([^`]+)`")
BULLET_RE = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


@dataclass(frozen=True)
class SourceFile:
    """A supported source file selected for draft extraction."""

    path: Path
    display_path: str
    text: str


@dataclass(frozen=True)
class SourceCollection:
    """Supported source files plus skipped files discovered during traversal."""

    files: tuple[SourceFile, ...]
    skipped_paths: tuple[str, ...]


@dataclass(frozen=True)
class MissingDecision:
    """A source line that should stay in human review instead of draft YAML."""

    source: str
    line: int
    reason: str
    text: str


@dataclass(frozen=True)
class DraftExtraction:
    """Extracted draft profile content and review-only decisions."""

    constraints: Mapping[str, tuple[str, ...]]
    validation_commands: Mapping[str, tuple[str, ...]]
    missing_decisions: tuple[MissingDecision, ...]


@dataclass(frozen=True)
class ProfileDraftResult:
    """Files and summary produced by a profile draft run."""

    output_dir: Path
    profile_file: Path
    missing_decisions_file: Path
    agent_review_file: Path
    source_files: tuple[str, ...]
    skipped_paths: tuple[str, ...]
    constraints_count: int
    validation_commands_count: int
    missing_decisions_count: int
    self_check: str


def create_profile_draft(
    *,
    profile_id: str,
    source_paths: Sequence[Path],
    output_dir: Path,
    bundle_name: str | None = None,
    org_name: str = "Local Team",
    replace: bool = False,
) -> ProfileDraftResult:
    """Create a three-file reviewable profile draft package."""
    profile_id = _validate_kebab(profile_id, "profile-id")
    if bundle_name is None:
        bundle_name = profile_id
    bundle_name = _validate_kebab(bundle_name, "bundle-name")
    org_name = org_name.strip()
    if not org_name:
        raise ValueError("org-name must be a non-empty string")

    collection = collect_source_files(source_paths)
    extraction = extract_draft_content(collection.files)

    output_dir = output_dir.resolve()
    _prepare_output_dir(output_dir, replace=replace)

    profile_file = output_dir / "profile.draft.yaml"
    missing_file = output_dir / "missing-decisions.md"
    review_file = output_dir / "agent-review.md"

    profile_file.write_text(
        render_profile_yaml(
            profile_id=profile_id,
            bundle_name=bundle_name,
            org_name=org_name,
            extraction=extraction,
        ),
        encoding="utf-8",
    )
    self_check = _self_check_profile(profile_file)
    missing_file.write_text(
        render_missing_decisions(extraction.missing_decisions),
        encoding="utf-8",
    )
    review_file.write_text(
        render_agent_review(
            profile_id=profile_id,
            bundle_name=bundle_name,
            org_name=org_name,
            collection=collection,
            extraction=extraction,
            self_check=self_check,
        ),
        encoding="utf-8",
    )

    return ProfileDraftResult(
        output_dir=output_dir,
        profile_file=profile_file,
        missing_decisions_file=missing_file,
        agent_review_file=review_file,
        source_files=tuple(item.display_path for item in collection.files),
        skipped_paths=collection.skipped_paths,
        constraints_count=sum(len(items) for items in extraction.constraints.values()),
        validation_commands_count=sum(
            len(items) for items in extraction.validation_commands.values()
        ),
        missing_decisions_count=len(extraction.missing_decisions),
        self_check=self_check,
    )


def collect_source_files(source_paths: Sequence[Path]) -> SourceCollection:
    """Collect supported source files from explicit file or directory inputs."""
    if not source_paths:
        raise ValueError("at least one --source is required")

    files: List[SourceFile] = []
    skipped: List[str] = []
    seen: set[Path] = set()

    for raw_source in source_paths:
        source = raw_source.expanduser().resolve()
        if not source.exists():
            raise ValueError(f"missing source: {raw_source}")
        if source.is_file():
            if source.suffix.lower() not in SUPPORTED_SOURCE_SUFFIXES:
                raise ValueError(f"unsupported source type: {raw_source}")
            _append_source_file(files, seen, source)
            continue
        if not source.is_dir():
            raise ValueError(f"unsupported source type: {raw_source}")
        for path in _walk_supported_files(source, skipped):
            _append_source_file(files, seen, path)

    if not files:
        raise ValueError("no supported source files found")
    return SourceCollection(files=tuple(files), skipped_paths=tuple(sorted(set(skipped))))


def extract_draft_content(source_files: Sequence[SourceFile]) -> DraftExtraction:
    """Conservatively extract durable-looking profile rules from source text."""
    constraints: dict[str, List[str]] = {stage: [] for stage in STAGE_KEYS}
    validation_commands: dict[str, List[str]] = {stage: [] for stage in STAGE_KEYS}
    missing: List[MissingDecision] = []

    for source in source_files:
        heading = ""
        for line_number, raw_line in enumerate(source.text.splitlines(), start=1):
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith("#"):
                heading = line.lstrip("#").strip()
                continue
            candidate = _candidate_text(line)
            if not candidate:
                continue
            if _looks_like_validation(candidate):
                stage = _stage_for_text(candidate, heading)
                for command in _extract_commands(candidate):
                    _append_unique(validation_commands[stage], command)
                continue
            if not _looks_like_rule(candidate):
                continue
            reason = _missing_decision_reason(candidate, heading)
            if reason:
                missing.append(
                    MissingDecision(
                        source=source.display_path,
                        line=line_number,
                        reason=reason,
                        text=_shorten(candidate),
                    )
                )
                continue
            stage = _stage_for_text(candidate, heading)
            _append_unique(constraints[stage], _shorten(candidate))

    compact_constraints = {
        stage: tuple(items)
        for stage, items in constraints.items()
        if items
    }
    compact_commands = {
        stage: tuple(items)
        for stage, items in validation_commands.items()
        if items
    }
    return DraftExtraction(
        constraints=compact_constraints,
        validation_commands=compact_commands,
        missing_decisions=tuple(missing),
    )


def render_profile_yaml(
    *,
    profile_id: str,
    bundle_name: str,
    org_name: str,
    extraction: DraftExtraction,
) -> str:
    """Render a profile draft that satisfies the tracked profile loader."""
    data: dict[str, object] = {
        "profile": {
            "id": profile_id,
            "description": (
                "Reviewable Forma profile draft generated from explicit local "
                "project-rule source files."
            ),
        },
        "bundle": {
            "name": bundle_name,
            "description": f"Reviewable Plan-First workflow bundle for {profile_id}.",
        },
        "org": {"name": org_name},
        "stages": _default_stage_config(),
        "skills": _default_skill_descriptions(),
    }
    if extraction.constraints:
        data["constraints"] = _stage_mapping_for_yaml(extraction.constraints)
    if extraction.validation_commands:
        data["validation_commands"] = _stage_mapping_for_yaml(
            extraction.validation_commands
        )
    return yaml.safe_dump(data, sort_keys=False, allow_unicode=False)


def render_missing_decisions(missing_decisions: Sequence[MissingDecision]) -> str:
    """Render review-only source material that was not promoted into YAML."""
    lines = [
        "# Missing Decisions",
        "",
        "This draft keeps uncertain material out of `profile.draft.yaml`.",
        "Review these items before promoting the draft into tracked profile source.",
        "",
    ]
    if not missing_decisions:
        lines.extend(["## Items Requiring Review", "", "- None detected in this pass.", ""])
        return "\n".join(lines)

    lines.extend(["## Items Requiring Review", ""])
    for item in missing_decisions:
        lines.append(
            f"- `{item.source}:{item.line}` [{item.reason}] {item.text}"
        )
    lines.append("")
    return "\n".join(lines)


def render_agent_review(
    *,
    profile_id: str,
    bundle_name: str,
    org_name: str,
    collection: SourceCollection,
    extraction: DraftExtraction,
    self_check: str,
) -> str:
    """Render the review report for the local draft package."""
    constraints_count = sum(len(items) for items in extraction.constraints.values())
    command_count = sum(len(items) for items in extraction.validation_commands.values())
    lines = [
        "# Agent Review",
        "",
        "This package is reviewable candidate output. `profile.draft.yaml` is not durable source until it is reviewed and moved into the owning profile path.",
        "",
        "## Draft",
        "",
        f"- Profile id: `{profile_id}`",
        f"- Bundle name: `{bundle_name}`",
        f"- Org name: `{org_name}`",
        f"- Self-check: {self_check}",
        "",
        "## Source Files",
        "",
    ]
    for source in collection.files:
        lines.append(f"- `{source.display_path}`")
    lines.extend(["", "## Skipped Paths", ""])
    if collection.skipped_paths:
        for skipped in collection.skipped_paths:
            lines.append(f"- `{skipped}`")
    else:
        lines.append("- None")
    lines.extend(
        [
            "",
            "## Extraction Summary",
            "",
            f"- Constraints placed in YAML: {constraints_count}",
            f"- Validation commands placed in YAML: {command_count}",
            f"- Missing decisions for review: {len(extraction.missing_decisions)}",
            "",
            "## Next Review",
            "",
            "- Confirm stage placement before promotion.",
            "- Move the reviewed profile into a tracked profile directory only after approval.",
            "",
        ]
    )
    return "\n".join(lines)


def _walk_supported_files(root: Path, skipped: List[str]) -> Iterable[Path]:
    for path in sorted(root.rglob("*")):
        if path == root:
            continue
        rel_parts = path.relative_to(root).parts
        if _is_skipped_path(rel_parts):
            if path.is_file():
                skipped.append(path.as_posix())
            continue
        if path.is_dir():
            continue
        if path.suffix.lower() in SUPPORTED_SOURCE_SUFFIXES:
            yield path
        else:
            skipped.append(path.as_posix())


def _is_skipped_path(parts: Sequence[str]) -> bool:
    if any(part in SKIPPED_DIRECTORY_NAMES for part in parts):
        return True
    for index, part in enumerate(parts[:-1]):
        if part == "examples" and parts[index + 1] == "generated":
            return True
    return False


def _append_source_file(files: List[SourceFile], seen: set[Path], path: Path) -> None:
    resolved = path.resolve()
    if resolved in seen:
        return
    seen.add(resolved)
    try:
        text = resolved.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"source must be UTF-8 text: {path}") from exc
    files.append(
        SourceFile(
            path=resolved,
            display_path=resolved.as_posix(),
            text=text,
        )
    )


def _prepare_output_dir(output_dir: Path, *, replace: bool) -> None:
    if output_dir.exists() and not output_dir.is_dir():
        raise ValueError(f"output path exists and is not a directory: {output_dir}")
    if output_dir.exists():
        if not replace:
            raise ValueError("output directory already exists; pass --replace to overwrite")
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True)


def _validate_kebab(value: str, field_name: str) -> str:
    value = value.strip()
    if not KEBAB_RE.fullmatch(value):
        raise ValueError(f"{field_name} must be lower kebab-case")
    return value


def _self_check_profile(profile_file: Path) -> str:
    try:
        load_profile(profile_file)
    except ValueError as exc:
        raise ValueError(f"profile.draft.yaml failed load_profile self-check: {exc}") from exc
    return "passed load_profile()"


def _candidate_text(line: str) -> str:
    line = BULLET_RE.sub("", line).strip()
    if not line:
        return ""
    return re.sub(r"\s+", " ", line)


def _looks_like_validation(text: str) -> bool:
    lowered = text.lower()
    return (
        ("`" in text and any(word in lowered for word in ("validate", "test", "run", "check", "verify")))
        or lowered.startswith(("validate:", "validation:", "test:", "check:"))
    )


def _extract_commands(text: str) -> tuple[str, ...]:
    commands = [
        command.strip()
        for command in CODE_SPAN_RE.findall(text)
        if _looks_like_command(command)
    ]
    if commands:
        return tuple(commands)
    if ":" in text:
        tail = text.split(":", 1)[1].strip()
        if _looks_like_command(tail):
            return (tail,)
    return ()


def _looks_like_command(text: str) -> bool:
    lowered = text.lower()
    if not text or len(text.split()) < 2:
        return False
    starters = (
        "python ",
        "python3 ",
        "pytest",
        "uv ",
        "go ",
        "npm ",
        "pnpm ",
        "yarn ",
        "cargo ",
        "forma ",
        "git diff",
        "mypy",
        "ruff",
    )
    return lowered.startswith(starters)


def _looks_like_rule(text: str) -> bool:
    lowered = text.lower()
    return any(
        phrase in lowered
        for phrase in (
            "must ",
            "must not ",
            "do not ",
            "don't ",
            "never ",
            "always ",
            "before ",
            "after ",
            "preserve ",
            "record ",
            "require ",
            "validate ",
            "stop ",
            "keep ",
        )
    )


def _missing_decision_reason(text: str, heading: str) -> str:
    combined = f"{heading} {text}".lower()
    if any(marker in combined for marker in ("/users/", "/private/", "/var/", "credential", "secret", "token")):
        return "private-or-local"
    if any(marker in combined for marker in ("adapter", "source adapter", "connector")):
        return "adapter-like"
    if any(marker in combined for marker in ("generated baseline", "examples/generated", "dist/", "release artifact")):
        return "generated-baseline-or-release"
    if any(marker in combined for marker in ("current issue", "current task", "this issue", "one-off", "temporary injection")):
        return "one-off-or-task-specific"
    if any(marker in combined for marker in ("conditional overlay", "route-specific", "impact profile")):
        return "route-specific"
    if "read first" in combined or "read these files first" in combined:
        return "broad-reading"
    return ""


def _stage_for_text(text: str, heading: str) -> str:
    combined = f"{heading} {text}".lower()
    stage_keywords = (
        ("flow", ("showhand", "continue remaining", "autopilot")),
        ("pour", ("implement", "execute", "validate", "validation", "proof", "runs/", "preserve unrelated")),
        ("seal", ("plan.md", "tasks.md", "lock", "task contract")),
        ("gauge", ("ground", "inspect", "evidence", "read code", "read docs")),
        ("shape", ("plan", "clarify", "scope", "acceptance", "before implementation")),
    )
    for stage, keywords in stage_keywords:
        if any(keyword in combined for keyword in keywords):
            return stage
    if any(keyword in combined for keyword in ("preserve unrelated", "do not revert")):
        return "default"
    return "shape"


def _shorten(text: str, limit: int = 180) -> str:
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1].rstrip() + "..."


def _append_unique(values: List[str], value: str) -> None:
    if value and value not in values:
        values.append(value)


def _stage_mapping_for_yaml(mapping: Mapping[str, Sequence[str]]) -> dict[str, list[str]]:
    return {stage: list(mapping[stage]) for stage in STAGE_KEYS if stage in mapping}


def _default_stage_config() -> dict[str, dict[str, str]]:
    return {
        "shape": {
            "name": "forma-plan",
            "directory": "forma-plan",
            "display_name": "Forma Plan",
            "short_description": "Clarify goals, constraints, boundaries, and acceptance criteria.",
            "default_prompt": "Use $forma-plan to clarify goals, constraints, boundaries, and acceptance criteria before implementation.",
        },
        "gauge": {
            "name": "forma-ground",
            "directory": "forma-ground",
            "display_name": "Forma Ground",
            "short_description": "Inspect code, docs, issues, and evidence before deciding.",
            "default_prompt": "Use $forma-ground to inspect code, docs, issues, and evidence before deciding.",
        },
        "seal": {
            "name": "forma-lock",
            "directory": "forma-lock",
            "display_name": "Forma Lock",
            "short_description": "Lock the execution plan and task contract.",
            "default_prompt": "Use $forma-lock to lock the execution plan and task contract.",
        },
        "pour": {
            "name": "forma-execute",
            "directory": "forma-execute",
            "display_name": "Forma Execute",
            "short_description": "Execute one accepted task and leave verifiable evidence.",
            "default_prompt": "Use $forma-execute to execute one accepted task and leave verifiable evidence.",
        },
        "flow": {
            "name": "forma-showhand",
            "directory": "forma-showhand",
            "display_name": "Forma Showhand",
            "short_description": "Continue remaining tasks, but stop when evidence is insufficient.",
            "default_prompt": "Use $forma-showhand to continue remaining tasks, but stop when evidence is insufficient.",
        },
    }


def _default_skill_descriptions() -> dict[str, dict[str, str]]:
    return {
        "shape": {
            "description": "Clarify goals, constraints, boundaries, and acceptance criteria.",
        },
        "gauge": {
            "description": "Inspect code, docs, issues, and evidence before deciding.",
        },
        "seal": {"description": "Lock the execution plan and task contract."},
        "pour": {
            "description": "Execute one accepted task and leave verifiable evidence.",
        },
        "flow": {
            "description": "Continue remaining tasks, but stop when evidence is insufficient.",
        },
    }
