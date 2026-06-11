"""Build local plugin artifacts from Forma workflow bundles."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from forma.adapters.workflow import plugin_id, workflow_adapter
from forma.base_origin import creator_base_origin
from forma.creator import build_bundle
from forma.creator.manifest import methodology_dir_context
from forma.creator.profiles import load_profile
from forma_verifier import verify


def build_plugin(
    profile_file: Path,
    output_dir: Path,
    target_agent: str,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a target-specific plugin rooted at `output_dir` and return plugin.json."""
    adapter = workflow_adapter(target_agent)
    adapter.assert_plugin_supported()
    output_dir = output_dir.resolve()
    _prepare_plugin_output_dir(output_dir)
    skills_dir = output_dir / "skills"
    manifest_path = build_bundle(
        profile_file=profile_file,
        output_dir=skills_dir,
        target_agent=target_agent,
        methodology_dir=methodology_dir,
    )
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest_path.unlink()
    profile = load_profile(profile_file)
    plugin_name = plugin_id(profile.bundle_name)
    manifest = adapter.localize_plugin_skills(
        manifest=manifest,
        skills_dir=skills_dir,
        plugin_name=plugin_name,
    )
    plugin_dir = output_dir / adapter.plugin_dir_name()
    plugin_dir.mkdir(parents=True, exist_ok=True)
    plugin_json = plugin_dir / "plugin.json"
    plugin_json.write_text(
        json.dumps(
            adapter.plugin_manifest(profile, manifest, skills_dir),
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    with methodology_dir_context(methodology_dir) as resolved_methodology_dir:
        base_origin = creator_base_origin(
            target_agent,
            adapter.plugin_artifact_kind(),
            methodology_dir=resolved_methodology_dir,
        )
    manifest_with_origin = dict(manifest)
    manifest_with_origin["base_origin"] = base_origin
    (output_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest_with_origin, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    report = verify(output_dir)
    if not report.passed:
        raise ValueError(report.format_human())
    return plugin_json


def build_codex_plugin(
    profile_file: Path,
    output_dir: Path,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a Codex plugin rooted at `output_dir` and return plugin.json."""
    return build_plugin(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=methodology_dir,
    )


def build_claude_code_plugin(
    profile_file: Path,
    output_dir: Path,
    methodology_dir: Path | None = None,
) -> Path:
    """Build a Claude Code plugin rooted at `output_dir` and return plugin.json."""
    return build_plugin(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="claude-code",
        methodology_dir=methodology_dir,
    )


def _prepare_plugin_output_dir(output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    allowed = {".codex-plugin", ".claude-plugin", ".forma-manifest.json", "skills"}
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
    for child in (
        output_dir / ".codex-plugin",
        output_dir / ".claude-plugin",
        output_dir / "skills",
    ):
        if child.exists():
            shutil.rmtree(child)
    manifest_path = output_dir / ".forma-manifest.json"
    if manifest_path.exists():
        manifest_path.unlink()
