"""Shared actionable report envelope and renderers for CLI handoff output."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Literal, Mapping, Sequence

ReportFormat = Literal["human", "agent", "json"]
REPORT_FORMATS: tuple[ReportFormat, ...] = ("human", "agent", "json")


@dataclass(frozen=True)
class ReportSection:
    kind: str
    title: str
    payload: str | Sequence[str] | Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "title": self.title,
            "payload": _jsonable(self.payload),
        }


@dataclass(frozen=True)
class NextAction:
    title: str
    command: str | None = None
    description: str | None = None
    stop_condition: str | None = None
    forbidden: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {"title": self.title}
        if self.command is not None:
            data["command"] = self.command
        if self.description is not None:
            data["description"] = self.description
        if self.stop_condition is not None:
            data["stop_condition"] = self.stop_condition
        if self.forbidden:
            data["forbidden"] = list(self.forbidden)
        return data


@dataclass(frozen=True)
class ActionableReport:
    command: str
    subject: str
    status: str
    summary: str
    schema: str = "forma.actionable-report.v1"
    sections: tuple[ReportSection, ...] = ()
    next_actions: tuple[NextAction, ...] = ()
    blockers: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "schema": self.schema,
            "command": self.command,
            "subject": self.subject,
            "status": self.status,
            "summary": self.summary,
        }
        if self.sections:
            data["sections"] = [section.to_dict() for section in self.sections]
        if self.next_actions:
            data["next_actions"] = [action.to_dict() for action in self.next_actions]
        if self.blockers:
            data["blockers"] = list(self.blockers)
        if self.warnings:
            data["warnings"] = list(self.warnings)
        if self.metadata:
            data["metadata"] = _jsonable(self.metadata)
        return data

    def render(self, output_format: ReportFormat) -> str:
        if output_format == "human":
            return render_human(self)
        if output_format == "agent":
            return render_agent(self)
        if output_format == "json":
            return render_json(self)
        raise ValueError(
            "unsupported report format "
            f"{output_format!r}; expected one of {', '.join(REPORT_FORMATS)}"
        )


def render_report(report: ActionableReport, output_format: ReportFormat) -> str:
    return report.render(output_format)


def render_json(report: ActionableReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True)


def render_human(report: ActionableReport) -> str:
    lines = [
        f"{report.command}: {report.summary}",
        f"status: {report.status}",
        f"subject: {report.subject}",
    ]
    _append_list(lines, "Warnings", report.warnings)
    _append_list(lines, "Blockers", report.blockers)
    for section in report.sections:
        if not _human_should_show_section(section):
            continue
        lines.append("")
        lines.append(section.title)
        _append_payload(lines, section.payload)
    visible_next_actions = [
        action for action in report.next_actions if _human_should_show_next_action(report, action)
    ]
    if visible_next_actions:
        lines.append("")
        lines.append("Next:")
        for action in visible_next_actions:
            if action.command is not None:
                lines.append(f"  - {action.title}: {action.command}")
            else:
                lines.append(f"  - {action.title}")
            if action.description is not None:
                lines.append(f"    {action.description}")
    return "\n".join(lines)


def _human_should_show_section(section: ReportSection) -> bool:
    agent_only_kinds = {
        "codex-plugin-handoff",
        "profile-local-reinstall-workflow",
    }
    return section.kind not in agent_only_kinds


def _human_should_show_next_action(
    report: ActionableReport,
    action: NextAction,
) -> bool:
    if report.command.startswith("forma build "):
        return False
    return not action.forbidden and action.stop_condition is None


def render_agent(report: ActionableReport) -> str:
    lines = [
        "ACTIONABLE REPORT",
        f"command: {report.command}",
        f"subject: {report.subject}",
        f"status: {report.status}",
        f"summary: {report.summary}",
    ]
    _append_list(lines, "warnings", report.warnings)
    _append_list(lines, "blockers", report.blockers)
    for section in report.sections:
        lines.append("")
        lines.append(f"[{section.kind}] {section.title}")
        _append_payload(lines, section.payload)
    if report.next_actions:
        lines.append("")
        lines.append("next_actions:")
        for index, action in enumerate(report.next_actions, start=1):
            lines.append(f"{index}. {action.title}")
            if action.command is not None:
                lines.append(f"   command: {action.command}")
            if action.description is not None:
                lines.append(f"   detail: {action.description}")
            if action.stop_condition is not None:
                lines.append(f"   stop_condition: {action.stop_condition}")
            for forbidden in action.forbidden:
                lines.append(f"   forbidden: {forbidden}")
    return "\n".join(lines)


def _append_list(lines: list[str], title: str, values: Sequence[str]) -> None:
    if not values:
        return
    lines.append("")
    lines.append(f"{title}:")
    for value in values:
        lines.append(f"  - {value}")


def _append_payload(
    lines: list[str],
    payload: str | Sequence[str] | Mapping[str, Any],
) -> None:
    if isinstance(payload, str):
        for line in payload.splitlines() or [""]:
            lines.append(f"  {line}")
        return
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            lines.append(f"  {key}: {_format_scalar(value)}")
        return
    for item in payload:
        lines.append(f"  - {_format_scalar(item)}")


def _format_scalar(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(_jsonable(value), sort_keys=True)
    return str(value)


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value
