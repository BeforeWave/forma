"""Deterministic Forma repository initialization remediation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from forma.repo_doctor import REPO_DOCTOR_SCHEMA, diagnose_repo
from forma.reports import ActionableReport, NextAction, ReportSection


@dataclass(frozen=True)
class InitFile:
    path: Path
    description: str
    content: str
    executable: bool = False


def plan_init(
    *,
    root: Path,
    profile_dir: Path | None,
    apply: bool,
    from_report: Path | None = None,
) -> ActionableReport:
    repo_root = root.resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        return ActionableReport(
            command="forma init",
            subject=str(repo_root),
            status="unsafe",
            summary="init target is not an existing directory",
            blockers=("provide an existing repository directory",),
        )

    report_data: dict[str, Any] | None = None
    if from_report is not None:
        loaded = _load_report(from_report)
        if isinstance(loaded, ActionableReport):
            return loaded
        report_data = loaded
        mismatch = _report_subject_mismatch(repo_root, report_data)
        if mismatch is not None:
            return ActionableReport(
                command="forma init",
                subject=str(repo_root),
                status="unsafe",
                summary="doctor report does not match init target",
                blockers=(mismatch,),
            )

    resolved_profile_dir = _resolve_profile_dir(repo_root, profile_dir)
    files = _init_files(repo_root, resolved_profile_dir, report_data)
    changes = [_plan_or_apply(file, repo_root, apply) for file in files]
    diagnosis = _diagnosis_summary(repo_root, report_data)
    verb = "applied" if apply else "planned"
    report_mode = " from repo doctor report" if report_data is not None else ""
    status = "needs-agent" if report_data is not None else "needs-human"
    warnings = [
        "init creates draft workflow source only; it does not review or approve a profile",
        "accepted .forma contents should be tracked by Git",
    ]
    if report_data is not None:
        warnings.append(
            "from-report materializes deterministic workflow source and handoff files only; Agent remediation is still required before calling the repo agent-friendly"
        )
    return ActionableReport(
        command="forma init",
        subject=str(repo_root),
        status=status,
        summary=f"deterministic Forma initialization {verb}{report_mode}",
        sections=(
            ReportSection(
                kind="repo-diagnosis",
                title="Repository Diagnosis",
                payload=diagnosis,
            ),
            ReportSection(
                kind="planned-changes" if not apply else "applied-changes",
                title="Planned Changes" if not apply else "Applied Changes",
                payload={"items": changes},
            ),
            ReportSection(
                kind="agent-operability-handoff",
                title="Agent Operability Handoff",
                payload=_handoff_summary(report_data),
            )
            if report_data is not None
            else ReportSection(
                kind="init-mode",
                title="Init Mode",
                payload="run `forma doctor --format json` first when report-derived workflow source is needed",
            ),
        ),
        next_actions=(
            NextAction(
                title="use generated workflow source as project-rule input",
                description=(
                    "Treat .forma contents as draft project workflow source and "
                    "project-rule management input; Agent remediation and owner "
                    "confirmations are still required before durable workflow generation."
                ),
            ),
            NextAction(
                title="run repo doctor after edits",
                command=f"forma doctor {_display_path(repo_root, repo_root)}",
            ),
        ),
        warnings=tuple(warnings),
    )


def _resolve_profile_dir(root: Path, profile_dir: Path | None) -> Path:
    if profile_dir is None:
        return root / ".forma"
    if profile_dir.is_absolute():
        return profile_dir
    return root / profile_dir


def _plan_or_apply(file: InitFile, root: Path, apply: bool) -> dict[str, str]:
    exists = file.path.exists()
    action = "skip-existing" if exists else ("create" if apply else "plan-create")
    if apply and not exists:
        file.path.parent.mkdir(parents=True, exist_ok=True)
        file.path.write_text(file.content, encoding="utf-8")
        if file.executable:
            file.path.chmod(0o755)
    return {
        "path": _display_path(root, file.path),
        "action": action,
        "description": file.description,
    }


def _init_files(
    root: Path,
    profile_dir: Path,
    report_data: dict[str, Any] | None,
) -> tuple[InitFile, ...]:
    files = [
        InitFile(
            path=root / ".forma" / ".gitignore",
            description="Ignore Forma runtime state while keeping workflow source tracked.",
            content=FORMA_GITIGNORE,
        ),
        InitFile(
            path=profile_dir / "profile.yaml",
            description="Draft profile skeleton; requires human review before use.",
            content=PROFILE_YAML,
        ),
        InitFile(
            path=profile_dir / "reinstall-workflow.sh",
            description="Single profile-local reinstall entrypoint skeleton.",
            content=REINSTALL_WORKFLOW,
            executable=True,
        ),
    ]
    if report_data is not None:
        handoff_dir = root / ".forma" / "agent-operability"
        files.extend(
            [
                InitFile(
                    path=handoff_dir / "doctor-report.json",
                    description="Sanitized repo doctor facts and findings for Agent remediation.",
                    content=_doctor_report_json(report_data),
                ),
                InitFile(
                    path=handoff_dir / "agent-handoff.md",
                    description="Agent remediation handoff generated from repo doctor findings.",
                    content=_agent_handoff_markdown(report_data),
                ),
                InitFile(
                    path=handoff_dir / "human-decisions.md",
                    description="Owner decision checklist generated from repo doctor findings.",
                    content=_human_decisions_markdown(report_data),
                ),
            ]
        )
    return tuple(files)


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _load_report(path: Path) -> dict[str, Any] | ActionableReport:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return ActionableReport(
            command="forma init",
            subject=str(path),
            status="unsafe",
            summary="doctor report could not be read",
            blockers=(str(exc),),
        )
    if not isinstance(raw, dict):
        return ActionableReport(
            command="forma init",
            subject=str(path),
            status="unsafe",
            summary="doctor report must be a JSON object",
            blockers=("report root is not an object",),
        )
    if raw.get("schema") != REPO_DOCTOR_SCHEMA:
        return ActionableReport(
            command="forma init",
            subject=str(path),
            status="unsafe",
            summary="unsupported doctor report schema",
            blockers=(f"expected {REPO_DOCTOR_SCHEMA}",),
        )
    if raw.get("command") != "forma doctor":
        return ActionableReport(
            command="forma init",
            subject=str(path),
            status="unsafe",
            summary="unsupported doctor report command",
            blockers=("expected command `forma doctor`",),
        )
    subject = raw.get("subject")
    if not isinstance(subject, str) or not subject.strip():
        return ActionableReport(
            command="forma init",
            subject=str(path),
            status="unsafe",
            summary="doctor report is missing subject",
            blockers=("report subject must be a non-empty string",),
        )
    return raw


def _report_subject_mismatch(root: Path, report_data: dict[str, Any]) -> str | None:
    subject = str(report_data["subject"])
    subject_path = Path(subject)
    if not subject_path.is_absolute():
        subject_path = root / subject_path
    try:
        resolved_subject = subject_path.resolve()
    except OSError:
        resolved_subject = subject_path.absolute()
    if resolved_subject != root:
        return f"report subject {subject!r} does not match init target {str(root)!r}"
    return None


def _diagnosis_summary(root: Path, report_data: dict[str, Any] | None) -> dict[str, Any]:
    if report_data is None:
        doctor = diagnose_repo(root)
        return {
            "status": doctor.status,
            "summary": doctor.summary,
        }
    return {
        "status": report_data.get("status"),
        "summary": report_data.get("summary"),
        "schema": report_data.get("schema"),
    }


def _handoff_summary(report_data: dict[str, Any] | None) -> dict[str, Any]:
    if report_data is None:
        return {}
    return {
        "facts_file": ".forma/agent-operability/doctor-report.json",
        "agent_handoff": ".forma/agent-operability/agent-handoff.md",
        "human_decisions": ".forma/agent-operability/human-decisions.md",
        "programmatic_actions": len(report_data.get("programmatic_actions", [])),
        "agent_handoffs": len(report_data.get("agent_handoffs", [])),
        "human_decisions_count": len(report_data.get("human_decisions", [])),
    }


def _doctor_report_json(report_data: dict[str, Any]) -> str:
    sanitized = {
        "schema": report_data.get("schema"),
        "command": report_data.get("command"),
        "subject": ".",
        "status": report_data.get("status"),
        "summary": report_data.get("summary"),
        "facts": report_data.get("facts", {}),
        "findings": report_data.get("findings", []),
        "evidence": report_data.get("evidence", {}),
        "confidence": report_data.get("confidence"),
        "programmatic_actions": report_data.get("programmatic_actions", []),
        "agent_handoffs": report_data.get("agent_handoffs", []),
        "human_decisions": report_data.get("human_decisions", []),
    }
    return json.dumps(sanitized, indent=2, sort_keys=True) + "\n"


def _agent_handoff_markdown(report_data: dict[str, Any]) -> str:
    lines = [
        "# Agent Operability Handoff",
        "",
        "This file is generated from `forma doctor --format json`.",
        "It is handoff input for Agent remediation, not approved durable project rules.",
        "",
        f"Status: {report_data.get('status')}",
        f"Summary: {report_data.get('summary')}",
        "",
        "## Findings",
    ]
    for finding in report_data.get("findings", []):
        if not isinstance(finding, dict):
            continue
        lines.append(f"- {finding.get('domain')}: {finding.get('status')} - {finding.get('summary')}")
    lines.extend(["", "## Agent Questions"])
    for handoff in report_data.get("agent_handoffs", []):
        if not isinstance(handoff, dict):
            continue
        for question in handoff.get("questions", []):
            lines.append(f"- {question}")
    lines.extend(
        [
            "",
            "## Return Shape",
            "- Programmatic changes: deterministic files or checklist updates.",
            "- Semantic changes: repo-rule or documentation proposals for Agent review.",
            "- Owner confirmations: approval points required before durable adoption.",
            "",
        ]
    )
    return "\n".join(lines)


def _human_decisions_markdown(report_data: dict[str, Any]) -> str:
    lines = [
        "# Owner Confirmations",
        "",
        "This checklist is generated from the repo doctor report.",
        "It does not approve any durable project rule by itself.",
        "",
    ]
    decisions = report_data.get("human_decisions", [])
    if not decisions:
        lines.append("- None recorded by the report.")
    for decision in decisions:
        if not isinstance(decision, dict):
            continue
        lines.append(f"- {decision.get('id')}: {decision.get('description')}")
    lines.append("")
    return "\n".join(lines)


PROFILE_YAML = """profile:
  id: local-project
  description: Draft local Forma profile. Review before workflow generation.
bundle:
  name: local-project
  description: Draft local workflow bundle. Review before use.
constraints:
  default:
    - Replace this draft constraint with reviewed project rules before building installable workflow output.
    - Treat .forma/agent-operability files as handoff input, not approved durable rules.
"""


FORMA_GITIGNORE = """/state/
"""


REINSTALL_WORKFLOW = """#!/usr/bin/env sh
set -eu

FORMA_REINSTALL_WORKFLOW_BOOTSTRAP_INCOMPLETE=1

cat <<'MSG'
This reinstall-workflow.sh is bootstrap-incomplete.

Before using it as a reusable profile-local reinstall flow, confirm the install
facts with the user and replace this skeleton with a fixed-fact script:

- artifact kind
- target
- plugin id when the artifact kind is plugin
- marketplace name when the target install uses a marketplace
- marketplace source when the target install uses a marketplace
- install selector
- visibility check

The completed script should run the build, freshness gate, verify gate, install
or marketplace refresh, and visibility check with those facts encoded. It should
not list marketplaces or leave plugin id, marketplace, selector, or source
refresh decisions open at runtime.
MSG

exit 3
"""
