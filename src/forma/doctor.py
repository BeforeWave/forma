"""Artifact diagnosis for agent handoff and install routing."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from forma.install import classify_install_artifact
from forma.plugin_guidance import codex_plugin_name
from forma_verifier import verify


@dataclass(frozen=True)
class DoctorReport:
    path: str
    artifact_kind: str
    target: str
    verification_passed: bool
    verification_summary: dict[str, int]
    verification_bundle_kind: str
    forma_install_supported: bool
    installable_now: bool
    install_route: str
    blockers: tuple[str, ...]
    next_steps: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema": "forma.doctor.report.v1",
            "path": self.path,
            "artifact_kind": self.artifact_kind,
            "target": self.target,
            "verification": {
                "passed": self.verification_passed,
                "bundle_kind": self.verification_bundle_kind,
                "summary": self.verification_summary,
            },
            "forma_install_supported": self.forma_install_supported,
            "installable_now": self.installable_now,
            "install_route": self.install_route,
            "blockers": list(self.blockers),
            "next_steps": list(self.next_steps),
        }

    def format_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    def format_human(self) -> str:
        verification = "passed" if self.verification_passed else "failed"
        forma_install = "yes" if self.forma_install_supported else "no"
        installable_now = "yes" if self.installable_now else "no"
        lines = [
            f"forma doctor: {self.path}",
            f"  artifact kind : {self.artifact_kind}",
            f"  target        : {self.target}",
            f"  verification  : {verification}",
            f"  forma install : {forma_install}",
            f"  installable   : {installable_now}",
            f"  install route : {self.install_route}",
        ]
        if self.blockers:
            lines.append("")
            lines.append("Blockers:")
            for blocker in self.blockers:
                lines.append(f"  - {blocker}")
        if self.next_steps:
            lines.append("")
            lines.append("Next:")
            for step in self.next_steps:
                lines.append(f"  - {step}")
        return "\n".join(lines)


def diagnose_artifact(path: Path) -> DoctorReport:
    """Return the install and verification diagnosis for an artifact path."""
    source = path.resolve()
    report = verify(source)
    artifact_kind = _safe_artifact_kind(source)
    target = _artifact_target(source, artifact_kind)
    forma_supported = artifact_kind in {"skill", "skill-bundle", "claude-code-plugin"}
    blockers = _blockers(report.passed, artifact_kind, forma_supported)
    installable_now = report.passed and forma_supported
    install_route = _install_route(source, artifact_kind, target)
    next_steps = _next_steps(source, artifact_kind, target, report.passed)
    summary = report.to_dict()["summary"]
    assert isinstance(summary, dict)
    return DoctorReport(
        path=str(source),
        artifact_kind=artifact_kind,
        target=target,
        verification_passed=report.passed,
        verification_summary={
            "errors": int(summary["errors"]),
            "warnings": int(summary["warnings"]),
            "infos": int(summary["infos"]),
            "total": int(summary["total"]),
        },
        verification_bundle_kind=report.bundle_kind,
        forma_install_supported=forma_supported,
        installable_now=installable_now,
        install_route=install_route,
        blockers=tuple(blockers),
        next_steps=tuple(next_steps),
    )


def _safe_artifact_kind(source: Path) -> str:
    try:
        return classify_install_artifact(source)
    except ValueError:
        return "unsupported"


def _artifact_target(source: Path, artifact_kind: str) -> str:
    if artifact_kind == "codex-plugin":
        return "codex"
    if artifact_kind == "claude-code-plugin":
        return "claude-code"
    manifest = _load_manifest(source)
    target = manifest.get("target")
    if isinstance(target, str) and target.strip():
        return target.strip()
    return "unknown"


def _load_manifest(source: Path) -> dict[str, Any]:
    manifest_path = source / ".forma-manifest.json"
    try:
        raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    return raw


def _blockers(
    verification_passed: bool,
    artifact_kind: str,
    forma_supported: bool,
) -> list[str]:
    blockers: list[str] = []
    if artifact_kind == "unsupported":
        blockers.append("path is not a supported Forma artifact")
    if not verification_passed:
        blockers.append("verification failed")
    if artifact_kind != "codex-plugin" and not forma_supported and artifact_kind != "unsupported":
        blockers.append("Forma install does not support this artifact kind")
    return blockers


def _install_route(source: Path, artifact_kind: str, target: str) -> str:
    if artifact_kind == "codex-plugin":
        return "codex-plugin"
    if artifact_kind == "claude-code-plugin":
        return "forma-install:claude-code"
    if artifact_kind in {"skill", "skill-bundle"}:
        if target == "unknown":
            return "forma-install"
        return f"forma-install:{target}"
    return "none"


def _next_steps(
    source: Path,
    artifact_kind: str,
    target: str,
    verification_passed: bool,
) -> list[str]:
    if artifact_kind == "unsupported":
        return [
            "Provide a local skill, skill bundle, Codex plugin artifact, or Claude Code plugin artifact.",
            f"Run `forma verify {source}` after fixing the artifact shape.",
        ]
    if not verification_passed:
        return [
            f"Run `forma verify {source}` and fix the reported errors.",
        ]
    if artifact_kind == "codex-plugin":
        plugin_name = codex_plugin_name(source)
        return [
            "Install through Codex marketplace/plugin UI, not `forma install`.",
            f"After marketplace registration, run `codex plugin add {plugin_name}@<marketplace-name>`.",
            "Start a new Codex thread after installation.",
        ]
    if artifact_kind == "claude-code-plugin":
        return [
            f"Run `forma install --target claude-code --scope user|project {source}`.",
        ]
    if artifact_kind in {"skill", "skill-bundle"}:
        target_hint = target if target != "unknown" else "codex|claude-code"
        return [
            f"Run `forma install --target {target_hint} --scope user|project {source}`.",
        ]
    return []
