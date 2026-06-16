"""Generated artifact drift checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from forma.adapters import build_creator
from forma.adopt import (
    ARTIFACT_BUNDLE,
    ARTIFACT_CLAUDE_CODE_PLUGIN,
    ARTIFACT_PLUGIN,
    PLUGIN_ARTIFACTS,
    _assert_base_origin,
    _generate_creator_baseline,
    _load_artifact_info,
)
from forma.creator import build_bundle
from forma.origin import normalized_payload_digest
from forma.plugins import build_plugin
from forma.reports import INTERACTION_CHOICE, NextAction
from forma_verifier import verify


DRIFT_REPORT_SCHEMA = "forma.drift.report.v1"
STATUS_FRESH = "fresh"
STATUS_STALE = "stale"
STATUS_INVALID = "invalid"
STATUS_UNKNOWN_SOURCE = "unknown-source"


@dataclass(frozen=True)
class DriftArtifactResult:
    path: str
    status: str
    artifact_kind: str
    target: str
    source_kind: str
    message: str
    normalized_payload_digest: str | None = None
    regenerated_payload_digest: str | None = None
    base_origin_status: str | None = None

    def to_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "path": self.path,
            "status": self.status,
            "artifact_kind": self.artifact_kind,
            "target": self.target,
            "source_kind": self.source_kind,
            "message": self.message,
        }
        if self.normalized_payload_digest is not None:
            result["normalized_payload_digest"] = self.normalized_payload_digest
        if self.regenerated_payload_digest is not None:
            result["regenerated_payload_digest"] = self.regenerated_payload_digest
        if self.base_origin_status is not None:
            result["base_origin_status"] = self.base_origin_status
        return result


@dataclass(frozen=True)
class DriftReport:
    artifacts: tuple[DriftArtifactResult, ...]

    @property
    def status(self) -> str:
        statuses = {artifact.status for artifact in self.artifacts}
        if STATUS_INVALID in statuses:
            return STATUS_INVALID
        if STATUS_STALE in statuses:
            return STATUS_STALE
        if STATUS_UNKNOWN_SOURCE in statuses:
            return STATUS_UNKNOWN_SOURCE
        return STATUS_FRESH

    def to_dict(self) -> dict[str, object]:
        return {
            "schema": DRIFT_REPORT_SCHEMA,
            "status": self.status,
            "artifacts": [artifact.to_dict() for artifact in self.artifacts],
            "next_actions": [action.to_dict() for action in self.next_actions],
        }

    def format_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    @property
    def next_actions(self) -> tuple[NextAction, ...]:
        if self.status == STATUS_FRESH:
            return (
                NextAction(
                    title="no drift remediation required",
                    description=(
                        "The checked artifact is fresh; if the user asked for "
                        "semantic profile coverage, run doctor/profile review "
                        "instead of treating drift as that proof."
                    ),
                ),
            )
        if self.status == STATUS_STALE:
            return (
                NextAction(
                    title="regenerate stale artifact",
                    description=(
                        "Regenerate the artifact from its approved source, run "
                        "`forma verify`, then ask whether the user wants the "
                        "fresh artifact installed, committed, or published."
                    ),
                    requires_confirmation=True,
                    confirmation_prompt="Should I regenerate and verify the stale artifact now?",
                    interaction=INTERACTION_CHOICE,
                ),
            )
        if self.status == STATUS_UNKNOWN_SOURCE:
            return (
                NextAction(
                    title="provide source for full drift proof",
                    description=(
                        "Rerun drift with `--profile` or `--creator-source`, "
                        "or ask the user for the owning source before making a "
                        "fresh/stale claim."
                    ),
                    requires_confirmation=True,
                    confirmation_prompt="Should I rerun drift with the owning source now?",
                    interaction=INTERACTION_CHOICE,
                ),
            )
        return (
            NextAction(
                title="fix invalid artifact before drift",
                description=(
                    "Resolve verifier or manifest errors, rerun `forma verify`, "
                    "then rerun `forma drift` and offer to apply the next concrete fix."
                ),
                requires_confirmation=True,
                confirmation_prompt="Should I inspect and fix the invalid artifact now?",
                interaction=INTERACTION_CHOICE,
            ),
        )

    def format_human(self) -> str:
        lines = [f"forma drift: {self.status}"]
        for artifact in self.artifacts:
            source = f" source={artifact.source_kind}"
            base = (
                f" base_origin={artifact.base_origin_status}"
                if artifact.base_origin_status
                else ""
            )
            lines.append(
                f"  {artifact.status}: {artifact.path}"
                f" ({artifact.artifact_kind}, target={artifact.target}{source}{base})"
            )
            if artifact.message:
                lines.append(f"    {artifact.message}")
        lines.append("")
        lines.append("Next:")
        for action in self.next_actions:
            lines.append(f"  - {action.title}: {action.description}")
            if action.requires_confirmation and action.confirmation_prompt:
                lines.append(f"    confirmation: {action.confirmation_prompt}")
        return "\n".join(lines)


def drift_artifact(
    artifact_path: Path,
    profile_file: Path | None = None,
    creator_source: Path | None = None,
) -> DriftReport:
    """Check one artifact for drift."""
    if profile_file is not None and creator_source is not None:
        raise ValueError("use either --profile or --creator-source, not both")
    if profile_file is not None:
        result = _drift_with_profile(artifact_path, profile_file)
    elif creator_source is not None:
        result = _drift_with_creator_source(artifact_path, creator_source)
    else:
        result = _drift_without_source(artifact_path)
    return DriftReport((result,))


def drift_release_surface(root: Path) -> DriftReport:
    """Check Forma's active committed dist release surface.

    Product-level forma-creator bundles are intentionally deferred from this
    fixed check until the creator path is isolated and resumed.
    """
    root = root.resolve()
    results = [
        _drift_with_creator_source(
            root / "dist/skill-bundles/codex",
            root / "source/skill-creator",
        ),
        _drift_with_creator_source(
            root / "dist/skill-bundles/claude-code",
            root / "source/skill-creator",
        ),
        _drift_with_creator_source(
            root / "dist/skill-bundles/opencode",
            root / "source/skill-creator",
        ),
        _drift_with_creator_source(
            root / "dist/plugins/codex/forma",
            root / "source/skill-creator",
        ),
        _drift_with_creator_source(
            root / "dist/plugins/claude-code/forma",
            root / "source/skill-creator",
        ),
    ]
    return DriftReport(tuple(results))


def _drift_with_profile(artifact_path: Path, profile_file: Path) -> DriftArtifactResult:
    artifact = artifact_path.resolve()
    try:
        info = _load_artifact_info(artifact)
        _assert_verify_passes(artifact)
        with tempfile.TemporaryDirectory(prefix="forma-drift-") as temp_root_text:
            regenerated = Path(temp_root_text) / "regenerated"
            if info.artifact_kind in PLUGIN_ARTIFACTS:
                build_plugin(profile_file, regenerated, info.target)
            else:
                build_bundle(profile_file, regenerated, info.target)
            return _compare_payloads(
                artifact=artifact,
                regenerated=regenerated,
                artifact_kind=info.artifact_kind,
                target=info.target,
                source_kind="profile",
            )
    except Exception as exc:
        return _invalid_result(artifact, "profile", str(exc))


def _drift_with_creator_source(
    artifact_path: Path,
    creator_source: Path,
) -> DriftArtifactResult:
    artifact = artifact_path.resolve()
    try:
        manifest = _load_manifest(artifact)
        target = _manifest_target(manifest)
        _assert_verify_passes(artifact)
        if manifest.get("format") == "forma-creator-manifest-v1":
            with tempfile.TemporaryDirectory(prefix="forma-drift-") as temp_root_text:
                regenerated = build_creator(
                    creator_source,
                    Path(temp_root_text) / "creator",
                    target,
                )
                return _compare_payloads(
                    artifact=artifact,
                    regenerated=regenerated,
                    artifact_kind="creator",
                    target=target,
                    source_kind="creator-source",
                )
        info = _load_artifact_info(artifact)
        with tempfile.TemporaryDirectory(prefix="forma-drift-") as temp_root_text:
            baseline = _generate_creator_baseline_from_source(
                output_dir=Path(temp_root_text) / "baseline",
                creator_source=creator_source,
                target=info.target,
                artifact_kind=info.artifact_kind,
            )
            artifact_digest = normalized_payload_digest(artifact)
            baseline_digest = normalized_payload_digest(baseline)
            if artifact_digest == baseline_digest:
                status = STATUS_FRESH
                message = "artifact matches the no-injection creator output"
            else:
                base_status = _base_origin_status(info, baseline_digest)
                if base_status == STATUS_FRESH:
                    status = STATUS_UNKNOWN_SOURCE
                    message = (
                        "Forma creator provenance is fresh, but injected/profile "
                        "source is required for full drift proof"
                    )
                else:
                    status = STATUS_STALE
                    message = "creator base origin is stale"
                return DriftArtifactResult(
                    path=str(artifact),
                    status=status,
                    artifact_kind=info.artifact_kind,
                    target=info.target,
                    source_kind="creator-source",
                    message=message,
                    normalized_payload_digest=artifact_digest,
                    regenerated_payload_digest=baseline_digest,
                    base_origin_status=base_status,
                )
            return DriftArtifactResult(
                path=str(artifact),
                status=status,
                artifact_kind=info.artifact_kind,
                target=info.target,
                source_kind="creator-source",
                message=message,
                normalized_payload_digest=artifact_digest,
                regenerated_payload_digest=baseline_digest,
            )
    except Exception as exc:
        return _invalid_result(artifact, "creator-source", str(exc))


def _drift_without_source(artifact_path: Path) -> DriftArtifactResult:
    artifact = artifact_path.resolve()
    try:
        manifest = _load_manifest(artifact)
        target = _manifest_target(manifest)
        _assert_verify_passes(artifact)
        if manifest.get("format") == "forma-creator-manifest-v1":
            return DriftArtifactResult(
                path=str(artifact),
                status=STATUS_UNKNOWN_SOURCE,
                artifact_kind="creator",
                target=target,
                source_kind="none",
                message="creator source is required for full drift proof",
                normalized_payload_digest=normalized_payload_digest(artifact),
            )
        info = _load_artifact_info(artifact)
        base_status = _current_base_origin_status(info)
        return DriftArtifactResult(
            path=str(artifact),
            status=STATUS_UNKNOWN_SOURCE,
            artifact_kind=info.artifact_kind,
            target=info.target,
            source_kind="none",
            message="profile or creator source is required for full drift proof",
            normalized_payload_digest=normalized_payload_digest(artifact),
            base_origin_status=base_status,
        )
    except Exception as exc:
        return _invalid_result(artifact, "none", str(exc))


def _compare_payloads(
    artifact: Path,
    regenerated: Path,
    artifact_kind: str,
    target: str,
    source_kind: str,
) -> DriftArtifactResult:
    artifact_digest = normalized_payload_digest(artifact)
    regenerated_digest = normalized_payload_digest(regenerated)
    status = STATUS_FRESH if artifact_digest == regenerated_digest else STATUS_STALE
    message = (
        "artifact matches regenerated output"
        if status == STATUS_FRESH
        else "artifact differs from regenerated output"
    )
    return DriftArtifactResult(
        path=str(artifact),
        status=status,
        artifact_kind=artifact_kind,
        target=target,
        source_kind=source_kind,
        message=message,
        normalized_payload_digest=artifact_digest,
        regenerated_payload_digest=regenerated_digest,
    )


def _generate_creator_baseline_from_source(
    output_dir: Path,
    creator_source: Path,
    target: str,
    artifact_kind: str,
) -> Path:
    with tempfile.TemporaryDirectory(prefix="forma-creator-") as creator_root_text:
        creator = build_creator(creator_source, Path(creator_root_text), target)
        args = [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(output_dir),
        ]
        if artifact_kind in PLUGIN_ARTIFACTS:
            args.extend(["--artifact", "plugin"])
        result = subprocess.run(
            args,
            text=True,
            capture_output=True,
            check=False,
        )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or result.stdout.strip())
    return output_dir


def _current_base_origin_status(info) -> str | None:
    try:
        with tempfile.TemporaryDirectory(prefix="forma-drift-") as temp_root_text:
            baseline = _generate_creator_baseline(
                Path(temp_root_text) / "baseline",
                info.target,
                info.artifact_kind,
            )
            return _base_origin_status(info, normalized_payload_digest(baseline))
    except Exception:
        return None


def _base_origin_status(info, baseline_digest: str) -> str:
    base_origin = _assert_base_origin(info)
    return (
        STATUS_FRESH
        if base_origin["base_output_digest"] == baseline_digest
        else STATUS_STALE
    )


def _assert_verify_passes(path: Path) -> None:
    report = verify(path)
    if not report.passed:
        raise ValueError(report.format_human())


def _invalid_result(path: Path, source_kind: str, message: str) -> DriftArtifactResult:
    manifest = _load_manifest(path)
    return DriftArtifactResult(
        path=str(path),
        status=STATUS_INVALID,
        artifact_kind=_manifest_artifact_kind(path, manifest),
        target=_safe_manifest_target(manifest),
        source_kind=source_kind,
        message=message,
    )


def _load_manifest(path: Path) -> Mapping[str, Any]:
    manifest_path = path / ".forma-manifest.json"
    if not manifest_path.is_file():
        return {}
    raw = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        return {}
    return raw


def _manifest_target(manifest: Mapping[str, Any]) -> str:
    target = manifest.get("target")
    if not isinstance(target, str) or not target.strip():
        raise ValueError("manifest.target is missing")
    if target not in {"codex", "claude-code", "opencode"}:
        raise ValueError(f"unsupported target: {target}")
    return target


def _safe_manifest_target(manifest: Mapping[str, Any]) -> str:
    target = manifest.get("target")
    if isinstance(target, str) and target.strip():
        return target.strip()
    return "unknown"


def _manifest_artifact_kind(path: Path, manifest: Mapping[str, Any]) -> str:
    if (path / ".codex-plugin" / "plugin.json").is_file():
        return ARTIFACT_PLUGIN
    if (path / ".claude-plugin" / "plugin.json").is_file():
        return ARTIFACT_CLAUDE_CODE_PLUGIN
    if manifest.get("format") == "forma-creator-manifest-v1":
        return "creator"
    return ARTIFACT_BUNDLE
