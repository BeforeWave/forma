"""Build local Codex plugin artifacts from Forma workflow bundles."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Mapping

from forma.creator import build_bundle
from forma.creator.profiles import load_profile
from forma_verifier import verify


CODEX_PLUGIN_ID = "forma"
CODEX_PLUGIN_NAME = "Forma"
CODEX_PLUGIN_DESCRIPTION = (
    "Forma provides Plan-First workflow skills for grounded planning, locked task contracts, and evidence-backed execution."
)


def build_codex_plugin(
    profile_file: Path,
    output_dir: Path,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a Codex plugin rooted at `output_dir` and return plugin.json."""
    output_dir = output_dir.resolve()
    _prepare_plugin_output_dir(output_dir)
    skills_dir = output_dir / "skills"
    manifest_path = build_bundle(
        profile_file=profile_file,
        output_dir=skills_dir,
        target_agent="codex",
        methodology_dir=methodology_dir,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path.unlink()
    (output_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    plugin_dir = output_dir / ".codex-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    profile = load_profile(profile_file)
    plugin_json = plugin_dir / "plugin.json"
    plugin_json.write_text(
        json.dumps(
            _plugin_manifest(profile.skill_descriptions),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    report = verify(output_dir)
    if not report.passed:
        raise ValueError(report.format_human())
    return plugin_json


def _prepare_plugin_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed = {".codex-plugin", ".forma-manifest.json", "skills"}
    unexpected = [
        path.name
        for path in output_dir.iterdir()
        if path.name not in allowed
    ]
    if unexpected:
        unexpected_list = ", ".join(sorted(unexpected))
        raise ValueError(
            f"output directory contains non-Forma files: {unexpected_list}; "
            "choose an empty directory or remove those files"
        )
    for child in (output_dir / ".codex-plugin", output_dir / "skills"):
        if child.exists():
            shutil.rmtree(child)
    manifest_path = output_dir / ".forma-manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()


def _plugin_manifest(skill_descriptions: Mapping[str, str]) -> dict[str, object]:
    stage_ids = {
        "shape": "forma-plan",
        "gauge": "forma-ground",
        "seal": "forma-lock",
        "pour": "forma-execute",
        "flow": "forma-showhand",
    }
    skills = [
        {
            "id": skill_id,
            "description": skill_descriptions.get(kind, ""),
        }
        for kind, skill_id in stage_ids.items()
    ]
    return {
        "id": CODEX_PLUGIN_ID,
        "name": CODEX_PLUGIN_NAME,
        "description": CODEX_PLUGIN_DESCRIPTION,
        "skills": skills,
    }
