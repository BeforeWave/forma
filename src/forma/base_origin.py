"""Same-origin base skeleton provenance helpers."""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from forma.origin import (
    BASE_ORIGIN_SCHEMA,
    NORMALIZATION_ID,
    normalized_payload_digest,
)


def creator_base_origin(
    target_agent: str,
    artifact_kind: str,
    methodology_dir: Path | None = None,
    creator_source_dir: Path | None = None,
) -> dict[str, str]:
    """Return the no-injection creator baseline origin for an artifact kind."""
    digest = _creator_baseline_digest(
        target_agent=target_agent,
        artifact_kind=artifact_kind,
        methodology_dir=methodology_dir,
        creator_source_dir=creator_source_dir,
    )
    return {
        "schema": BASE_ORIGIN_SCHEMA,
        "target": target_agent,
        "artifact_kind": artifact_kind,
        "normalization_id": NORMALIZATION_ID,
        "base_output_digest": digest,
    }


def _creator_baseline_digest(
    target_agent: str,
    artifact_kind: str,
    methodology_dir: Path | None,
    creator_source_dir: Path | None,
) -> str:
    if artifact_kind not in {"skill-bundle", "codex-plugin", "claude-code-plugin"}:
        raise ValueError(f"unsupported artifact kind for base origin: {artifact_kind}")
    if artifact_kind == "codex-plugin" and target_agent != "codex":
        raise ValueError("Codex plugin base origin requires target codex")
    if artifact_kind == "claude-code-plugin" and target_agent != "claude-code":
        raise ValueError("Claude Code plugin base origin requires target claude-code")

    from forma.adapters import build_creator

    with tempfile.TemporaryDirectory(prefix="forma-base-origin-") as temp_root_text:
        root = Path(temp_root_text)
        creator = build_creator(creator_source_dir, root / "creator", target_agent)
        baseline = root / "baseline"
        args = [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(baseline),
            "--artifact",
            "plugin"
            if artifact_kind in {"codex-plugin", "claude-code-plugin"}
            else "bundle",
        ]
        if methodology_dir is not None:
            args.extend(["--methodology", str(methodology_dir)])
        result = subprocess.run(
            args,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            raise ValueError(result.stderr.strip() or result.stdout.strip())
        return normalized_payload_digest(baseline)
