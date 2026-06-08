"""Install verified local Forma artifacts into agent skill/plugin roots."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

from forma_verifier import verify
from forma_verifier.rules import parse_frontmatter


InstallTarget = Literal["codex", "claude-code"]
InstallScope = Literal["user", "project"]


@dataclass(frozen=True)
class InstallResult:
    artifact_kind: str
    installed_paths: tuple[Path, ...]


def install_artifact(
    source: Path,
    target_agent: InstallTarget,
    scope: InstallScope,
    replace: bool = False,
) -> InstallResult:
    """Install a verified local artifact and return installed destination paths."""
    source = source.resolve()
    artifact_kind = _classify_artifact(source)
    if artifact_kind == "codex-plugin":
        if target_agent != "codex":
            raise ValueError("Codex plugins can only be installed with --target codex")
        _verify_source(source)
        plugin_id = _plugin_id(source)
        destination = _plugin_root(target_agent, scope) / plugin_id
        _copy_targets([(source, destination)], replace)
        return InstallResult(artifact_kind, (destination,))
    if artifact_kind == "skill":
        _verify_source(source)
        name = _skill_name(source)
        destination = _skills_root(target_agent, scope) / name
        _copy_targets([(source, destination)], replace)
        return InstallResult(artifact_kind, (destination,))
    if artifact_kind == "skill-bundle":
        _verify_source(source)
        targets = [
            (skill_dir, _skills_root(target_agent, scope) / _skill_name(skill_dir))
            for skill_dir in _bundle_skill_dirs(source)
        ]
        _copy_targets(targets, replace)
        return InstallResult(
            artifact_kind,
            tuple(destination for _source, destination in targets),
        )
    raise ValueError(f"unsupported local Forma artifact: {source}")


def _classify_artifact(source: Path) -> str:
    if (source / ".codex-plugin" / "plugin.json").is_file():
        return "codex-plugin"
    if (source / "SKILL.md").is_file():
        return "skill"
    if _bundle_skill_dirs(source):
        return "skill-bundle"
    raise ValueError(
        "path is not a supported Forma artifact: expected a skill, skill bundle, or Codex plugin"
    )


def _verify_source(source: Path) -> None:
    report = verify(source)
    if not report.passed:
        raise ValueError(report.format_human())


def _bundle_skill_dirs(source: Path) -> list[Path]:
    return sorted(
        path
        for path in source.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )


def _skill_name(skill_dir: Path) -> str:
    text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, _body = parse_frontmatter(text)
    name = frontmatter.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{skill_dir}/SKILL.md has no frontmatter name")
    return name.strip()


def _plugin_id(plugin_root: Path) -> str:
    raw = json.loads(
        (plugin_root / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    if not isinstance(raw, dict):
        raise ValueError("plugin.json must contain an object")
    plugin_id = raw.get("name", raw.get("id"))
    if not isinstance(plugin_id, str) or not plugin_id.strip():
        raise ValueError("plugin.json must include non-empty name")
    return plugin_id.strip()


def _skills_root(target_agent: InstallTarget, scope: InstallScope) -> Path:
    if target_agent == "codex":
        root = Path.home() / ".codex" / "skills" if scope == "user" else Path.cwd() / ".codex" / "skills"
        return root
    if target_agent == "claude-code":
        root = Path.home() / ".claude" / "skills" if scope == "user" else Path.cwd() / ".claude" / "skills"
        return root
    raise ValueError(f"unsupported install target: {target_agent}")


def _plugin_root(target_agent: InstallTarget, scope: InstallScope) -> Path:
    if target_agent != "codex":
        raise ValueError("plugin install roots are only supported for Codex")
    return Path.home() / ".codex" / "plugins" if scope == "user" else Path.cwd() / ".codex" / "plugins"


def _copy_targets(targets: Iterable[tuple[Path, Path]], replace: bool) -> None:
    targets = tuple(targets)
    conflicts = [destination for _source, destination in targets if destination.exists()]
    if conflicts and not replace:
        names = ", ".join(str(path) for path in conflicts)
        raise ValueError(f"install target already exists; pass --replace to overwrite: {names}")
    for _source, destination in targets:
        if destination.exists():
            shutil.rmtree(destination)
    for source, destination in targets:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination)
