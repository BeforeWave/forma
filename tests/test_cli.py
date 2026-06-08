from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner

from forma.cli import main


ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = ROOT / "source" / "methodology"
FORMA_SELF_PROFILE = ROOT / "profiles" / "forma-self" / "forma-self-iteration.yaml"
SAMPLE_PROFILE = (
    ROOT
    / "examples"
    / "profiles"
    / "sample-backend"
    / "sample-backend-go-github-issue-tracked.yaml"
)


def test_create_bundle_default_profile_emits_forma_workflow(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "create-bundle",
            "--target",
            "codex",
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output / "forma-plan" / "SKILL.md").is_file()
    assert (output / "forma-showhand" / "SKILL.md").is_file()
    assert not (output / "shape").exists()
    manifest = json.loads((output / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["format"] == "forma-bundle-manifest-v1"
    assert manifest["bundle_kind"] == "plan-first-workflow"
    assert manifest["emitted_skills"]["shape"]["name"] == "forma-plan"


def test_create_plugin_emits_codex_plugin_layout(tmp_path: Path) -> None:
    output = tmp_path / "plugin"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Codex plugin generated, not installed." in result.output
    assert "name: forma" in result.output
    assert "root:" in result.output
    assert "Install with Codex:" in result.output
    assert "codex plugin marketplace list" in result.output
    assert "developers.openai.com/codex/plugins/build#install-a-local-plugin-manually" in result.output
    assert "developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli" in result.output
    assert "codex plugin add forma@<marketplace-name>" in result.output
    assert "Codex plugin UI" in result.output
    assert "Start a new Codex thread" in result.output
    assert "Forma does not install Codex plugins" in result.output
    assert (output / ".codex-plugin" / "plugin.json").is_file()
    assert (output / ".forma-manifest.json").is_file()
    assert (output / "skills" / "forma-plan" / "SKILL.md").is_file()
    assert (output / "skills" / "forma-showhand" / "SKILL.md").is_file()
    assert not (output / "skill-bundles").exists()
    assert not (output / "skills" / ".forma-manifest.json").exists()
    plugin = json.loads(
        (output / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert plugin["id"] == "forma"
    assert plugin["name"] == "forma"
    assert plugin["interface"]["displayName"] == "Forma"
    assert plugin["skills"] == "./skills/"


def test_create_plugin_with_forma_self_profile_uses_emitted_skills(
    tmp_path: Path,
) -> None:
    output = tmp_path / "plugin"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(FORMA_SELF_PROFILE),
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (output / "skills" / "forma-plan" / "SKILL.md").is_file()
    assert (output / "skills" / "forma-showhand" / "SKILL.md").is_file()
    plugin = json.loads(
        (output / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert plugin["id"] == "forma"
    assert plugin["name"] == "forma"
    assert plugin["skills"] == "./skills/"


def test_create_plugin_rejects_claude_code_target(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "claude-code",
            "--output",
            str(tmp_path / "plugin"),
        ],
    )

    assert result.exit_code != 0
    assert "only --target codex" in result.output


def test_install_codex_bundle_project_scope_and_replace(
    tmp_path: Path,
    monkeypatch,
) -> None:
    bundle = tmp_path / "bundle"
    project = tmp_path / "project"
    project.mkdir()
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-bundle",
            "--target",
            "codex",
            "--output",
            str(bundle),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    assert create.exit_code == 0, create.output

    monkeypatch.chdir(project)
    install = runner.invoke(
        main,
        ["install", "--target", "codex", "--scope", "project", str(bundle)],
    )
    assert install.exit_code == 0, install.output
    assert (project / ".codex" / "skills" / "forma-plan").is_dir()
    assert (project / ".codex" / "skills" / "forma-showhand").is_dir()

    conflict = runner.invoke(
        main,
        ["install", "--target", "codex", "--scope", "project", str(bundle)],
    )
    assert conflict.exit_code != 0
    assert "--replace" in conflict.output

    replace = runner.invoke(
        main,
        [
            "install",
            "--target",
            "codex",
            "--scope",
            "project",
            "--replace",
            str(bundle),
        ],
    )
    assert replace.exit_code == 0, replace.output


def test_install_claude_code_bundle_project_scope(
    tmp_path: Path,
    monkeypatch,
) -> None:
    bundle = tmp_path / "bundle"
    project = tmp_path / "project"
    project.mkdir()
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-bundle",
            "--target",
            "claude-code",
            "--output",
            str(bundle),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    assert create.exit_code == 0, create.output

    monkeypatch.chdir(project)
    install = runner.invoke(
        main,
        ["install", "--target", "claude-code", "--scope", "project", str(bundle)],
    )
    assert install.exit_code == 0, install.output
    assert (project / ".claude" / "skills" / "forma-plan").is_dir()
    assert (project / ".claude" / "skills" / "forma-showhand").is_dir()


def test_install_rejects_codex_plugin_artifacts(tmp_path: Path, monkeypatch) -> None:
    plugin = tmp_path / "plugin"
    project = tmp_path / "project"
    project.mkdir()
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--output",
            str(plugin),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    assert create.exit_code == 0, create.output

    monkeypatch.chdir(project)
    install = runner.invoke(
        main,
        ["install", "--target", "codex", "--scope", "project", str(plugin)],
    )

    assert install.exit_code != 0
    assert "forma install does not install Codex plugin artifacts" in install.output
    assert "Codex plugin generated, not installed." in install.output
    assert "name: forma" in install.output
    assert "root:" in install.output
    assert "Install with Codex:" in install.output
    assert "codex plugin marketplace list" in install.output
    assert "developers.openai.com/codex/plugins/build#install-a-local-plugin-manually" in install.output
    assert "developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli" in install.output
    assert "codex plugin add forma@<marketplace-name>" in install.output
    assert "Codex plugin UI" in install.output
    assert "Start a new Codex thread" in install.output
    assert "Forma does not install Codex plugins" in install.output
    assert not (project / ".codex" / "plugins").exists()


def test_install_rejects_profile_named_codex_plugin(
    tmp_path: Path,
    monkeypatch,
) -> None:
    plugin = tmp_path / "plugin"
    project = tmp_path / "project"
    project.mkdir()
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(SAMPLE_PROFILE),
            "--output",
            str(plugin),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    assert create.exit_code == 0, create.output

    monkeypatch.chdir(project)
    install = runner.invoke(
        main,
        ["install", "--target", "codex", "--scope", "project", str(plugin)],
    )

    assert install.exit_code != 0
    assert "forma install does not install Codex plugin artifacts" in install.output
    assert "name: sample-backend-go-github-issue-tracked" in install.output
    assert "codex plugin add sample-backend-go-github-issue-tracked@<marketplace-name>" in install.output
