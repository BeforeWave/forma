"""Methodology lookup and provenance manifest helpers."""

from __future__ import annotations

import json
import hashlib
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Mapping, Sequence

from forma import __version__
from forma.creator.composer import (
    KINDS,
    METHODOLOGY_REQUIREMENT_REFERENCES,
    METHODOLOGY_RESOURCES,
    STAGE_SOURCE_DIR,
)
from forma.creator.profiles import ConditionalOverlays, ConditionalRoute, ProfileConfig, ResourceSpec


METHODOLOGY_VERSION = "0.1.0"


def find_methodology_dir(methodology_dir: Path | None = None) -> Path:
    """Resolve the canonical methodology source directory.

    In editable development installs, `src/forma/...` lives under the repository
    root. Walk upward from this module and from cwd to find `source/methodology`.
    A packaged non-editable Mode-O source layout is deferred to issue-3, so v1
    intentionally keeps this lookup simple and explicit.
    """
    if methodology_dir is not None:
        path = methodology_dir.resolve()
        _assert_methodology_dir(path)
        return path
    candidates: List[Path] = []
    for base in [Path(__file__).resolve(), Path.cwd().resolve()]:
        candidates.extend(parent / "source" / "methodology" for parent in base.parents)
    seen: set[Path] = set()
    for candidate in candidates:
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate.is_dir():
            _assert_methodology_dir(candidate)
            return candidate
    raise ValueError(
        "could not auto-detect source/methodology; pass --methodology <path>"
    )


def build_manifest(
    methodology_dir: Path,
    profile: ProfileConfig,
    target_agent: str,
) -> Dict[str, object]:
    """Build provenance metadata for generated suites."""
    methodology_hashes = _file_hashes(methodology_dir)
    profile_hashes = _file_hashes_for_paths(profile.profile_root, profile.resolved_paths)
    methodology_tree_digest = _tree_digest(methodology_hashes)
    profile_digest = _tree_digest(profile_hashes)
    resource_hashes = _resource_hashes(profile.resources, profile.conditional_overlays)
    emitted_skills = {
        kind: {
            "name": stage.name,
            "directory": stage.directory,
            "display_name": stage.display_name,
        }
        for kind, stage in profile.stages.items()
        if stage.enabled
    }
    manifest: Dict[str, object] = {
        "format": "forma-suite-manifest-v1",
        "mode": "solo",
        "suite_kind": "plan-first",
        "target": target_agent,
        "methodology_version": METHODOLOGY_VERSION,
        "methodology_source_revision": _git_short_sha(methodology_dir),
        "methodology_source_revision_type": "git-short-sha",
        "methodology_tree_digest": methodology_tree_digest,
        "generator_version": __version__,
        "generated_at": _generated_at(),
        "profile": {
            "top_level_id": profile.profile_id,
            "top_level_path": profile.top_level_path,
            "resolved_order": list(profile.resolved_order),
            "file_hashes": profile_hashes,
            "digest": profile_digest,
            "resource_hashes": resource_hashes,
            "resource_digest": _tree_digest(resource_hashes),
            "bundle_name": profile.bundle_name,
            "org_name": profile.org_name,
        },
        "skills": list(emitted_skills),
        "emitted_skills": emitted_skills,
    }
    if profile.conditional_overlays is not None:
        manifest["conditional_overlays"] = _conditional_manifest(
            profile.conditional_overlays
        )
    return manifest


def _assert_methodology_dir(path: Path) -> None:
    required = [f"{STAGE_SOURCE_DIR}/{kind}.md" for kind in KINDS]
    required.extend(
        source_rel
        for kind in KINDS
        for source_rel, _dest, _executable in METHODOLOGY_RESOURCES[kind]
    )
    required.extend(
        spec.source_rel
        for kind in KINDS
        for spec in METHODOLOGY_REQUIREMENT_REFERENCES[kind]
    )
    missing = [rel for rel in required if not (path / rel).is_file()]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"invalid methodology directory: missing {missing_list}")


def _file_hashes(root: Path) -> Dict[str, str]:
    root = root.resolve()
    hashes: Dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        hashes[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return hashes


def _file_hashes_for_paths(root: Path, paths: Sequence[Path]) -> Dict[str, str]:
    root = root.resolve()
    hashes: Dict[str, str] = {}
    for path in sorted(path.resolve() for path in paths):
        rel = path.relative_to(root).as_posix()
        hashes[rel] = _sha256(path)
    return hashes


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tree_digest(file_hashes: Mapping[str, str]) -> str:
    payload = json.dumps(file_hashes, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _resource_hashes(
    resources: Mapping[str, Sequence[ResourceSpec]],
    conditional_overlays: ConditionalOverlays | None = None,
) -> Dict[str, str]:
    hashes: Dict[str, str] = {}
    for kind, specs in sorted(resources.items()):
        for spec in specs:
            key = f"{kind}:{spec.dest}"
            hashes[key] = _resource_digest(spec)
    if conditional_overlays is not None:
        for overlay_id, overlay in sorted(conditional_overlays.overlays.items()):
            for kind, specs in sorted(overlay.resources.items()):
                for spec in specs:
                    key = f"conditional:{overlay_id}:{kind}:{spec.dest}"
                    hashes[key] = _resource_digest(spec)
    return hashes


def _resource_digest(spec: ResourceSpec) -> str:
    if spec.content is None:
        return _sha256(spec.source)
    payload = spec.content.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _conditional_manifest(
    conditional_overlays: ConditionalOverlays,
) -> Dict[str, object]:
    return {
        "decision": {
            "name": conditional_overlays.decision.name,
            "must_record_in_plan": conditional_overlays.decision.must_record_in_plan,
            "missing_during_execution": conditional_overlays.decision.missing_during_execution,
        },
        "routes": [
            {
                "id": route.id,
                "description": route.description,
                "overlays": list(route.overlays),
                "references": {
                    kind: refs
                    for kind in KINDS
                    if (refs := _conditional_route_reference_paths(kind, route, conditional_overlays))
                },
            }
            for route in conditional_overlays.routes
        ],
        "overlays": {
            overlay_id: {
                "description": overlay.description,
                "constraints": {
                    stage: list(items)
                    for stage, items in sorted(overlay.constraints.items())
                },
                "resources": {
                    stage: [resource.dest for resource in resources]
                    for stage, resources in sorted(overlay.resources.items())
                },
                "validation_commands": {
                    stage: list(items)
                    for stage, items in sorted(overlay.validation_commands.items())
                },
            }
            for overlay_id, overlay in sorted(conditional_overlays.overlays.items())
        },
    }


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


def _git_short_sha(path: Path) -> str:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--short", "HEAD"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return "unknown"
    return result.stdout.strip() or "unknown"


def _generated_at() -> str:
    forced = os.environ.get("FORMA_GENERATED_AT")
    if forced:
        return forced
    return datetime.now(timezone.utc).replace(microsecond=0).strftime(
        "%Y-%m-%dT%H:%M:%SZ"
    )
