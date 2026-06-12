from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import yaml
from click.testing import CliRunner

from forma.adapters import build_creator
from forma.cli import main
from forma.origin import normalized_payload_digest


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
INVALID_BUNDLE = ROOT / "tests" / "fixtures" / "invalid-bundle"
META_SOURCE = ROOT / "source" / "skill-creator"


def _creator_artifact(
    tmp_path: Path,
    target: str = "codex",
    artifact: str = "bundle",
    injection: dict[str, object] | None = None,
) -> Path:
    creator = build_creator(META_SOURCE, tmp_path / f"creator-{target}", target)
    output = tmp_path / f"generated-{target}-{artifact}"
    args = [
        sys.executable,
        str(creator / "scripts" / "create.py"),
        "--output",
        str(output),
    ]
    if artifact == "plugin":
        args.extend(["--artifact", "plugin"])
    if injection:
        injection_path = tmp_path / f"{target}-{artifact}-injection.json"
        injection_path.write_text(json.dumps(injection, indent=2), encoding="utf-8")
        args.extend(["--injection-json", str(injection_path)])
    result = subprocess.run(args, text=True, capture_output=True, check=False)
    assert result.returncode == 0, result.stderr + result.stdout
    return output


def _write_minimal_claude_plugin(root: Path, name: str = "sample-plugin") -> Path:
    plugin_dir = root / ".claude-plugin"
    skill_dir = root / "skills" / "plan"
    plugin_dir.mkdir(parents=True)
    skill_dir.mkdir(parents=True)
    (plugin_dir / "plugin.json").write_text(
        json.dumps(
            {
                "name": name,
                "version": "1.0.0",
                "description": "Reusable sample workflow.",
                "skills": "./skills/",
            }
        ),
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        """---
name: plan
description: Plan a sample task.
---

## Workflow

Plan the sample task.
""",
        encoding="utf-8",
    )
    return root


def _assert_profile_drift_fresh(
    runner: CliRunner,
    artifact: Path,
    profile_file: Path,
) -> None:
    result = runner.invoke(
        main,
        [
            "drift",
            str(artifact),
            "--profile",
            str(profile_file),
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["status"] == "fresh"
    assert data["artifacts"][0]["message"] == "artifact matches regenerated output"


def test_root_help_guides_agents_and_no_args_exits_zero() -> None:
    runner = CliRunner()

    no_args = runner.invoke(main, [])
    help_result = runner.invoke(main, ["--help"])
    short_help = runner.invoke(main, ["-h"])

    for result in (no_args, help_result, short_help):
        assert result.exit_code == 0, result.output
        assert "Agents:" in result.output
        assert "forma explain agent" in result.output
        assert "forma explain agent --target codex" in result.output
        assert "forma explain agent --target claude-code" in result.output
        assert "forma explain agent --target opencode" in result.output


def test_command_help_includes_agent_next_steps() -> None:
    runner = CliRunner()
    cases = [
        (
            ["build-creator", "--help"],
            [
                "Use this when a user specifically wants an on-the-spot creator run",
                "Verify the generated creator skill:",
                "forma install --target codex|claude-code|opencode --scope user|project <creator-path>",
            ],
        ),
        (
            ["create-bundle", "--help"],
            [
                "Compile project rules into a target-specific skill bundle.",
                "Verify before installing:",
                "forma install --target codex|claude-code|opencode --scope user|project <output-dir>",
            ],
        ),
        (
            ["create-plugin", "--help"],
            [
                "Compile project rules into a target-specific plugin source.",
                "Verify the plugin source:",
                "ask the user which marketplace to use",
                "codex plugin add <plugin-id>@<marketplace-name>",
                "Do not install Codex plugins with forma install.",
                "Install Claude Code plugin roots with forma install --target claude-code.",
            ],
        ),
        (
            ["install", "--help"],
            [
                "Install only verified local skills, skill bundles, or Claude Code plugin roots.",
                "Do not pass URLs.",
                "Do not pass Codex plugin sources; install plugins through Codex.",
            ],
        ),
        (
            ["verify", "--help"],
            [
                "Verify a generated Forma workflow output at PATH.",
                "If verification passes for a skill bundle or Claude Code plugin source, install it with:",
                "If verification passes for a Codex plugin source, install it through Codex.",
            ],
        ),
        (
            ["doctor", "--help"],
            [
                "Diagnose a generated Forma artifact at PATH.",
                "whether",
                "install route",
            ],
        ),
        (
            ["drift", "--help"],
            [
                "Check whether generated Forma artifacts are fresh.",
                "Use --profile when an artifact should still match profile source.",
                "Without a source, drift reports base-origin freshness only.",
            ],
        ),
        (
            ["explain", "agent", "--help"],
            [
                "Explain the agent command path for workflow generation and maintenance.",
                "profile authoring, workflow generation",
                "plugin output, optional creator output, profile adoption, drift, doctor, and install",
                "If no approved profile exists yet",
            ],
        ),
        (
            ["explain", "profile", "--help"],
            [
                "Explain profile authoring and task-rule placement.",
                "Profile YAML Proposal",
                "Profile Review Packet",
                "forma create-bundle or forma create-plugin",
            ],
        ),
        (
            ["explain", "temporary-injection", "--help"],
            [
                "Explain temporary injection classification for one-off workflow rules.",
                "classify one-off workflow rules",
                "not an approved profile source",
            ],
        ),
        (
            ["profile", "adopt", "-h"],
            [
                "Convert a same-origin creator artifact into a candidate profile package.",
                "Directory to write the candidate profile package.",
                "Treat the profile as approved project source only after human review",
            ],
        ),
    ]

    for args, expected_phrases in cases:
        result = runner.invoke(main, args)
        assert result.exit_code == 0, result.output
        for phrase in expected_phrases:
            assert phrase in result.output


def test_explain_agent_outputs_command_guide() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["explain", "agent"])

    assert result.exit_code == 0, result.output
    assert "# Forma Agent Guide" in result.output
    assert "Generation targets: `codex`, `claude-code`, `opencode`" in result.output
    assert "plugin targets: `codex`, `claude-code`" in result.output
    assert "install targets: `codex`, `claude-code`, `opencode`" in result.output
    assert "## Profile write boundary" in result.output
    assert "Profiles are structured project-rule input" in result.output
    assert "`Profile YAML Proposal` and `Profile Review Packet`" in result.output
    assert "forma doctor <path>" in result.output
    assert "## Draft project rules, then generate workflow output" in result.output
    assert "forma explain profile --target <generation-target>" in result.output
    assert "forma verify <dir>/<generation-target>/forma-creator" in result.output
    assert "forma create-bundle --target <generation-target> --output <dir>" in result.output
    assert (
        "forma create-bundle --target <generation-target> --profile <profile.yaml> --output <dir>"
        in result.output
    )
    assert "forma create-bundle --target opencode" in result.output
    assert "forma install --target opencode" in result.output
    assert ".opencode/skills" in result.output
    assert "Codex plugin install state belongs to Codex" in result.output
    assert "ask the user which marketplace to use" in result.output
    assert "codex plugin marketplace list" in result.output
    assert "codex plugin add <plugin-id>@<marketplace-name>" in result.output
    assert "Claude Code plugin roots can be installed" in result.output
    assert (
        "forma create-plugin --target codex --profile <profile.yaml> --output <dir>"
        in result.output
    )
    assert (
        "forma create-plugin --target claude-code --profile <profile.yaml> --output <dir>"
        in result.output
    )
    assert "Generate from an approved profile" in result.output
    assert "Optional on-the-spot creator path" in result.output
    assert "candidate profile package" in result.output
    assert "forma profile adopt <artifact-dir> --output <profile-dir>" in result.output
    assert "`drift` checks whether generated output is fresh" in result.output
    assert "Omitting `--profile` generates generic no-profile workflow output" in result.output


def test_explain_agent_json_outputs_command_guide() -> None:
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["explain", "agent", "--format", "json", "--target", "claude-code"],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["topic"] == "agent"
    assert payload["target"] == "claude-code"
    assert "# Forma Agent Guide" in payload["markdown"]
    assert "## Profile write boundary" in payload["markdown"]
    assert "candidate profile package" in payload["markdown"]
    assert "Generate a Claude Code plugin" in payload["markdown"]
    assert "forma install --target claude-code --scope project <dir>" in payload["markdown"]


def test_old_create_command_is_rejected_with_current_command_names() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["create", "--help"])

    assert result.exit_code != 0
    assert "No such command 'create'" in result.output
    assert "create-bundle" in result.output
    assert "create-plugin" in result.output

def test_verify_json_emits_machine_readable_report_for_failures() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["verify", "--json", str(INVALID_BUNDLE)])

    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["schema"] == "forma.verify.report.v1"
    assert data["passed"] is False
    assert data["summary"]["errors"] > 0
    assert data["results"][0]["failure_class"]
    assert "Error:" not in result.output


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


def test_create_bundle_opencode_emits_native_skill_frontmatter(
    tmp_path: Path,
) -> None:
    output = tmp_path / "opencode-bundle"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "create-bundle",
            "--target",
            "opencode",
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert result.exit_code == 0, result.output
    skill_md = (output / "forma-plan" / "SKILL.md").read_text(encoding="utf-8")
    assert 'name: "forma-plan"' in skill_md
    assert "compatibility: opencode" in skill_md
    assert 'forma.stage: "shape"' in skill_md
    assert 'forma.target: "opencode"' in skill_md
    assert not (output / "forma-plan" / "agents" / "openai.yaml").exists()
    assert not (output / ".codex-plugin").exists()
    assert not (output / ".claude-plugin").exists()
    manifest = json.loads((output / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["target"] == "opencode"
    assert manifest["emitted_skills"]["shape"]["directory"] == "forma-plan"


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
    assert "Before install:" in result.output
    assert "Recommended Codex install path:" in result.output
    assert "run drift before any postprocess" in result.output
    assert "use `forma verify` as the final gate" in result.output
    assert "codex plugin marketplace list" in result.output
    assert "Ask the user to choose an existing marketplace" in result.output
    assert "developers.openai.com/codex/plugins/build#install-a-local-plugin-manually" in result.output
    assert "developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli" in result.output
    assert "codex plugin add forma@<marketplace-name>" in result.output
    assert "Codex plugin UI" in result.output
    assert "codex plugin marketplace --help" in result.output
    assert "Start a new Codex thread" in result.output
    assert "Forma does not install Codex plugins" in result.output
    assert (output / ".codex-plugin" / "plugin.json").is_file()
    assert (output / ".forma-manifest.json").is_file()
    assert (output / "skills" / "plan" / "SKILL.md").is_file()
    assert (output / "skills" / "showhand" / "SKILL.md").is_file()
    assert not (output / "skills" / "forma-plan").exists()
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
    assert (output / "skills" / "plan" / "SKILL.md").is_file()
    assert (output / "skills" / "showhand" / "SKILL.md").is_file()
    assert (output / "skills" / "reconcile" / "SKILL.md").is_file()
    assert not (output / "skills" / "forma-plan").exists()
    plugin = json.loads(
        (output / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert plugin["id"] == "forma"
    assert plugin["name"] == "forma"
    assert plugin["skills"] == "./skills/"


def test_profile_adopt_round_trips_creator_bundle(tmp_path: Path) -> None:
    refs = tmp_path / "refs"
    refs.mkdir()
    for name in ("zeta.md", "alpha.md", "middle.md"):
        (refs / name).write_text(f"# {name}\n", encoding="utf-8")
    artifact = _creator_artifact(
        tmp_path,
        injection={
            "rename": {"prefix": "acme-plan-first"},
            "stages": {
                "shape": {
                    "display_name": "Acme Plan",
                    "short_description": "Clarify Acme work before planning.",
                    "default_prompt": "Use $acme-plan-first-plan for Acme planning.",
                }
            },
            "skills": {
                "shape": {
                    "description": "Clarify Acme goals and boundaries before planning."
                }
            },
            "constraints": {
                "shape": ["Confirm Acme source material before proposal-ready."],
            },
            "validation_commands": {
                "pour": ["pytest tests/acme"],
            },
            "decision_gate_extras": ["External dependency impact"],
            "resources": {
                "shape": {
                    "references": [
                        {"source": str(refs / "zeta.md"), "dest": "zeta.md"},
                        {"source": str(refs / "alpha.md"), "dest": "alpha.md"},
                        {"source": str(refs / "middle.md"), "dest": "middle.md"},
                    ]
                }
            },
        },
    )
    manifest = json.loads((artifact / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert "profile" not in manifest
    assert manifest["creator_bundle"]["bundle_kind"] == "creator"
    output = tmp_path / "adopted-profile"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "profile",
            "adopt",
            str(artifact),
            "--output",
            str(output),
            "--profile-id",
            "acme-plan-first",
            "--json",
        ],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["schema"] == "forma.profile-adoption.v1"
    assert data["status"] == "adopted"
    assert data["profile_state"] == "candidate"
    assert data["review_required"] is True
    assert data["promotion_required"] is True
    assert data["artifact_kind"] == "skill-bundle"
    assert data["target"] == "codex"
    profile_file = output / "profile.yaml"
    assert profile_file.is_file()
    assert (output / "adoption-report.json").is_file()
    profile = yaml.safe_load(profile_file.read_text(encoding="utf-8"))
    assert profile["profile"]["id"] == "acme-plan-first"
    assert profile["stages"]["shape"]["name"] == "acme-plan-first-plan"
    assert profile["stages"]["shape"]["short_description"] == (
        "Clarify Acme work before planning."
    )
    assert profile["skills"]["shape"]["description"] == (
        "Clarify Acme goals and boundaries before planning."
    )
    assert profile["constraints"]["shape"] == [
        "Confirm Acme source material before proposal-ready."
    ]
    assert profile["validation_commands"]["pour"] == ["pytest tests/acme"]
    assert profile["decision_gate_extras"] == ["External dependency impact"]
    assert [
        item["dest"]
        for item in profile["resources"]["shape"]["references"]
    ] == ["zeta.md", "alpha.md", "middle.md"]

    regenerated = tmp_path / "regenerated"
    create = runner.invoke(
        main,
        [
            "create-bundle",
            "--target",
            "codex",
            "--profile",
            str(profile_file),
            "--output",
            str(regenerated),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert create.exit_code == 0, create.output
    assert normalized_payload_digest(regenerated) == normalized_payload_digest(artifact)
    _assert_profile_drift_fresh(runner, artifact, profile_file)


def test_profile_adopt_round_trips_creator_codex_plugin(tmp_path: Path) -> None:
    artifact = _creator_artifact(
        tmp_path,
        artifact="plugin",
        injection={
            "rename": {"prefix": "acme-plan-first"},
            "skills": {
                "flow": {
                    "description": "Execute accepted Acme work until the plan is complete."
                }
            },
        },
    )
    manifest = json.loads((artifact / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert "profile" not in manifest
    assert manifest["creator_bundle"]["bundle_kind"] == "creator"
    output = tmp_path / "adopted-plugin-profile"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "profile",
            "adopt",
            str(artifact),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "forma profile adopt: wrote candidate profile:" in result.output
    profile_file = output / "profile.yaml"
    profile = yaml.safe_load(profile_file.read_text(encoding="utf-8"))
    assert profile["profile"]["id"] == "acme-plan-first"
    assert profile["bundle"]["name"] == "acme-plan-first"
    assert profile["stages"]["flow"]["name"] == "showhand"

    regenerated = tmp_path / "regenerated-plugin"
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(profile_file),
            "--output",
            str(regenerated),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert create.exit_code == 0, create.output
    assert normalized_payload_digest(regenerated) == normalized_payload_digest(artifact)
    _assert_profile_drift_fresh(runner, artifact, profile_file)


def test_profile_adopt_round_trips_profile_codex_plugin(tmp_path: Path) -> None:
    artifact = tmp_path / "profile-plugin"
    output = tmp_path / "adopted-profile-plugin"
    runner = CliRunner()

    create_artifact = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(SAMPLE_PROFILE),
            "--output",
            str(artifact),
        ],
    )
    assert create_artifact.exit_code == 0, create_artifact.output

    result = runner.invoke(
        main,
        [
            "profile",
            "adopt",
            str(artifact),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    profile_file = output / "profile.yaml"
    profile = yaml.safe_load(profile_file.read_text(encoding="utf-8"))
    assert profile["profile"]["id"] == "sample-backend-go-github-issue-tracked"
    assert profile["bundle"]["name"] == "sample-backend-go-github-issue-tracked"
    assert profile["bundle"]["description"] == (
        "Sanitized sample Go backend plan-first workflow bundle for GitHub issue tracked development."
    )
    assert profile["org"]["name"] == "Example Team"
    assert profile["stages"]["shape"]["short_description"].startswith(
        "Use only in Plan mode"
    )
    assert profile["skills"]["shape"]["description"].startswith(
        "Use only in plan-oriented collaboration"
    )

    regenerated = tmp_path / "regenerated-profile-plugin"
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(profile_file),
            "--output",
            str(regenerated),
        ],
    )

    assert create.exit_code == 0, create.output
    assert normalized_payload_digest(regenerated) == normalized_payload_digest(artifact)


def test_profile_adopt_preserves_codex_plugin_display_name(tmp_path: Path) -> None:
    profile_file = tmp_path / "api-tools.yaml"
    profile_file.write_text(
        """
profile:
  id: api-tools
bundle:
  name: api-tools
  description: API tools workflow.
plugin:
  display_name: API Tools
""".lstrip(),
        encoding="utf-8",
    )
    artifact = tmp_path / "profile-plugin"
    output = tmp_path / "adopted-profile-plugin"
    runner = CliRunner()

    create_artifact = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(profile_file),
            "--output",
            str(artifact),
        ],
    )
    assert create_artifact.exit_code == 0, create_artifact.output

    result = runner.invoke(
        main,
        [
            "profile",
            "adopt",
            str(artifact),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    adopted_profile_file = output / "profile.yaml"
    profile = yaml.safe_load(adopted_profile_file.read_text(encoding="utf-8"))
    assert profile["bundle"]["name"] == "api-tools"
    assert profile["plugin"]["display_name"] == "API Tools"

    regenerated = tmp_path / "regenerated-profile-plugin"
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(adopted_profile_file),
            "--output",
            str(regenerated),
        ],
    )

    assert create.exit_code == 0, create.output
    assert normalized_payload_digest(regenerated) == normalized_payload_digest(artifact)


def test_profile_adopt_round_trips_plugin_with_disabled_stage(tmp_path: Path) -> None:
    source_profile = tmp_path / "four-stage.yaml"
    source_profile.write_text(
        """profile:
  id: acme-four-stage-plan-first
bundle:
  name: acme-four-stage
stages:
  pour:
    enabled: false
""",
        encoding="utf-8",
    )
    artifact = tmp_path / "four-stage-plugin"
    output = tmp_path / "adopted-four-stage-profile"
    runner = CliRunner()

    create_artifact = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(source_profile),
            "--output",
            str(artifact),
        ],
    )

    assert create_artifact.exit_code == 0, create_artifact.output
    manifest = json.loads(
        (artifact / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert "pour" not in manifest["emitted_skills"]

    result = runner.invoke(
        main,
        [
            "profile",
            "adopt",
            str(artifact),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    profile_file = output / "profile.yaml"
    profile = yaml.safe_load(profile_file.read_text(encoding="utf-8"))
    assert profile["stages"]["pour"] == {"enabled": False}
    assert "pour" not in profile["skills"]

    regenerated = tmp_path / "regenerated-four-stage-plugin"
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(profile_file),
            "--output",
            str(regenerated),
        ],
    )

    assert create.exit_code == 0, create.output
    assert normalized_payload_digest(regenerated) == normalized_payload_digest(artifact)


def test_profile_adopt_round_trips_plugin_with_conditional_overlays(
    tmp_path: Path,
) -> None:
    backend_ref = tmp_path / "backend-rules.md"
    backend_ref.write_text("Backend overlay rules.\n", encoding="utf-8")
    source_profile = tmp_path / "conditional.yaml"
    source_profile.write_text(
        """profile:
  id: acme-conditional-plan-first
bundle:
  name: acme-conditional
conditional_overlays:
  decision:
    name: Plan Type
    must_record_in_plan: true
    missing_during_execution: stop-for-plan-correction
  routes:
    - id: generic-dev
      description: Generic development work.
      overlays: []
    - id: backend
      description: Backend work.
      overlays: [backend]
  overlays:
    backend:
      description: Backend-specific planning and execution rules.
      constraints:
        shape:
          - Confirm backend-visible behavior before proposal-ready.
      resources:
        default:
          references:
            - source: backend-rules.md
              dest: backend-rules.md
""",
        encoding="utf-8",
    )
    artifact = tmp_path / "conditional-plugin"
    output = tmp_path / "adopted-conditional-profile"
    runner = CliRunner()

    create_artifact = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(source_profile),
            "--output",
            str(artifact),
        ],
    )

    assert create_artifact.exit_code == 0, create_artifact.output
    manifest = json.loads(
        (artifact / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["conditional_overlays"]["routes"][1]["references"]["shape"] == [
        "references/backend-rules.md"
    ]

    result = runner.invoke(
        main,
        [
            "profile",
            "adopt",
            str(artifact),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    profile_file = output / "profile.yaml"
    profile = yaml.safe_load(profile_file.read_text(encoding="utf-8"))
    routes = profile["conditional_overlays"]["routes"]
    assert "references" not in routes[1]
    assert routes[1]["overlays"] == ["backend"]

    regenerated = tmp_path / "regenerated-conditional-plugin"
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "codex",
            "--profile",
            str(profile_file),
            "--output",
            str(regenerated),
        ],
    )

    assert create.exit_code == 0, create.output
    assert normalized_payload_digest(regenerated) == normalized_payload_digest(artifact)


def test_profile_adopt_fails_without_base_origin(tmp_path: Path) -> None:
    artifact = _creator_artifact(tmp_path)
    manifest_path = artifact / ".forma-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.pop("base_origin")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["profile", "adopt", str(artifact), "--output", str(tmp_path / "profile")],
    )

    assert result.exit_code != 0
    assert "missing base_origin" in result.output


def test_profile_adopt_fails_on_base_origin_mismatch(tmp_path: Path) -> None:
    artifact = _creator_artifact(tmp_path)
    manifest_path = artifact / ".forma-manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["base_origin"]["base_output_digest"] = "0" * 64
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["profile", "adopt", str(artifact), "--output", str(tmp_path / "profile")],
    )

    assert result.exit_code != 0
    assert "base_origin digest does not match" in result.output


def test_profile_adopt_fails_on_unrepresentable_residual_diff(tmp_path: Path) -> None:
    artifact = _creator_artifact(tmp_path)
    metadata = artifact / "forma-plan" / "agents" / "openai.yaml"
    metadata.write_text(
        metadata.read_text(encoding="utf-8").replace(
            'display_name: "Shape"',
            'display_name: "Different Metadata Name"',
        ),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["profile", "adopt", str(artifact), "--output", str(tmp_path / "profile")],
    )

    assert result.exit_code != 0
    assert "display_name differs" in result.output


def test_drift_with_profile_reports_fresh_and_stale(tmp_path: Path) -> None:
    artifact = tmp_path / "bundle"
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-bundle",
            "--target",
            "codex",
            "--profile",
            str(SAMPLE_PROFILE),
            "--output",
            str(artifact),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    assert create.exit_code == 0, create.output

    fresh = runner.invoke(
        main,
        ["drift", str(artifact), "--profile", str(SAMPLE_PROFILE), "--json"],
    )

    assert fresh.exit_code == 0, fresh.output
    fresh_data = json.loads(fresh.output)
    assert fresh_data["status"] == "fresh"
    assert fresh_data["artifacts"][0]["source_kind"] == "profile"

    skill = artifact / "backend-plan-first-ground" / "SKILL.md"
    skill.write_text(
        skill.read_text(encoding="utf-8") + "\n<!-- stale marker -->\n",
        encoding="utf-8",
    )
    stale = runner.invoke(
        main,
        ["drift", str(artifact), "--profile", str(SAMPLE_PROFILE), "--json"],
    )

    assert stale.exit_code == 0, stale.output
    stale_data = json.loads(stale.output)
    assert stale_data["status"] == "stale"
    assert stale_data["artifacts"][0]["status"] == "stale"


def test_drift_without_source_reports_unknown_source_base_origin(
    tmp_path: Path,
) -> None:
    artifact = _creator_artifact(
        tmp_path,
        injection={"constraints": {"shape": ["Confirm source context."]}},
    )
    runner = CliRunner()

    result = runner.invoke(main, ["drift", str(artifact), "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["status"] == "unknown-source"
    item = data["artifacts"][0]
    assert item["status"] == "unknown-source"
    assert item["source_kind"] == "none"
    assert item["base_origin_status"] == "fresh"


def test_drift_creator_source_reports_unknown_for_injected_artifact(
    tmp_path: Path,
) -> None:
    artifact = _creator_artifact(
        tmp_path,
        injection={"constraints": {"shape": ["Confirm source context."]}},
    )
    runner = CliRunner()

    result = runner.invoke(
        main,
        ["drift", str(artifact), "--creator-source", str(META_SOURCE), "--json"],
    )

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["status"] == "unknown-source"
    assert data["artifacts"][0]["base_origin_status"] == "fresh"


def test_drift_release_surface_reports_known_paths() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["drift", "--release-surface", "--json"])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    paths = {item["path"] for item in data["artifacts"]}
    assert any(path.endswith("examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex") for path in paths)
    assert any(path.endswith("dist/skills/codex/forma-creator") for path in paths)
    assert any(path.endswith("dist/skills/opencode/forma-creator") for path in paths)
    assert any(path.endswith("dist/skill-bundles/opencode") for path in paths)
    assert any(path.endswith("dist/plugins/codex/forma") for path in paths)
    assert any(path.endswith("dist/plugins/claude-code/forma") for path in paths)
    assert {item["status"] for item in data["artifacts"]} <= {
        "fresh",
        "stale",
        "invalid",
        "unknown-source",
    }


def test_doctor_json_reports_forma_install_route_for_bundle(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    runner = CliRunner()
    create = runner.invoke(
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
    assert create.exit_code == 0, create.output

    result = runner.invoke(main, ["doctor", "--json", str(output)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["schema"] == "forma.doctor.report.v1"
    assert data["artifact_kind"] == "skill-bundle"
    assert data["target"] == "codex"
    assert data["verification"]["passed"] is True
    assert data["forma_install_supported"] is True
    assert data["installable_now"] is True
    assert data["install_route"] == "forma-install:codex"
    assert data["blockers"] == []


def test_doctor_routes_codex_plugins_to_codex(tmp_path: Path) -> None:
    output = tmp_path / "plugin"
    runner = CliRunner()
    create = runner.invoke(
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
    assert create.exit_code == 0, create.output

    human = runner.invoke(main, ["doctor", str(output)])
    result = runner.invoke(main, ["doctor", "--json", str(output)])

    assert human.exit_code == 0, human.output
    assert "artifact kind : codex-plugin" in human.output
    assert "forma install : no" in human.output
    assert "install route : codex-plugin" in human.output
    data = json.loads(result.output)
    assert result.exit_code == 0, result.output
    assert data["artifact_kind"] == "codex-plugin"
    assert data["target"] == "codex"
    assert data["forma_install_supported"] is False
    assert data["installable_now"] is False
    assert data["install_route"] == "codex-plugin"
    assert data["blockers"] == []
    assert any("codex plugin add forma@<marketplace-name>" in step for step in data["next_steps"])


def test_doctor_routes_claude_code_plugins_to_forma_install(tmp_path: Path) -> None:
    output = tmp_path / "plugin"
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "claude-code",
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    assert create.exit_code == 0, create.output

    human = runner.invoke(main, ["doctor", str(output)])
    result = runner.invoke(main, ["doctor", "--json", str(output)])

    assert human.exit_code == 0, human.output
    assert "artifact kind : claude-code-plugin" in human.output
    assert "forma install : yes" in human.output
    assert "install route : forma-install:claude-code" in human.output
    data = json.loads(result.output)
    assert result.exit_code == 0, result.output
    assert data["artifact_kind"] == "claude-code-plugin"
    assert data["target"] == "claude-code"
    assert data["forma_install_supported"] is True
    assert data["installable_now"] is True
    assert data["install_route"] == "forma-install:claude-code"
    assert data["blockers"] == []
    assert any("forma install --target claude-code" in step for step in data["next_steps"])


def test_doctor_json_reports_invalid_bundle_blockers() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--json", str(INVALID_BUNDLE)])

    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["artifact_kind"] == "skill-bundle"
    assert data["verification"]["passed"] is False
    assert "verification failed" in data["blockers"]


def test_create_plugin_emits_claude_code_plugin_layout(tmp_path: Path) -> None:
    runner = CliRunner()
    output = tmp_path / "plugin"

    result = runner.invoke(
        main,
        [
            "create-plugin",
            "--target",
            "claude-code",
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "wrote Claude Code plugin" in result.output
    assert "forma install --target claude-code" in result.output
    assert (output / ".claude-plugin" / "plugin.json").is_file()
    assert (output / ".forma-manifest.json").is_file()
    assert (output / "skills" / "plan" / "SKILL.md").is_file()
    assert (output / "skills" / "showhand" / "SKILL.md").is_file()
    assert not (output / ".codex-plugin").exists()
    assert not (output / "skills" / "forma-plan").exists()
    plugin = json.loads(
        (output / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert plugin["name"] == "forma"
    manifest = json.loads(
        (output / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["target"] == "claude-code"
    assert manifest["emitted_skills"]["shape"]["name"] == "plan"


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
    assert (project / ".agents" / "skills" / "forma-plan").is_dir()
    assert (project / ".agents" / "skills" / "forma-showhand").is_dir()
    assert not (project / ".codex" / "skills").exists()

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


def test_install_codex_bundle_user_scope_uses_codex_home(
    tmp_path: Path,
    monkeypatch,
) -> None:
    bundle = tmp_path / "bundle"
    home = tmp_path / "home"
    home.mkdir()
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

    monkeypatch.setenv("HOME", str(home))
    install = runner.invoke(
        main,
        ["install", "--target", "codex", "--scope", "user", str(bundle)],
    )

    assert install.exit_code == 0, install.output
    assert (home / ".codex" / "skills" / "forma-plan").is_dir()
    assert (home / ".codex" / "skills" / "forma-showhand").is_dir()
    assert not (home / ".agents" / "skills").exists()


def test_install_opencode_bundle_project_scope(
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
            "opencode",
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
        ["install", "--target", "opencode", "--scope", "project", str(bundle)],
    )

    assert install.exit_code == 0, install.output
    assert (project / ".opencode" / "skills" / "forma-plan").is_dir()
    assert (project / ".opencode" / "skills" / "forma-showhand").is_dir()
    assert not (project / ".agents" / "skills").exists()


def test_install_opencode_bundle_user_scope(
    tmp_path: Path,
    monkeypatch,
) -> None:
    bundle = tmp_path / "bundle"
    home = tmp_path / "home"
    home.mkdir()
    runner = CliRunner()
    create = runner.invoke(
        main,
        [
            "create-bundle",
            "--target",
            "opencode",
            "--output",
            str(bundle),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    assert create.exit_code == 0, create.output

    monkeypatch.setenv("HOME", str(home))
    install = runner.invoke(
        main,
        ["install", "--target", "opencode", "--scope", "user", str(bundle)],
    )

    assert install.exit_code == 0, install.output
    assert (home / ".config" / "opencode" / "skills" / "forma-plan").is_dir()
    assert (home / ".config" / "opencode" / "skills" / "forma-showhand").is_dir()
    assert not (home / ".agents" / "skills").exists()


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


def test_install_claude_code_plugin_project_scope_and_replace(
    tmp_path: Path,
    monkeypatch,
) -> None:
    plugin = _write_minimal_claude_plugin(tmp_path / "plugin")
    project = tmp_path / "project"
    project.mkdir()
    runner = CliRunner()

    monkeypatch.chdir(project)
    install = runner.invoke(
        main,
        ["install", "--target", "claude-code", "--scope", "project", str(plugin)],
    )

    assert install.exit_code == 0, install.output
    assert "forma install: installed claude-code-plugin" in install.output
    destination = project / ".claude" / "skills" / "sample-plugin"
    assert (destination / ".claude-plugin" / "plugin.json").is_file()
    assert (destination / "skills" / "plan" / "SKILL.md").is_file()

    conflict = runner.invoke(
        main,
        ["install", "--target", "claude-code", "--scope", "project", str(plugin)],
    )
    assert conflict.exit_code != 0
    assert "--replace" in conflict.output

    replace = runner.invoke(
        main,
        [
            "install",
            "--target",
            "claude-code",
            "--scope",
            "project",
            "--replace",
            str(plugin),
        ],
    )
    assert replace.exit_code == 0, replace.output


def test_install_rejects_claude_code_plugin_for_codex_target(
    tmp_path: Path,
    monkeypatch,
) -> None:
    plugin = _write_minimal_claude_plugin(tmp_path / "plugin")
    project = tmp_path / "project"
    project.mkdir()
    runner = CliRunner()

    monkeypatch.chdir(project)
    install = runner.invoke(
        main,
        ["install", "--target", "codex", "--scope", "project", str(plugin)],
    )

    assert install.exit_code != 0
    assert "can only be installed with --target claude-code" in install.output
    assert not (project / ".agents" / "skills" / "sample-plugin").exists()


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
    assert "Before install:" in install.output
    assert "Recommended Codex install path:" in install.output
    assert "run drift before any postprocess" in install.output
    assert "use `forma verify` as the final gate" in install.output
    assert "codex plugin marketplace list" in install.output
    assert "Ask the user to choose an existing marketplace" in install.output
    assert "developers.openai.com/codex/plugins/build#install-a-local-plugin-manually" in install.output
    assert "developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli" in install.output
    assert "codex plugin add forma@<marketplace-name>" in install.output
    assert "Codex plugin UI" in install.output
    assert "codex plugin marketplace --help" in install.output
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
