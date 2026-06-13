"""Read-only repository operability diagnosis for agent handoff."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from forma.reports import ActionableReport, NextAction, ReportSection

REPO_DOCTOR_STATUSES = ("ready", "needs-agent", "needs-human", "unsafe")


@dataclass(frozen=True)
class RepoFinding:
    id: str
    status: str
    summary: str
    evidence: tuple[str, ...]
    impact: str
    next_action: str | None = None

    def to_dict(self) -> dict[str, object]:
        data: dict[str, object] = {
            "id": self.id,
            "status": self.status,
            "summary": self.summary,
            "evidence": list(self.evidence),
            "impact": self.impact,
        }
        if self.next_action is not None:
            data["next_action"] = self.next_action
        return data


def diagnose_repo(path: Path) -> ActionableReport:
    root = path.resolve()
    if not root.exists():
        return _unsafe_report(root, "repository path does not exist")
    if not root.is_dir():
        return _unsafe_report(root, "repository path is not a directory")

    findings = (
        _agent_entry_finding(root),
        _source_boundary_finding(root),
        _validation_finding(root),
        _profile_finding(root),
        _instruction_weight_finding(root),
    )
    status = _status(findings)
    blockers = tuple(
        finding.summary for finding in findings if finding.status == "unsafe"
    )
    warnings = tuple(
        finding.summary
        for finding in findings
        if finding.status in {"needs-agent", "needs-human"}
    )
    return ActionableReport(
        command="forma doctor repo",
        subject=str(root),
        status=status,
        summary=_summary(status),
        sections=(
            ReportSection(
                kind="diagnostic-findings",
                title="Findings",
                payload={"items": [finding.to_dict() for finding in findings]},
            ),
        ),
        next_actions=_next_actions(findings),
        blockers=blockers,
        warnings=warnings,
    )


def _unsafe_report(root: Path, message: str) -> ActionableReport:
    return ActionableReport(
        command="forma doctor repo",
        subject=str(root),
        status="unsafe",
        summary="repo diagnosis could not run",
        blockers=(message,),
        next_actions=(
            NextAction(
                title="provide a repository directory",
                description="Run `forma doctor repo <repo-path>` with an existing directory.",
            ),
        ),
    )


def _agent_entry_finding(root: Path) -> RepoFinding:
    evidence = _existing(root, ("AGENTS.md", "CLAUDE.md", ".agents", ".codex"))
    if evidence:
        return RepoFinding(
            id="agent-entry",
            status="ready",
            summary="agent entrypoint is present",
            evidence=evidence,
            impact="Agents have an explicit starting point for repository rules.",
        )
    return RepoFinding(
        id="agent-entry",
        status="needs-human",
        summary="no obvious agent entrypoint found",
        evidence=(),
        impact="Agents may need to infer repository rules from scattered files.",
        next_action="Add or point agents to a concise AGENTS.md or equivalent entrypoint.",
    )


def _source_boundary_finding(root: Path) -> RepoFinding:
    evidence = _existing(root, ("STRUCTURE.md", "docs/AGENTS.md", "docs/INDEX.md"))
    if evidence:
        return RepoFinding(
            id="source-boundaries",
            status="ready",
            summary="source boundary documentation is present",
            evidence=evidence,
            impact="Agents can distinguish source, generated output, docs, and evidence.",
        )
    return RepoFinding(
        id="source-boundaries",
        status="needs-agent",
        summary="source boundary documentation is not obvious",
        evidence=(),
        impact="Agents may confuse generated artifacts, source inputs, and evidence.",
        next_action="Identify source/generated/evidence boundaries before broad edits.",
    )


def _validation_finding(root: Path) -> RepoFinding:
    evidence = _existing(
        root,
        (
            "pyproject.toml",
            "package.json",
            "Makefile",
            "justfile",
            "go.mod",
            "Cargo.toml",
        ),
    )
    if evidence:
        return RepoFinding(
            id="validation",
            status="ready",
            summary="validation entrypoint signals are present",
            evidence=evidence,
            impact="Agents can usually derive task-local validation commands.",
        )
    return RepoFinding(
        id="validation",
        status="needs-human",
        summary="no common validation entrypoint found",
        evidence=(),
        impact="Agents need a human-provided test or validation command.",
        next_action="Document at least one local validation command.",
    )


def _profile_finding(root: Path) -> RepoFinding:
    evidence = _existing(
        root,
        (
            ".forma/profile.yaml",
            ".forma-profile/profile/profile.yaml",
            ".forma-profile/profile.yaml",
            "profiles",
        ),
    )
    if evidence:
        return RepoFinding(
            id="forma-profile",
            status="ready",
            summary="Forma profile source is present",
            evidence=evidence,
            impact="Forma can anchor workflow generation in tracked project source.",
        )
    return RepoFinding(
        id="forma-profile",
        status="needs-agent",
        summary="no Forma profile found",
        evidence=(),
        impact="Agents may need to bootstrap deterministic Forma source before reuse.",
        next_action="Use `forma init` planning before creating profile source.",
    )


def _instruction_weight_finding(root: Path) -> RepoFinding:
    instruction_files = [root / name for name in ("AGENTS.md", "CLAUDE.md")]
    heavy = [
        path.relative_to(root).as_posix()
        for path in instruction_files
        if path.is_file() and _line_count(path) > 220
    ]
    if heavy:
        return RepoFinding(
            id="instruction-weight",
            status="needs-agent",
            summary="agent instructions may be too heavy for default reads",
            evidence=tuple(heavy),
            impact="Agents may miss task-specific rules or over-read unrelated policy.",
            next_action="Move detailed references behind conditional docs or profile references.",
        )
    evidence = tuple(
        path.relative_to(root).as_posix()
        for path in instruction_files
        if path.is_file()
    )
    return RepoFinding(
        id="instruction-weight",
        status="ready",
        summary="agent instructions are not obviously oversized",
        evidence=evidence,
        impact="Default agent reads should stay manageable.",
    )


def _next_actions(findings: tuple[RepoFinding, ...]) -> tuple[NextAction, ...]:
    actions = []
    for finding in findings:
        if finding.next_action is not None:
            actions.append(
                NextAction(
                    title=finding.summary,
                    description=finding.next_action,
                )
            )
    return tuple(actions)


def _status(findings: tuple[RepoFinding, ...]) -> str:
    statuses = {finding.status for finding in findings}
    if "unsafe" in statuses:
        return "unsafe"
    if "needs-human" in statuses:
        return "needs-human"
    if "needs-agent" in statuses:
        return "needs-agent"
    return "ready"


def _summary(status: str) -> str:
    if status == "ready":
        return "repo is ready for agent operation"
    if status == "needs-agent":
        return "repo can proceed after agent-side preparation"
    if status == "needs-human":
        return "repo needs human decisions before reliable agent operation"
    return "repo is unsafe for automated agent operation"


def _existing(root: Path, rel_paths: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(rel for rel in rel_paths if (root / rel).exists())


def _line_count(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except OSError:
        return 0
