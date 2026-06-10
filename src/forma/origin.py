"""Normalized output provenance helpers."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Mapping


BASE_ORIGIN_SCHEMA = "forma.base-origin.v1"
NORMALIZATION_ID = "forma.normalized-output.v1"
MANIFEST_NAME = ".forma-manifest.json"
LOCAL_ADOPTION_REPORTS = frozenset({"adoption-report.json"})


def normalized_payload_file_hashes(root: Path) -> dict[str, str]:
    """Return stable file hashes for runtime payload files under `root`."""
    root = root.resolve()
    hashes: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if _excluded_payload_path(rel):
            continue
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def normalized_payload_digest(root: Path) -> str:
    """Return the normalized digest for runtime payload files under `root`."""
    payload = json.dumps(
        normalized_payload_file_hashes(root),
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_base_origin(root: Path, target: str, artifact_kind: str) -> dict[str, str]:
    """Build same-origin metadata for a normalized runtime payload."""
    return {
        "schema": BASE_ORIGIN_SCHEMA,
        "target": target,
        "artifact_kind": artifact_kind,
        "normalization_id": NORMALIZATION_ID,
        "base_output_digest": normalized_payload_digest(root),
    }


def manifest_with_base_origin(
    manifest: Mapping[str, object],
    root: Path,
    target: str,
    artifact_kind: str,
) -> dict[str, object]:
    """Return a manifest copy with `base_origin` computed from `root`."""
    result = dict(manifest)
    result["base_origin"] = build_base_origin(root, target, artifact_kind)
    return result


def _excluded_payload_path(rel: str) -> bool:
    return rel == MANIFEST_NAME or rel in LOCAL_ADOPTION_REPORTS
