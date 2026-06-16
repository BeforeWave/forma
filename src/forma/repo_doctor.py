"""Read-only repository operability diagnosis for agent handoff."""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from forma.reports import HandoffAction, INTERACTION_CHOICE, NextAction, ReportFormat
from forma.routes import (
    HANDOFF_KIND_AGENT_OPERABILITY,
    HANDOFF_KIND_PROFILE_REFINEMENT,
    HANDOFF_TITLE_AGENT_OPERABILITY,
    HANDOFF_TITLE_PROFILE_REFINEMENT,
)

REPO_DOCTOR_SCHEMA = "forma.repo-doctor.report.v1"
REPO_DOCTOR_STATUSES = ("ready", "needs-agent", "needs-human", "unsafe")
CORE_DOMAINS = (
    "entrypoint",
    "task-state",
    "source-boundaries",
    "validation",
    "human-gates",
    "noise-control",
    "instruction-quality",
    "instruction-polarity",
    "tooling-signals",
)
CORE_CONTRACT_DOMAINS = (
    "entrypoint",
    "task-state",
    "source-boundaries",
    "validation",
    "human-gates",
    "noise-control",
    "instruction-quality",
    "instruction-polarity",
)
TOOLING_SIGNAL_FILES = (
    "pyproject.toml",
    "package.json",
    "Makefile",
    "justfile",
    "go.mod",
    "Cargo.toml",
    ".github/workflows",
)
ENTRYPOINT_FILES = (
    "AGENTS.md",
    "CLAUDE.md",
    ".github/copilot-instructions.md",
    ".cursor/rules",
    ".openhands/microagents",
)
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
AT_REFERENCE_RE = re.compile(r"(?<![\w/.-])@([A-Za-z0-9_./~+-][^\s`<>()\[\]{}'\",;:]*)")
INSTRUCTION_REFERENCE_SUFFIXES = {".md", ".markdown", ".mdc"}
MAX_ENTRYPOINT_REFERENCES = 128
ENTRYPOINT_REFERENCE_WARNING_LIMIT = 24
MAX_AGENT_INSTRUCTION_LINES = 200
MAX_CODEX_PROJECT_DOC_BYTES = 32 * 1024
MAX_LOCAL_ENTRYPOINTS = 64
LOCAL_ENTRYPOINT_NAMES = {"agents.md", "claude.md"}
ENTRYPOINT_SCAN_SKIP_DIRS = {
    ".git",
    ".forma",
    ".forma-profile",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "generated",
    "node_modules",
    "vendor",
}
MARKDOWN_COVERAGE_SKIP_DIRS = {
    ".git",
    ".forma",
    ".forma-profile",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "generated",
    "node_modules",
    "plans",
    "source",
    "vendor",
}
RULE_MARKDOWN_HINT_TERMS = (
    "agent",
    "approval",
    "avoid",
    "boundary",
    "constraint",
    "credential",
    "do not",
    "don't",
    "generated",
    "handoff",
    "human approval",
    "must",
    "never",
    "publish",
    "release",
    "rule",
    "security",
    "setup",
    "should",
    "source",
    "task contract",
    "test",
    "validation",
    "workflow",
    "不要",
    "不能",
    "不得",
    "规则",
    "规范",
    "验证",
)
MAINTENANCE_SEMANTIC_PROMPTS = (
    "repository purpose and primary deliverables",
    "runtime, artifact, or publishing model",
    "source-of-truth, generated-output, release, and local-state boundaries",
    "validation model for ordinary changes and high-risk changes",
    "compatibility, migration, data, security, privacy, or contract risks that fit this repo",
    "review, evidence, handoff, and owner-decision model",
)
NEGATIVE_RULE_RE = re.compile(
    r"\b(?:do not|don't|must not|should not|avoid|never)\b|stop instead|不要|不能|不得|不应|禁止",
    re.IGNORECASE,
)
HARD_RISK_RULE_TERMS = (
    "approval",
    "approve",
    "ask",
    "boundary",
    "checkout",
    "commit",
    "credential",
    "delete",
    "destructive",
    "dist",
    "evidence",
    "external-write",
    "generated",
    "git add",
    "git rm",
    "human",
    "irreversible",
    "key",
    "owner",
    "password",
    "permission",
    "private",
    "publish",
    "release",
    "remove",
    "reset",
    "rm ",
    "secret",
    "security",
    "source",
    "stage",
    "token",
    "安全",
    "审批",
    "发布",
    "凭证",
    "密钥",
    "删除",
    "确认",
)
POSITIVE_CONTRACT_TERMS = (
    "ask",
    "confirm",
    "execute",
    "generate",
    "include",
    "keep",
    "prefer",
    "record",
    "report",
    "resolve",
    "return",
    "run",
    "select",
    "source",
    "treat",
    "use",
    "verify",
    "write",
    "使用",
    "运行",
    "记录",
    "保持",
    "确认",
    "报告",
    "写入",
    "验证",
)

FindingStatus = Literal["contract", "signal", "missing", "warning", "optional"]


@dataclass(frozen=True)
class RepoFinding:
    domain: str
    status: FindingStatus
    summary: str
    evidence: tuple[str, ...]
    confidence: str
    handoff: str | None = None

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "domain": self.domain,
            "status": self.status,
            "summary": self.summary,
            "evidence": list(self.evidence),
            "confidence": self.confidence,
        }
        if self.handoff is not None:
            data["handoff"] = self.handoff
        return data


@dataclass(frozen=True)
class RepoDoctorReport:
    subject: str
    status: str
    summary: str
    facts: dict[str, Any]
    findings: tuple[RepoFinding, ...]
    evidence: dict[str, list[str]]
    confidence: str
    programmatic_actions: tuple[dict[str, Any], ...] = ()
    agent_handoffs: tuple[HandoffAction, ...] = ()
    human_decisions: tuple[dict[str, Any], ...] = ()
    unsafe_blockers: tuple[str, ...] = ()
    command: str = "forma doctor"
    schema: str = REPO_DOCTOR_SCHEMA

    @property
    def terminal(self) -> bool:
        return self.status in {"ready", "unsafe"} and not self.agent_handoffs

    @property
    def terminal_reason(self) -> str:
        if self.agent_handoffs:
            return "primary_handoff_required"
        if self.status == "unsafe":
            return "unsafe_blocker"
        if self.status == "needs-human":
            return "owner_decision_required"
        if self.status == "needs-agent":
            return "agent_disposition_required"
        return "no_required_action"

    @property
    def next_required_action(self) -> str:
        if self.agent_handoffs:
            return self.agent_handoffs[0].handoff_kind
        if self.status == "unsafe":
            return "stop_for_unsafe_blocker"
        if self.status == "needs-human":
            return "owner_decision"
        if self.status == "needs-agent":
            return "agent_disposition"
        return "none"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": self.schema,
            "command": self.command,
            "subject": self.subject,
            "status": self.status,
            "summary": self.summary,
            "terminal": self.terminal,
            "terminal_reason": self.terminal_reason,
            "next_required_action": self.next_required_action,
            "facts": self.facts,
            "findings": [finding.to_dict() for finding in self.findings],
            "evidence": self.evidence,
            "confidence": self.confidence,
            "programmatic_actions": list(self.programmatic_actions),
            "agent_handoffs": [handoff.to_dict() for handoff in self.agent_handoffs],
            "human_decisions": list(self.human_decisions),
            "unsafe_blockers": list(self.unsafe_blockers),
        }

    def render(self, output_format: ReportFormat) -> str:
        if output_format == "json":
            return json.dumps(self.to_dict(), indent=2, sort_keys=True)
        if output_format == "agent":
            return _render_agent(self)
        if output_format == "human":
            return _render_human(self)
        raise ValueError(f"unsupported report format: {output_format}")


def diagnose_repo(path: Path) -> RepoDoctorReport:
    root = path.resolve()
    if not root.exists():
        return _unsafe_report(root, "repository path does not exist")
    if not root.is_dir():
        return _unsafe_report(root, "repository path is not a directory")

    facts = _collect_facts(root)
    findings = tuple(
        finding
        for finding in (
            _entrypoint_finding(root, facts),
            _task_state_finding(facts),
            _source_boundaries_finding(root, facts),
            _validation_finding(root, facts),
            _human_gates_finding(root, facts),
            _noise_control_finding(root, facts),
            _instruction_quality_finding(facts),
            _instruction_polarity_finding(facts),
            _entrypoint_reference_quality_finding(facts),
            _markdown_rule_coverage_finding(facts),
            _tooling_signals_finding(facts),
            _forma_integration_finding(facts),
        )
        if finding is not None
    )
    unsafe_blockers: tuple[str, ...] = ()
    status = _status(findings, unsafe_blockers)
    return RepoDoctorReport(
        subject=str(root),
        status=status,
        summary=_summary(status),
        facts=facts,
        findings=findings,
        evidence={finding.domain: list(finding.evidence) for finding in findings},
        confidence=_confidence(findings),
        programmatic_actions=_programmatic_actions(facts),
        agent_handoffs=_agent_handoffs(findings, facts),
        human_decisions=_human_decisions(findings),
        unsafe_blockers=unsafe_blockers,
    )


def _unsafe_report(root: Path, message: str) -> RepoDoctorReport:
    return RepoDoctorReport(
        subject=str(root),
        status="unsafe",
        summary="repo diagnosis could not run",
        facts={},
        findings=(),
        evidence={},
        confidence="high",
        unsafe_blockers=(message,),
        agent_handoffs=(
            HandoffAction(
                title="provide repository directory",
                handoff_kind=HANDOFF_KIND_AGENT_OPERABILITY,
                questions=("Run `forma doctor <repo-path>` with an existing directory.",),
                return_shape={"path": "existing repository path"},
            ),
        ),
    )


def _collect_facts(root: Path) -> dict[str, Any]:
    root_entrypoints = _existing_entrypoints(root, ENTRYPOINT_FILES)
    local_entrypoints = _local_entrypoints(root, root_entrypoints)
    entrypoints = tuple(_dedupe([*root_entrypoints, *local_entrypoints]))
    entrypoint_references, entrypoint_reference_cycles = _entrypoint_reference_docs(root, entrypoints)
    entrypoint_reference_quality = _entrypoint_reference_quality(
        entrypoints,
        entrypoint_references,
        entrypoint_reference_cycles,
    )
    tooling = _existing(root, TOOLING_SIGNAL_FILES)
    validation_sources = _validation_evidence(
        root,
        tuple(_dedupe([*entrypoints, *entrypoint_references])),
    )
    task_state = _existing(root, ("plans", "tasks", "docs/adr", "docs/ADR"))
    generated_candidates = _existing(root, ("dist", "build", "generated", "examples/generated"))
    forma_paths = _existing(
        root,
        (
            ".forma/profile.yaml",
            ".forma/.gitignore",
            ".forma/reinstall-workflow.sh",
            ".forma-profile/profile.yaml",
            ".forma-profile/profile/profile.yaml",
            "profiles",
        ),
    )
    purpose_sources = _purpose_sources(root, entrypoints, entrypoint_references, tooling)
    return {
        "entrypoints": list(entrypoints),
        "root_entrypoints": list(root_entrypoints),
        "local_entrypoints": list(local_entrypoints),
        "entrypoint_references": list(entrypoint_references),
        "entrypoint_reference_cycles": list(entrypoint_reference_cycles),
        "entrypoint_reference_quality": entrypoint_reference_quality,
        "agent_instruction_quality": _agent_instruction_quality(
            root,
            entrypoints,
            entrypoint_references,
            validation_sources,
        ),
        "instruction_polarity": _instruction_polarity(
            root,
            tuple(_dedupe([*entrypoints, *entrypoint_references])),
        ),
        "markdown_rule_coverage": _markdown_rule_coverage(
            root,
            entrypoints,
            entrypoint_references,
        ),
        "tooling_signals": list(tooling),
        "purpose_sources": list(purpose_sources),
        "maintenance_semantic_prompts": list(MAINTENANCE_SEMANTIC_PROMPTS),
        "validation_sources": list(validation_sources),
        "task_state_paths": list(task_state),
        "generated_candidates": list(generated_candidates),
        "forma": {
            "present": bool(forma_paths),
            "paths": list(forma_paths),
        },
        "forma_adoption": _forma_adoption(bool(forma_paths)),
    }


def _purpose_sources(
    root: Path,
    entrypoints: tuple[str, ...],
    entrypoint_references: tuple[str, ...],
    tooling: tuple[str, ...],
) -> tuple[str, ...]:
    candidates = _dedupe(
        [
            *entrypoints,
            "README.md",
            "README",
            "docs/README.md",
            "docs/INDEX.md",
            "STRUCTURE.md",
            *entrypoint_references,
            *tooling,
        ]
    )
    return tuple(item for item in candidates if (root / item).exists())


def _entrypoint_finding(root: Path, facts: dict[str, Any]) -> RepoFinding:
    evidence = tuple(facts["entrypoints"])
    if not evidence:
        return RepoFinding(
            "entrypoint",
            "missing",
            "no agent entrypoint found",
            (),
            "high",
            "Propose a concise AGENTS.md or equivalent entrypoint.",
        )
    if not facts["root_entrypoints"] and facts["local_entrypoints"]:
        return RepoFinding(
            "entrypoint",
            "signal",
            "path-scoped agent entrypoints exist but no repo-level entrypoint was found",
            tuple(facts["local_entrypoints"]),
            "high",
            "Add a concise root AGENTS.md or equivalent repo-level entrypoint that points agents to the path-scoped rules.",
        )
    contract_evidence = tuple(_dedupe([*evidence, *facts["entrypoint_references"]]))
    if _any_file_contains(
        root,
        contract_evidence,
        (
            "read first",
            "must read",
            "before performing",
            "execution prerequisites",
            "source boundaries",
            "validation",
            "handoff",
            "do not",
            "human",
        ),
    ):
        return RepoFinding(
            "entrypoint",
            "contract",
            "agent entrypoint contains operational instructions",
            contract_evidence,
            "medium",
        )
    return RepoFinding(
        "entrypoint",
        "signal",
        "agent entrypoint exists but does not obviously carry an operating contract",
        evidence,
        "medium",
        "Review the entrypoint for read-first, scope, validation, stop, and handoff rules.",
    )


def _task_state_finding(facts: dict[str, Any]) -> RepoFinding:
    evidence = tuple(facts["task_state_paths"])
    if "plans" in evidence:
        return RepoFinding(
            "task-state",
            "contract",
            "task planning or evidence directory is present",
            evidence,
            "high",
        )
    if evidence:
        return RepoFinding(
            "task-state",
            "signal",
            "task state signal is present but the agent evidence contract is unclear",
            evidence,
            "medium",
            "Identify where plans, run logs, review notes, and handoff evidence belong.",
        )
    return RepoFinding(
        "task-state",
        "missing",
        "no task state or evidence location found",
        (),
        "high",
        "Propose where task plans, evidence, and review notes should live.",
    )


def _source_boundaries_finding(root: Path, facts: dict[str, Any]) -> RepoFinding:
    evidence = tuple(
        _dedupe(
            [
                item
                for item in (
                    "AGENTS.md",
                    "STRUCTURE.md",
                    "docs/AGENTS.md",
                    "docs/INDEX.md",
                    *facts["entrypoint_references"],
                )
                if (root / item).exists()
            ]
        )
    )
    if evidence and _any_file_contains(
        root,
        evidence,
        ("source", "generated", "writable", "boundaries", "do not", "dist", "examples"),
    ):
        return RepoFinding(
            "source-boundaries",
            "contract",
            "source, generated, or writable boundary guidance is present",
            evidence,
            "medium",
        )
    if evidence:
        return RepoFinding(
            "source-boundaries",
            "signal",
            "boundary documentation exists but source/generated/write rules are unclear",
            evidence,
            "medium",
            "Review whether source, generated output, docs, examples, vendored code, and local state are separated.",
        )
    return RepoFinding(
        "source-boundaries",
        "missing",
        "no source boundary documentation found",
        (),
        "high",
        "Map source, generated output, docs, examples, vendored code, and local state.",
    )


def _validation_finding(root: Path, facts: dict[str, Any]) -> RepoFinding:
    evidence = tuple(facts["validation_sources"])
    if evidence:
        return RepoFinding(
            "validation",
            "contract",
            "explicit validation command is documented",
            evidence,
            "medium",
        )
    tooling = tuple(facts["tooling_signals"])
    if tooling:
        return RepoFinding(
            "validation",
            "signal",
            "tooling files exist but no explicit validation command was found",
            tooling,
            "high",
            "Identify quick and full validation commands before implementation.",
        )
    return RepoFinding(
        "validation",
        "missing",
        "no validation command or tooling signal found",
        (),
        "high",
        "Propose the minimum reliable validation command.",
    )


def _human_gates_finding(root: Path, facts: dict[str, Any]) -> RepoFinding:
    evidence = tuple(facts["entrypoints"])
    if evidence and _any_file_contains(
        root,
        evidence,
        ("confirm", "approval", "ask", "human", "destructive", "publish", "release", "credential"),
    ):
        return RepoFinding(
            "human-gates",
            "contract",
            "human confirmation gates are documented",
            evidence,
            "medium",
        )
    if evidence:
        return RepoFinding(
            "human-gates",
            "signal",
            "agent entrypoint exists but human confirmation gates are unclear",
            evidence,
            "medium",
            "Review destructive, publish, release, credential, external-write, and durable-rule-adoption gates.",
        )
    return RepoFinding(
        "human-gates",
        "missing",
        "no human confirmation guidance found",
        (),
        "high",
        "Propose operations that must stop for owner confirmation.",
    )


def _noise_control_finding(root: Path, facts: dict[str, Any]) -> RepoFinding:
    generated = tuple(facts["generated_candidates"])
    boundary_files = tuple(
        rel for rel in ("AGENTS.md", "STRUCTURE.md", ".gitignore") if (root / rel).exists()
    )
    if boundary_files and _any_file_contains(
        root,
        boundary_files,
        ("generated", "deprecated", "ignore", "dist", "local state", "cache"),
    ):
        return RepoFinding(
            "noise-control",
            "contract",
            "noise or generated-output boundary is documented",
            boundary_files,
            "medium",
        )
    if generated:
        return RepoFinding(
            "noise-control",
            "warning",
            "generated-looking directories are present without an obvious noise boundary",
            generated,
            "medium",
            "Review generated artifacts, stale docs, local state, and large outputs before broad reads.",
        )
    return RepoFinding(
        "noise-control",
        "signal",
        "no generated-output noise signal found",
        (),
        "low",
        "Confirm whether there are generated, deprecated, vendored, or local-state paths to ignore.",
    )


def _instruction_quality_finding(facts: dict[str, Any]) -> RepoFinding:
    evidence = tuple(facts["entrypoints"])
    quality = facts["agent_instruction_quality"]
    if not evidence:
        return RepoFinding(
            "instruction-quality",
            "missing",
            "instruction quality cannot be assessed without an entrypoint",
            (),
            "high",
        )
    if quality["status"] == "warning":
        issues = tuple(str(issue) for issue in quality["issues"])
        summary = "; ".join(issues) if issues else "agent instruction quality needs review"
        return RepoFinding(
            "instruction-quality",
            "warning",
            summary,
            evidence,
            "high",
            "Review instruction quality using the provider-informed criteria in facts.agent_instruction_quality.",
        )
    return RepoFinding(
        "instruction-quality",
        "contract",
        "agent instructions are concise, structured, and route to actionable guidance",
        evidence,
        "high",
    )


def _instruction_polarity_finding(facts: dict[str, Any]) -> RepoFinding | None:
    polarity = facts["instruction_polarity"]
    if not polarity["analyzed_docs"]:
        return None
    evidence = tuple(
        f"{item['path']}:{item['line']}" for item in polarity["sample_locations"]
    )
    if polarity["status"] == "warning":
        return RepoFinding(
            "instruction-polarity",
            "warning",
            "ordinary workflow prohibitions lack nearby positive contracts",
            evidence,
            "medium",
            "Rewrite ordinary process prohibitions as executable positive contracts; keep hard-risk prohibitions for destructive, security, release, approval, and source-boundary gates.",
        )
    return RepoFinding(
        "instruction-polarity",
        "contract",
        "ordinary workflow rules prefer positive contracts while hard-risk prohibitions remain explicit",
        evidence,
        "medium",
    )


def _tooling_signals_finding(facts: dict[str, Any]) -> RepoFinding:
    evidence = tuple(facts["tooling_signals"])
    if evidence:
        return RepoFinding(
            "tooling-signals",
            "signal",
            "tooling signals are present",
            evidence,
            "high",
            "Use these as evidence only; they do not replace explicit setup or validation contracts.",
        )
    return RepoFinding(
        "tooling-signals",
        "missing",
        "no common tooling signals found",
        (),
        "medium",
    )


def _entrypoint_reference_quality_finding(facts: dict[str, Any]) -> RepoFinding | None:
    quality = facts["entrypoint_reference_quality"]
    if not facts["entrypoints"]:
        return None
    evidence = tuple(_dedupe([*facts["entrypoints"], *facts["entrypoint_references"]]))
    if quality["status"] == "contract":
        return RepoFinding(
            "entrypoint-reference-quality",
            "contract",
            "entrypoint reference graph is bounded, local, and agent-readable",
            evidence,
            "high",
        )
    issues = tuple(str(issue) for issue in quality["issues"])
    summary = "; ".join(issues) if issues else "entrypoint Markdown reference quality needs review"
    return RepoFinding(
        "entrypoint-reference-quality",
        "warning",
        summary,
        evidence,
        "high",
        "Review read-first reference quality using the criteria in facts.entrypoint_reference_quality.",
    )


def _markdown_rule_coverage_finding(facts: dict[str, Any]) -> RepoFinding | None:
    coverage = facts["markdown_rule_coverage"]
    if not coverage["analyzed_markdown_count"]:
        return None
    evidence = tuple(item["path"] for item in coverage["sample_locations"])
    if coverage["status"] == "warning":
        return RepoFinding(
            "markdown-rule-coverage",
            "warning",
            "rule-like Markdown is not reachable from the agent read-first graph",
            evidence,
            "medium",
            "Review unreferenced rule-like Markdown with the owner; link valuable norms from AGENTS.md or a routed read-first index, and mark stale or informational docs as intentionally unreferenced.",
        )
    return RepoFinding(
        "markdown-rule-coverage",
        "contract",
        "rule-like Markdown is reachable from the agent read-first graph or intentionally absent",
        evidence,
        "medium",
    )


def _entrypoint_reference_quality(
    entrypoints: tuple[str, ...],
    references: tuple[str, ...],
    cycles: tuple[dict[str, list[str]], ...],
) -> dict[str, Any]:
    criteria = [
        "reported references must be existing local agent-readable instruction files",
        "reported references must stay inside the repository",
        "code and unsupported file links must not enter read-first evidence",
        "recursive instruction-reference traversal must stop when a cycle is detected",
        f"read-first reference lists should stay at or below {ENTRYPOINT_REFERENCE_WARNING_LIMIT} instruction files",
    ]
    issues: list[str] = []
    if cycles:
        issues.append("cycle(s) detected; repeated Markdown edges were skipped")
    if len(references) >= MAX_ENTRYPOINT_REFERENCES:
        issues.append("reference traversal hit the safety cap")
    elif len(references) > ENTRYPOINT_REFERENCE_WARNING_LIMIT:
        issues.append("read-first reference list is broad and may be hard for an agent to scan")
    status = "warning" if issues else "contract"
    return {
        "status": status,
        "criteria": criteria,
        "issues": issues,
        "entrypoint_count": len(entrypoints),
        "reference_count": len(references),
    }


def _agent_instruction_quality(
    root: Path,
    entrypoints: tuple[str, ...],
    references: tuple[str, ...],
    validation_sources: tuple[str, ...],
) -> dict[str, Any]:
    criteria = [
        "agent-facing instructions should make repo layout, run/test/lint commands, constraints, and done/verification expectations discoverable",
        "instructions should be concise, specific, and structured; default entrypoint files should stay near the Claude Code 200-line guidance and within the Codex project-doc budget",
        "concrete validation commands should be discoverable from entrypoints or routed Markdown",
        "large or topic-specific guidance should be routed through Markdown references, path-scoped rules, or skills instead of one long default read",
        "hard gates should identify owner-approval operations; enforcement belongs in hooks, settings, or permissions where the agent surface supports it",
        "provider discovery should be explicit when multiple agents are expected: Codex reads AGENTS.md, Claude Code reads CLAUDE.md or an import/link to shared rules",
    ]
    basis = [
        "OpenAI Codex AGENTS.md guidance",
        "OpenAI Codex prompting and reliability guidance",
        "Anthropic Claude Code memory guidance",
        "Anthropic Claude Code best-practices guidance",
    ]
    issues: list[str] = []
    entrypoint_lines: dict[str, int] = {}
    entrypoint_bytes: dict[str, int] = {}
    for rel in entrypoints:
        path = root / rel
        text = _read_text(path)
        entrypoint_lines[rel] = len(text.splitlines())
        entrypoint_bytes[rel] = len(text.encode("utf-8"))
        if entrypoint_lines[rel] > MAX_AGENT_INSTRUCTION_LINES:
            issues.append(f"{rel} exceeds {MAX_AGENT_INSTRUCTION_LINES} lines")
        if text and not _looks_structured_markdown(text):
            issues.append(f"{rel} is not clearly structured Markdown")
    if not entrypoints:
        issues.append("no agent instruction entrypoint found")
    if sum(entrypoint_bytes.values()) > MAX_CODEX_PROJECT_DOC_BYTES:
        issues.append("entrypoint instruction bytes exceed Codex default project-doc budget")
    if entrypoints and not validation_sources:
        issues.append("no concrete validation command found in entrypoints or referenced Markdown")
    if entrypoints and not _any_file_contains(
        root,
        tuple(_dedupe([*entrypoints, *references])),
        ("approval", "ask", "confirm", "human", "destructive", "publish", "release", "credential"),
    ):
        issues.append("owner-approval gates are not clearly documented")
    return {
        "status": "warning" if issues else "contract",
        "basis": basis,
        "criteria": criteria,
        "issues": issues,
        "entrypoint_count": len(entrypoints),
        "reference_count": len(references),
        "entrypoint_lines": entrypoint_lines,
        "entrypoint_bytes": entrypoint_bytes,
        "validation_sources": list(validation_sources),
    }


def _instruction_polarity(root: Path, rel_paths: tuple[str, ...]) -> dict[str, Any]:
    criteria = [
        "ordinary workflow rules should be phrased as positive executable contracts",
        "hard-risk prohibitions may remain explicit for destructive, security, release, approval, or source-boundary gates",
        "ordinary prohibitions should have a nearby positive contract that tells the agent what to do instead",
    ]
    analyzed_docs: list[str] = []
    matches: list[dict[str, Any]] = []
    ordinary_unpaired: list[dict[str, Any]] = []
    hard_risk_count = 0
    ordinary_count = 0

    for rel in rel_paths:
        path = root / rel
        if not path.is_file():
            continue
        text = _read_text(path)
        if not text:
            continue
        analyzed_docs.append(rel)
        lines = text.splitlines()
        for index, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or NEGATIVE_RULE_RE.search(stripped) is None:
                continue
            hard_risk = _has_any_term(stripped, HARD_RISK_RULE_TERMS)
            paired_positive_contract = _has_nearby_positive_contract(lines, index)
            category = "hard-risk" if hard_risk else "ordinary-process"
            if hard_risk:
                hard_risk_count += 1
            else:
                ordinary_count += 1
            item = {
                "path": rel,
                "line": index + 1,
                "text": _trim_text(stripped, 220),
                "category": category,
                "paired_positive_contract": paired_positive_contract,
            }
            matches.append(item)
            if not hard_risk and not paired_positive_contract:
                ordinary_unpaired.append(item)

    return {
        "status": "warning" if ordinary_unpaired else "contract",
        "criteria": criteria,
        "analyzed_docs": analyzed_docs,
        "negative_rule_count": len(matches),
        "ordinary_prohibition_count": ordinary_count,
        "hard_risk_prohibition_count": hard_risk_count,
        "unpaired_ordinary_count": len(ordinary_unpaired),
        "sample_locations": (ordinary_unpaired or matches)[:8],
    }


def _markdown_rule_coverage(
    root: Path,
    entrypoints: tuple[str, ...],
    references: tuple[str, ...],
) -> dict[str, Any]:
    criteria = [
        "agent-relevant rule Markdown should be reachable from AGENTS.md, CLAUDE.md, or a routed read-first Markdown index",
        "nested AGENTS.md and CLAUDE.md files are path-scoped entrypoints and do not need another Markdown document to reference them",
        "unreferenced rule-like Markdown should be reviewed with the owner before being linked, rewritten, archived, or left informational",
        "generated output, Forma profile source, source methodology internals, plans, vendored files, and dependency directories are outside this coverage scan",
    ]
    markdown_docs = _candidate_markdown_docs(root, entrypoints)
    implicit_roots = tuple(
        rel
        for rel in ("README.md", "README.zh-CN.md", "README", "docs/README.md")
        if rel in markdown_docs
    )
    plain_mentions = _plain_mentioned_markdown_docs(root, entrypoints, markdown_docs)
    plain_mention_references, _cycles = _entrypoint_reference_docs(root, plain_mentions)
    reachable_docs = set(
        _dedupe(
            [
                *entrypoints,
                *references,
                *implicit_roots,
                *plain_mentions,
                *plain_mention_references,
            ]
        )
    )
    unreferenced: list[dict[str, Any]] = []

    for rel in markdown_docs:
        if rel in reachable_docs:
            continue
        rule_signal = _markdown_rule_signal(root, rel)
        if rule_signal is None:
            continue
        unreferenced.append(rule_signal)

    return {
        "status": "warning" if unreferenced else "contract",
        "criteria": criteria,
        "analyzed_markdown_count": len(markdown_docs),
        "reachable_markdown_count": len(reachable_docs),
        "unreferenced_rule_markdown_count": len(unreferenced),
        "sample_locations": unreferenced[:8],
    }


def _forma_integration_finding(facts: dict[str, Any]) -> RepoFinding:
    forma = facts["forma"]
    evidence = tuple(forma["paths"])
    if evidence:
        return RepoFinding(
            "agent-specific-integrations.forma",
            "optional",
            "Forma workflow source is present for project-rule management",
            evidence,
            "high",
            "Use existing Forma workflow source by default; remove it only if the owner explicitly asks to clean Forma configuration.",
        )
    return RepoFinding(
        "agent-specific-integrations.forma",
        "optional",
        "Forma workflow source is not present; create it to manage project rules as an installable agent workflow",
        (),
        "high",
        "Tell the owner Forma can manage these engineering rules as a workflow; if they confirm, create the profile, build, verify, and install it.",
    )


def _forma_adoption(present: bool) -> dict[str, Any]:
    value = (
        "Forma turns this repository's engineering rules into a reusable agent workflow. "
        "The agent no longer needs repeated reminders about boundaries, validation, approval "
        "gates, and proof expectations in every thread; those rules become part of planning "
        "and execution, so work is less likely to drift, easier to review, and more "
        "consistently validated."
    )
    proposal = (
        "We can create that workflow now: extract and organize the project rules into a Forma "
        "profile, build and verify the workflow output, then install it for the approved target "
        "and scope."
    )
    cleanup_policy = (
        "Do not ask whether to keep `.forma`; keep it by default. Clean Forma configuration only "
        "when the owner explicitly asks to remove it."
    )
    if present:
        return {
            "status": "present",
            "recommendation": "use existing `.forma` as the project workflow source by default",
            "value": value,
            "proposal": proposal,
            "cleanup_policy": cleanup_policy,
            "owner_confirmations": [
                "confirm profile refinement from the current project rules",
                "approve the extracted or reorganized profile before workflow build",
                "approve build and verification of workflow output",
                "approve install or reinstall target and scope",
                "approve committing workflow source when the rules should be shared with future agents",
            ],
        }
    return {
        "status": "missing",
        "recommendation": "propose creating `.forma` workflow source for this repository",
        "value": value,
        "proposal": proposal,
        "cleanup_policy": cleanup_policy,
        "owner_confirmations": [
            "create `.forma` workflow source from the doctor report",
            "approve the extracted project engineering rules before workflow build",
            "approve build and verification of workflow output",
            "approve install target and scope",
            "approve committing workflow source when the rules should be shared with future agents",
        ],
    }


def _status(findings: tuple[RepoFinding, ...], unsafe_blockers: tuple[str, ...]) -> str:
    if unsafe_blockers:
        return "unsafe"
    required = {
        finding.domain: finding.status
        for finding in findings
        if finding.domain in CORE_CONTRACT_DOMAINS
    }
    if all(status == "contract" for status in required.values()):
        return "ready"
    return "needs-agent"


def _summary(status: str) -> str:
    if status == "ready":
        return "repo has core agent-operability contracts"
    if status == "needs-agent":
        return "repo needs agent-side operability review"
    if status == "needs-human":
        return "repo needs owner decisions before reliable agent operation"
    return "repo is unsafe for automated agent operation"


def _confidence(findings: tuple[RepoFinding, ...]) -> str:
    if any(finding.confidence == "low" for finding in findings):
        return "medium"
    return "high"


def _programmatic_actions(facts: dict[str, Any]) -> tuple[dict[str, Any], ...]:
    actions: list[dict[str, Any]] = []
    forma = facts["forma"]
    if not forma["present"]:
        actions.append(
            {
                "id": "create-forma-workflow-source",
                "kind": "create-files",
                "paths": [
                    ".forma/.gitignore",
                    ".forma/profile.yaml",
                    ".forma/reinstall-workflow.sh",
                ],
                "description": "Create `.forma` workflow source so reviewed project engineering rules can become an installable agent workflow.",
            }
        )
    elif ".forma/.gitignore" not in forma["paths"]:
        actions.append(
            {
                "id": "create-forma-state-ignore",
                "kind": "create-file",
                "paths": [".forma/.gitignore"],
                "description": "Keep tracked Forma source separate from ignored runtime state.",
            }
        )
    return tuple(actions)


def _agent_handoffs(
    findings: tuple[RepoFinding, ...],
    facts: dict[str, Any],
) -> tuple[HandoffAction, ...]:
    read_first = _dedupe(
        [
            rel
            for rel in (
                *facts["entrypoints"],
                "README.md",
                *facts["entrypoint_references"],
            )
            if rel
        ]
    )
    profile_read_first = _dedupe(
        [
            *read_first,
            *(
                rel
                for rel in facts["forma"]["paths"]
                if rel.endswith((".yaml", ".yml"))
            ),
        ]
    )
    review_questions = [
        finding.handoff
        for finding in findings
        if (
            finding.domain in CORE_CONTRACT_DOMAINS
            or finding.domain == "markdown-rule-coverage"
        )
        and finding.status != "contract"
        and finding.handoff
    ]
    handoffs: list[HandoffAction] = []
    if facts["forma"]["present"] and profile_read_first:
        handoffs.append(
            HandoffAction(
                title=HANDOFF_TITLE_PROFILE_REFINEMENT,
                handoff_kind=HANDOFF_KIND_PROFILE_REFINEMENT,
                read_first=tuple(profile_read_first),
                questions=(
                    "Load `forma explain profile --format agent --target <target>` and follow its existing-profile incremental review guidance.",
                    "Compare existing Forma profile source against this handoff's read_first sources.",
                    "Return the incremental profile review with the exact headings required by `forma explain profile`; do not collapse it into generic findings or suggestions.",
                    "End `Recommended Next Step` with exactly two child lines: `Recommendation: <one concrete next action>` and `Offer: Should I <perform that action> now?`.",
                    "If the host provides structured user-input, choice, or command-approval UI for the recommended action, use it; otherwise end with `Required Confirmation: <yes/no question>`.",
                    "Assign dispositions to non-contract core findings after the profile review; do not let setup or tooling findings replace it.",
                ),
                forbidden=(
                    "Do not treat doctor readiness or artifact validation as proof that profile rules cover project semantics.",
                    "Do not approve durable project rules without owner review.",
                ),
                return_shape={
                    "profile_review": "incremental review from `forma explain profile`: Covered, Missing, Stale, Redundant, and Stage Placement",
                    "proposal": "minimal Profile YAML Proposal plus Profile Review Packet for owner approval",
                    "core_findings": "disposition for every non-contract core finding",
                    "recommended_next_step": "exactly two child lines: Recommendation and Offer, where Offer is an explicit question to do the one action now",
                    "user_interaction": "use host structured confirmation for the recommended action when available; otherwise emit Required Confirmation",
                    "owner_confirmations": "owner confirmations required before durable profile adoption",
                },
                next_action=NextAction(
                    title="apply reviewed profile delta",
                    description="Apply the one approved profile change after the coverage review.",
                    requires_confirmation=True,
                    confirmation_prompt="Should I apply the reviewed profile delta now?",
                    interaction=INTERACTION_CHOICE,
                    handoff_kind=HANDOFF_KIND_PROFILE_REFINEMENT,
                ),
            )
        )
    if review_questions:
        handoffs.append(
            HandoffAction(
                title=HANDOFF_TITLE_AGENT_OPERABILITY,
                handoff_kind=HANDOFF_KIND_AGENT_OPERABILITY,
                read_first=tuple(_dedupe(read_first)),
                questions=tuple(review_questions),
                forbidden=(
                    "Do not treat tooling file presence as a validation contract.",
                    "Do not treat Forma profile presence as core repo readiness.",
                    "Do not approve durable project rules without owner review.",
                ),
                return_shape={
                    "programmatic": "deterministic file or checklist changes",
                    "semantic": "repo rule or documentation proposals for Agent review",
                    "owner_confirmations": "owner confirmations required before durable adoption",
                },
                next_action=NextAction(
                    title="resolve operability findings",
                    description="Resolve or disposition the non-contract core findings before reporting readiness.",
                    handoff_kind=HANDOFF_KIND_AGENT_OPERABILITY,
                ),
            )
        )
    return tuple(handoffs)


def _human_decisions(findings: tuple[RepoFinding, ...]) -> tuple[dict[str, Any], ...]:
    if any(finding.domain == "human-gates" and finding.status != "contract" for finding in findings):
        return (
            {
                "id": "confirm-human-gates",
                "description": "Owner should confirm which destructive, release, credential, external-write, and durable-rule-adoption actions require approval.",
            },
        )
    return ()


def _render_human(report: RepoDoctorReport) -> str:
    lines = [
        f"{report.command}: {report.summary}",
        f"status: {report.status}",
        f"subject: {report.subject}",
        "",
        "Agent guide:",
        "  Read `forma explain agent` before interpreting this report.",
        "  Use `forma explain agent --target codex|claude-code|opencode` when the consuming agent target is known.",
        "  Use `forma doctor --format agent <repo>` for the executable handoff.",
        "  Doctor readiness covers operability; profile authoring must still extract project purpose and maintenance semantics.",
        "",
        "Core findings:",
    ]
    for finding in report.findings:
        if finding.domain not in CORE_DOMAINS:
            continue
        lines.append(f"  - {finding.domain}: {finding.status} - {finding.summary}")
    diagnostics = [
        finding
        for finding in report.findings
        if finding.domain not in CORE_DOMAINS
        and not finding.domain.startswith("agent-specific-integrations.")
    ]
    if diagnostics:
        lines.append("")
        lines.append("Diagnostics:")
        for finding in diagnostics:
            lines.append(f"  - {finding.domain}: {finding.status} - {finding.summary}")
    optional = [
        finding
        for finding in report.findings
        if finding.domain.startswith("agent-specific-integrations.")
    ]
    if optional:
        lines.append("")
        lines.append("Workflow adoption:")
        for finding in optional:
            lines.append(f"  - {finding.domain}: {finding.summary}")
    forma_adoption = report.facts.get("forma_adoption")
    if isinstance(forma_adoption, dict):
        lines.append("")
        lines.append("Forma adoption:")
        lines.append(f"  recommendation: {forma_adoption.get('recommendation')}")
        lines.append(f"  value: {forma_adoption.get('value')}")
        lines.append(f"  proposal: {forma_adoption.get('proposal')}")
        lines.append(f"  cleanup_policy: {forma_adoption.get('cleanup_policy')}")
        lines.append("  owner confirmations:")
        for decision in forma_adoption.get("owner_confirmations", []):
            lines.append(f"  - {decision}")
    if report.programmatic_actions or report.agent_handoffs:
        lines.append("")
        lines.append("Next:")
        next_index = 1
        if report.agent_handoffs:
            primary_handoff = report.agent_handoffs[0]
            if primary_handoff.handoff_kind == HANDOFF_KIND_PROFILE_REFINEMENT:
                lines.append(
                    f"  {next_index}. Continue the profile refinement review with "
                    "`forma doctor --format agent <repo>`, then follow "
                    "`forma explain profile --format agent --target <target>`."
                )
                lines.append(
                    "     End with a recommended next step and ask whether the "
                    "user wants you to do it."
                )
            else:
                lines.append(
                    f"  {next_index}. Continue the Agent remediation review; "
                    "do not return unresolved findings as the final diagnosis."
                )
            lines.append(
                "     Do not return unresolved findings as the final diagnosis."
            )
            next_index += 1
        if report.programmatic_actions:
            lines.append(
                f"  {next_index}. Tell the owner Forma can manage this repo's engineering rules; "
                "if approved, run `forma init --from-report <report>` to create workflow source."
            )
    return "\n".join(lines)


def _render_agent(report: RepoDoctorReport) -> str:
    primary_handoff = report.agent_handoffs[0] if report.agent_handoffs else None
    lines = [
        "REPO DOCTOR AGENT HANDOFF",
        f"command: {report.command}",
        f"subject: {report.subject}",
        f"status: {report.status}",
        f"summary: {report.summary}",
        "guide: forma explain agent",
        "targeted_guide: forma explain agent --target codex|claude-code|opencode",
        f"terminal: {'true' if report.terminal else 'false'}",
        f"terminal_reason: {report.terminal_reason}",
        f"next_required_action: {report.next_required_action}",
    ]
    if primary_handoff is not None:
        lines.extend(
            [
                f"primary_handoff: {primary_handoff.title}",
                f"primary_handoff_kind: {primary_handoff.handoff_kind}",
                "",
                "continuation:",
                "- Follow the primary handoff before summarizing findings or chasing secondary gaps.",
                f"- If the primary handoff is {HANDOFF_TITLE_PROFILE_REFINEMENT}, load `forma explain profile --format agent --target <target>` next; do not reroute back through `forma explain agent`.",
                f"- For {HANDOFF_TITLE_PROFILE_REFINEMENT}, the final answer must use the exact section headings required by `forma explain profile`, including `Recommended Next Step`.",
                "- When the recommended next step needs user confirmation, use a host structured user-input, choice, or command-approval UI if available; otherwise end with `Required Confirmation:`.",
                "- Treat findings as investigation inputs, not verified final conclusions.",
                "- Assign dispositions to non-contract core findings after the primary handoff; valid dispositions are confirmed, resolved, not applicable, blocked by unavailable evidence, or owner decision required.",
                "- Stop only when the primary handoff is complete and every required finding has a disposition, an owner decision is required, evidence is unavailable, or an unsafe blocker is present.",
                "- Do not return this handoff unchanged as the final user answer.",
                "- Before profile authoring, summarize the repository purpose and maintenance model from source-backed facts; doctor-ready operability is not a project-ready profile.",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "continuation:",
                "- Treat findings as investigation inputs, not verified final conclusions.",
                "- Assign a disposition to every non-contract core finding before reporting the diagnosis.",
                "- Valid dispositions: confirmed, resolved, not applicable, blocked by unavailable evidence, or owner decision required.",
                "- Stop only when every finding has a disposition, an owner decision is required, evidence is unavailable, or an unsafe blocker is present.",
                "- Do not return this handoff unchanged as the final user answer.",
                "- Before profile authoring, summarize the repository purpose and maintenance model from source-backed facts; doctor-ready operability is not a project-ready profile.",
            ]
        )
    lines.extend(
        [
            "",
            "project_understanding:",
            "  purpose_sources:",
        ]
    )
    purpose_sources = report.facts.get("purpose_sources", [])
    if purpose_sources:
        lines.extend(f"  - {source}" for source in purpose_sources)
    else:
        lines.append("  - none discovered by doctor; request or inspect project source material before profile authoring")
    lines.extend(
        [
            "  required_summary:",
            "  - what this repository is for and what it delivers",
            "  - what makes changes correct, safe, and maintainable for this project",
            "  - which durable maintenance rules belong in a profile beyond operability findings",
            "  semantic_dimensions:",
        ]
    )
    prompts = report.facts.get("maintenance_semantic_prompts", [])
    if prompts:
        lines.extend(f"  - {prompt}" for prompt in prompts)
    else:
        lines.append("  - repository purpose and maintenance model")
    lines.extend(
        [
            "  profile_boundary: if a candidate profile only encodes doctor findings, label it operability-only, not project-ready",
            "",
        ]
    )
    for handoff in report.agent_handoffs:
        lines.append(f"handoff: {handoff.title}")
        lines.append(f"handoff_kind: {handoff.handoff_kind}")
        lines.append("read_first:")
        for path in handoff.read_first:
            lines.append(f"- {path}")
        lines.append("")
        lines.append("actions:")
        for question in handoff.questions:
            lines.append(f"- {question}")
        lines.append("")
        lines.append("forbidden:")
        for forbidden in handoff.forbidden:
            lines.append(f"- {forbidden}")
        lines.append("")
        lines.append("return_shape:")
        for key, value in handoff.return_shape.items():
            lines.append(f"- {key}: {value}")
        if handoff.next_action is not None:
            action = handoff.next_action
            lines.append("")
            lines.append("next_action:")
            lines.append(f"- title: {action.title}")
            if action.handoff_kind is not None:
                lines.append(f"- handoff_kind: {action.handoff_kind}")
            if action.description is not None:
                lines.append(f"- description: {action.description}")
            if action.interaction is not None:
                lines.append(f"- interaction: {action.interaction}")
            if action.requires_confirmation:
                lines.append("- requires_confirmation: true")
            if action.confirmation_prompt is not None:
                lines.append(f"- confirmation_prompt: {action.confirmation_prompt}")
        lines.append("")
    lines.extend(
        [
            "findings:",
        ]
    )
    for finding in report.findings:
        lines.append(f"- {finding.domain}: {finding.status}")
        lines.append(f"  summary: {finding.summary}")
        if finding.evidence:
            lines.append(f"  evidence: {', '.join(finding.evidence)}")
        if finding.handoff:
            lines.append(f"  action: {finding.handoff}")
    instruction_quality = report.facts.get("agent_instruction_quality")
    if isinstance(instruction_quality, dict):
        lines.append("")
        lines.append("instruction_quality:")
        lines.append("  standard: provider-informed heuristic, not a universal agent standard")
        lines.append(f"  status: {instruction_quality.get('status')}")
        lines.append(f"  entrypoint_count: {instruction_quality.get('entrypoint_count')}")
        lines.append(f"  reference_count: {instruction_quality.get('reference_count')}")
        basis = instruction_quality.get("basis", [])
        if basis:
            lines.append("  basis:")
            for item in basis:
                lines.append(f"  - {item}")
        lines.append("  criteria:")
        for criterion in instruction_quality.get("criteria", []):
            lines.append(f"  - {criterion}")
        validation_sources = instruction_quality.get("validation_sources", [])
        lines.append("  validation_sources:")
        if validation_sources:
            for source in validation_sources:
                lines.append(f"  - {source}")
        else:
            lines.append("  - none")
        lines.append("  issues:")
        issues = instruction_quality.get("issues", [])
        if issues:
            for issue in issues:
                lines.append(f"  - {issue}")
        else:
            lines.append("  - none")
    instruction_polarity = report.facts.get("instruction_polarity")
    if isinstance(instruction_polarity, dict):
        lines.append("")
        lines.append("instruction_polarity:")
        lines.append("  standard: positive-contract heuristic for agent-facing rules")
        lines.append(f"  status: {instruction_polarity.get('status')}")
        lines.append(f"  analyzed_doc_count: {len(instruction_polarity.get('analyzed_docs', []))}")
        lines.append(f"  negative_rule_count: {instruction_polarity.get('negative_rule_count')}")
        lines.append(
            f"  ordinary_prohibition_count: {instruction_polarity.get('ordinary_prohibition_count')}"
        )
        lines.append(
            f"  hard_risk_prohibition_count: {instruction_polarity.get('hard_risk_prohibition_count')}"
        )
        lines.append(f"  unpaired_ordinary_count: {instruction_polarity.get('unpaired_ordinary_count')}")
        lines.append("  criteria:")
        for criterion in instruction_polarity.get("criteria", []):
            lines.append(f"  - {criterion}")
        lines.append("  sample_locations:")
        samples = instruction_polarity.get("sample_locations", [])
        if samples:
            for sample in samples:
                lines.append(
                    "  - "
                    f"{sample.get('path')}:{sample.get('line')} "
                    f"{sample.get('category')} "
                    f"paired={sample.get('paired_positive_contract')}"
                )
        else:
            lines.append("  - none")
    markdown_coverage = report.facts.get("markdown_rule_coverage")
    if isinstance(markdown_coverage, dict):
        lines.append("")
        lines.append("markdown_rule_coverage:")
        lines.append("  standard: read-first reachability heuristic for rule-like Markdown")
        lines.append(f"  status: {markdown_coverage.get('status')}")
        lines.append(f"  analyzed_markdown_count: {markdown_coverage.get('analyzed_markdown_count')}")
        lines.append(f"  reachable_markdown_count: {markdown_coverage.get('reachable_markdown_count')}")
        lines.append(
            "  unreferenced_rule_markdown_count: "
            f"{markdown_coverage.get('unreferenced_rule_markdown_count')}"
        )
        lines.append("  criteria:")
        for criterion in markdown_coverage.get("criteria", []):
            lines.append(f"  - {criterion}")
        lines.append("  sample_locations:")
        samples = markdown_coverage.get("sample_locations", [])
        if samples:
            for sample in samples:
                lines.append(
                    "  - "
                    f"{sample.get('path')}:{sample.get('line')} "
                    f"terms={','.join(sample.get('matched_terms', []))}"
                )
        else:
            lines.append("  - none")
    forma_adoption = report.facts.get("forma_adoption")
    if isinstance(forma_adoption, dict):
        lines.append("")
        lines.append("forma_adoption:")
        lines.append(f"  status: {forma_adoption.get('status')}")
        lines.append(f"  recommendation: {forma_adoption.get('recommendation')}")
        lines.append(f"  value: {forma_adoption.get('value')}")
        lines.append(f"  proposal: {forma_adoption.get('proposal')}")
        lines.append(f"  cleanup_policy: {forma_adoption.get('cleanup_policy')}")
        lines.append("  owner_confirmations:")
        for decision in forma_adoption.get("owner_confirmations", []):
            lines.append(f"  - {decision}")
    reference_quality = report.facts.get("entrypoint_reference_quality")
    if isinstance(reference_quality, dict):
        lines.append("")
        lines.append("reference_quality:")
        lines.append("  standard: traversal-safety diagnostic for agent read-first Markdown")
        lines.append(f"  status: {reference_quality.get('status')}")
        lines.append(f"  entrypoint_count: {reference_quality.get('entrypoint_count')}")
        lines.append(f"  reference_count: {reference_quality.get('reference_count')}")
        lines.append("  criteria:")
        for criterion in reference_quality.get("criteria", []):
            lines.append(f"  - {criterion}")
        lines.append("  issues:")
        issues = reference_quality.get("issues", [])
        if issues:
            for issue in issues:
                lines.append(f"  - {issue}")
        else:
            lines.append("  - none")
    return "\n".join(lines)


def _validation_evidence(
    root: Path,
    entrypoint_references: tuple[str, ...] = (),
) -> tuple[str, ...]:
    candidate_files = (
        "AGENTS.md",
        "README.md",
        "README.zh-CN.md",
        "docs/usage.md",
        "docs/quick-start.md",
        "Makefile",
        "justfile",
        *entrypoint_references,
    )
    commands = (
        "uv run",
        "pytest",
        "npm test",
        "pnpm test",
        "make test",
        "go test",
        "cargo test",
        "git diff --check",
        "golangci-lint",
        "test/buildup",
        "test/start",
        "test/run",
    )
    evidence: list[str] = []
    for rel in _dedupe(list(candidate_files)):
        path = root / rel
        if not path.is_file():
            continue
        text = _read_text(path).lower()
        if any(command in text for command in commands):
            evidence.append(rel)
    return tuple(evidence)


def _entrypoint_reference_docs(
    root: Path,
    entrypoints: tuple[str, ...],
) -> tuple[tuple[str, ...], tuple[dict[str, list[str]], ...]]:
    references: list[str] = []
    cycles: list[dict[str, list[str]]] = []
    queue = [(rel, (rel,)) for rel in entrypoints if (root / rel).is_file()]
    seen = {rel for rel, _chain in queue}
    while queue and len(references) < MAX_ENTRYPOINT_REFERENCES:
        rel, chain = queue.pop(0)
        for linked in _local_markdown_links(root, rel):
            if linked in chain:
                cycle = {"path": [*chain, linked]}
                if cycle not in cycles:
                    cycles.append(cycle)
                continue
            if linked in seen:
                continue
            seen.add(linked)
            references.append(linked)
            queue.append((linked, (*chain, linked)))
            if len(references) >= MAX_ENTRYPOINT_REFERENCES:
                break
    return tuple(references), tuple(cycles)


def _local_entrypoints(root: Path, root_entrypoints: tuple[str, ...]) -> tuple[str, ...]:
    root_entrypoint_set = set(root_entrypoints)
    discovered: list[str] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(
            dirname for dirname in dirnames if dirname not in ENTRYPOINT_SCAN_SKIP_DIRS
        )
        for filename in sorted(filenames):
            if len(discovered) >= MAX_LOCAL_ENTRYPOINTS:
                return tuple(discovered)
            if filename.casefold() not in LOCAL_ENTRYPOINT_NAMES:
                continue
            path = Path(dirpath) / filename
            try:
                rel = path.relative_to(root).as_posix()
            except ValueError:
                continue
            if rel in root_entrypoint_set:
                continue
            discovered.append(rel)
    return tuple(sorted(discovered))


def _candidate_markdown_docs(root: Path, entrypoints: tuple[str, ...]) -> tuple[str, ...]:
    docs: list[str] = []
    entrypoint_set = set(entrypoints)
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = Path(dirpath).relative_to(root)
        parts = set(rel_dir.parts)
        dirnames[:] = sorted(
            dirname
            for dirname in dirnames
            if dirname not in MARKDOWN_COVERAGE_SKIP_DIRS
            and dirname not in {".mypy_cache", ".pytest_cache", ".ruff_cache"}
        )
        if parts & MARKDOWN_COVERAGE_SKIP_DIRS:
            continue
        for filename in sorted(filenames):
            path = Path(dirpath) / filename
            if path.suffix.lower() not in {".md", ".markdown"}:
                continue
            rel = path.relative_to(root).as_posix()
            if (
                rel in entrypoint_set
                or "/" not in rel
                or rel.startswith(("docs/", ".github/"))
            ):
                docs.append(rel)
    return tuple(_dedupe(docs))


def _plain_mentioned_markdown_docs(
    root: Path,
    entrypoints: tuple[str, ...],
    markdown_docs: tuple[str, ...],
) -> tuple[str, ...]:
    mentioned: list[str] = []
    entrypoint_text = "\n".join(_read_text(root / rel) for rel in entrypoints).lower()
    if not entrypoint_text:
        return ()
    for rel in markdown_docs:
        rel_lower = rel.lower()
        name_lower = Path(rel).name.lower()
        if rel_lower in entrypoint_text or name_lower in entrypoint_text:
            mentioned.append(rel)
    return tuple(_dedupe(mentioned))


def _local_markdown_links(root: Path, source_rel: str) -> tuple[str, ...]:
    source = root / source_rel
    text = _read_text(source)
    links: list[str] = []
    for match in MARKDOWN_LINK_RE.finditer(text):
        target = match.group(1).strip()
        rel = _normalize_local_reference(root, source_rel, target)
        if rel is not None and rel not in links:
            links.append(rel)
    for match in AT_REFERENCE_RE.finditer(text):
        target = match.group(1).strip()
        rel = _normalize_local_reference(root, source_rel, target)
        if rel is not None and rel not in links:
            links.append(rel)
    return tuple(links)


def _normalize_local_reference(root: Path, source_rel: str, target: str) -> str | None:
    target = target.split("#", 1)[0].strip().strip("<>").strip("'\"").rstrip(".,;:")
    if not target or target.startswith(("#", "/")):
        return None
    if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", target):
        return None
    source_parent = (root / source_rel).parent
    candidate = (source_parent / target).resolve()
    try:
        rel_path = candidate.relative_to(root.resolve())
    except ValueError:
        return None
    if not candidate.is_file():
        return None
    if candidate.suffix.lower() not in INSTRUCTION_REFERENCE_SUFFIXES:
        return None
    return rel_path.as_posix()


def _resolve_case_insensitive(root: Path, rel: str) -> str | None:
    parts = Path(rel).parts
    current = root
    resolved_parts: list[str] = []
    for part in parts:
        if not current.is_dir():
            return None
        try:
            entries = {entry.name.casefold(): entry.name for entry in current.iterdir()}
        except OSError:
            return None
        actual = entries.get(part.casefold())
        if actual is None:
            return None
        resolved_parts.append(actual)
        current = current / actual
    if not current.exists():
        return None
    return Path(*resolved_parts).as_posix()


def _existing_entrypoints(root: Path, rel_paths: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(
        actual
        for rel in rel_paths
        if (actual := _resolve_case_insensitive(root, rel)) is not None
        and (root / actual).is_file()
    )


def _existing(root: Path, rel_paths: tuple[str, ...]) -> tuple[str, ...]:
    return tuple(rel for rel in rel_paths if (root / rel).exists())


def _any_file_contains(root: Path, rel_paths: tuple[str, ...], needles: tuple[str, ...]) -> bool:
    lowered = tuple(needle.lower() for needle in needles)
    for rel in rel_paths:
        path = root / rel
        if path.is_dir():
            continue
        text = _read_text(path).lower()
        if any(needle in text for needle in lowered):
            return True
    return False


def _looks_structured_markdown(text: str) -> bool:
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("#", "- ", "* ", "> ", "| ")) or re.match(r"\d+\.\s+", stripped):
            return True
    return False


def _has_nearby_positive_contract(lines: list[str], index: int) -> bool:
    start = max(0, index - 2)
    end = min(len(lines), index + 3)
    for nearby_index in range(start, end):
        if nearby_index == index:
            continue
        line = lines[nearby_index].strip()
        if not line or NEGATIVE_RULE_RE.search(line) is not None:
            continue
        if _has_any_term(line, POSITIVE_CONTRACT_TERMS):
            return True
    return False


def _has_any_term(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in terms)


def _trim_text(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return f"{text[: limit - 3].rstrip()}..."


def _markdown_rule_signal(root: Path, rel: str) -> dict[str, Any] | None:
    path = root / rel
    text = _read_text(path)
    fallback: dict[str, Any] | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        matched = tuple(term for term in RULE_MARKDOWN_HINT_TERMS if term in stripped.lower())
        if not matched:
            continue
        item = {
            "path": rel,
            "line": line_number,
            "text": _trim_text(stripped, 220),
            "matched_terms": list(matched[:5]),
        }
        if stripped.startswith("#"):
            fallback = fallback or item
            continue
        return item
    return fallback


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result
