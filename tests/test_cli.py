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
from forma.reports import (
    ActionableReport,
    INTERACTION_CHOICE,
    NextAction,
    ReportSection,
    render_report,
)
from forma.routes import (
    HANDOFF_KIND_PROFILE_REFINEMENT,
    HANDOFF_TITLE_PROFILE_REFINEMENT,
)


ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = ROOT / "source" / "methodology"
FORMA_SELF_PROFILE = ROOT / ".forma" / "profile.yaml"
SAMPLE_PROFILE = (
    ROOT
    / "examples"
    / "profiles"
    / "sample-backend"
    / "sample-backend-go-github-issue-tracked.yaml"
)
INVALID_BUNDLE = ROOT / "tests" / "fixtures" / "invalid-bundle"
VALID_BUNDLE = ROOT / "tests" / "fixtures" / "valid-bundle"
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
        assert 'For repository diagnosis or "is this project ready for agents"' in result.output
        assert "forma doctor --format agent <repo>" in result.output
        assert "forma doctor --format json <repo>" in result.output


def test_command_help_includes_agent_next_steps() -> None:
    runner = CliRunner()
    cases = [
        (
            ["build", "--help"],
            [
                "Build Forma workflow artifacts from profile or creator source.",
                "Profile-local reinstall workflow:",
                "If reinstall-workflow.sh exists",
                "treat the reusable install path as incomplete",
                "explicitly requests a temporary one-time run",
            ],
        ),
        (
            ["build", "creator", "--help"],
            [
                "Use this when a user specifically wants an on-the-spot creator run",
                "Verify the generated creator skill:",
                "forma install --target codex|claude-code|opencode --scope user|project <creator-path>",
            ],
        ),
        (
            ["build", "bundle", "--help"],
            [
                "Compile project rules into a target-specific skill bundle.",
                "Verify before installing:",
                "forma install --target codex|claude-code|opencode --scope user|project <output-dir>",
                "Profile-local reinstall workflow:",
                "If reinstall-workflow.sh exists",
                "treat the reusable install path as incomplete",
                "A completed reinstall script should cover generation",
            ],
        ),
        (
            ["build", "plugin", "--help"],
            [
                "Compile project rules into a target-specific plugin source.",
                "Verify the plugin source:",
                "ask the user which marketplace to use",
                "codex plugin add <plugin-id>@<marketplace-name>",
                "Do not install Codex plugins with forma install.",
                "Install Claude Code plugin roots with forma install --target claude-code.",
                "Profile-local reinstall workflow:",
                "If reinstall-workflow.sh exists",
                "treat the reusable install path as incomplete",
                "the local install route",
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
            ["init", "--help"],
                [
                    "Plan or apply deterministic Forma repository initialization.",
                    "Default mode is a dry run.",
                    "create deterministic workflow source files",
                    "--from-report",
                    "still needs human review",
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
                "Diagnose repository agent operability.",
                "forma explain agent",
                "forma explain agent --target codex|claude-code|opencode",
                "A needs-agent result requires",
                "finding dispositions",
                "not a final",
                "diagnosis to return unchanged",
                "--format",
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
                        "optional creator output, profile adoption",
                        "doctor, init, verify, and install",
                        "If no approved profile exists yet",
                    ],
                ),
        (
            ["explain", "profile", "--help"],
                [
                    "Explain profile authoring and task-rule placement.",
                    "Profile YAML",
                    "Review Packet",
                    "forma build bundle or forma build plugin",
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
                "Convert a Forma-provenance creator artifact into a candidate profile package.",
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
    assert "read-only command-routing guide for agents using Forma" in result.output
    assert "does not inspect a repository" in result.output
    assert "what facts the agent must bring from the repository or user" in result.output
    assert "Generation targets: `codex`, `claude-code`, `opencode`" in result.output
    assert "plugin targets: `codex`, `claude-code`" in result.output
    assert "install targets: `codex`, `claude-code`, `opencode`" in result.output
    assert "## Profile write boundary" in result.output
    assert "Profiles are structured project-rule input" in result.output
    assert "`Profile YAML Proposal` and `Profile Review Packet`" in result.output
    assert "## Profile-local workflow scripts" in result.output
    assert "`reinstall-workflow.sh`" in result.output
    assert "instead of assembling `forma build bundle`" in result.output
    assert "treat the reusable install path as incomplete" in result.output
    assert "Before running hand-assembled build or install commands" in result.output
    assert "Only proceed with a one-off manual flow" in result.output
    assert "Reusable install setup goal: explore whatever local environment details" in result.output
    assert "Required install facts before reusable success" in result.output
    assert "artifact kind, target" in result.output
    assert "Stable reinstall scripts must encode fixed facts" in result.output
    assert "must not run `codex plugin marketplace list`" in result.output
    assert "write one real script, not notes" in result.output
    assert "`reinstall-workflow.sh` must reproduce generation" in result.output
    assert "run the new script once before reporting reusable install setup success" in result.output
    assert "final install report must include the profile-local reinstall state" in result.output
    assert "completed and ran the script" in result.output
    assert "user requested one-off manual flow" in result.output
    assert "forma doctor --format json <repo>" in result.output
    assert "forma doctor --format agent <repo>" in result.output
    assert "forma init --from-report <report> --apply <repo>" in result.output
    assert "not a generated artifact verifier" in result.output
    assert "Forma workflow source is project-rule management" in result.output
    assert "investigation input, not the final user diagnosis" in result.output
    assert "assign a disposition to every non-contract core finding" in result.output
    assert "Do not copy unresolved findings into the final answer and stop" in result.output
    assert "Stop only when every finding has a disposition" in result.output
    assert "Finish all agent-resolvable investigation" in result.output
    assert "Doctor-ready operability is not the same as a project-ready profile" in result.output
    assert "what the repository is for" in result.output
    assert "durable maintenance semantics" in result.output
    assert "workflow source and Agent handoff files" in result.output
    assert "owner confirmations" in result.output
    assert "does not approve semantic rules" in result.output
    assert "forma doctor <path>" not in result.output
    assert "## Draft project rules, then generate workflow output" in result.output
    assert "forma explain profile --target <generation-target>" in result.output
    assert "forma verify <dir>/<generation-target>/forma-creator" in result.output
    assert "forma build bundle --target <generation-target> --output <dir>" in result.output
    assert (
        "forma build bundle --target <generation-target> --profile <profile.yaml> --output <dir>"
        in result.output
    )
    assert "forma build bundle --target opencode" in result.output
    assert "forma install --target opencode" in result.output
    assert ".opencode/skills" in result.output
    assert "Codex plugin install state belongs to Codex" in result.output
    assert "marketplace source" in result.output
    assert "codex plugin add <confirmed-plugin-id>@<confirmed-marketplace>" in result.output
    assert "Claude Code plugin roots can be installed" in result.output
    assert (
        "forma build plugin --target codex --profile <profile.yaml> --output <dir>"
        in result.output
    )
    assert (
        "forma build plugin --target claude-code --profile <profile.yaml> --output <dir>"
        in result.output
    )
    assert "Generate from an approved profile" in result.output
    assert "Optional on-the-spot creator path" in result.output
    assert "candidate profile package" in result.output
    assert "forma profile adopt <artifact-dir> --output <profile-dir>" in result.output
    assert "Build workflow artifacts with `forma build bundle`" in result.output
    assert "Do not use removed command entrypoints" in result.output
    assert "`forma create-bundle`, `forma create-plugin`" in result.output
    assert "Do not add compatibility aliases" in result.output
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
    assert payload["schema"] == "forma.actionable-report.v1"
    assert payload["command"] == "forma explain agent"
    assert payload["metadata"]["topic"] == "agent"
    assert payload["metadata"]["target"] == "claude-code"
    assert "# Forma Agent Guide" in payload["metadata"]["markdown"]
    assert "read-only command-routing guide for agents using Forma" in payload["metadata"]["markdown"]
    assert "doctor, init, verify, and install" in payload["metadata"]["markdown"]
    assert "## Profile write boundary" in payload["metadata"]["markdown"]
    assert "Start from this command-routing guide" in payload["metadata"]["markdown"]
    assert "does not inspect the repository" in payload["metadata"]["markdown"]
    assert "Doctor-ready operability is not the same as a project-ready profile" in payload[
        "metadata"
    ]["markdown"]
    assert HANDOFF_TITLE_PROFILE_REFINEMENT in payload["metadata"]["markdown"]
    assert "load `forma explain profile --format agent --target <target>` next" in payload[
        "metadata"
    ]["markdown"]
    assert "run `forma explain stage <stage>`" in payload["metadata"]["markdown"]
    assert "candidate profile package" in payload["metadata"]["markdown"]
    assert "Generate a Claude Code plugin" in payload["metadata"]["markdown"]
    assert "forma install --target claude-code --scope project <dir>" in payload["metadata"]["markdown"]
    assert "workflow source and Agent handoff files" in payload["metadata"]["markdown"]
    commands = {action["command"] for action in payload["next_actions"] if "command" in action}
    assert "forma doctor --format json <repo>" in commands
    assert "forma init --from-report <report> --apply <repo>" in commands
    profile_action = next(
        action
        for action in payload["next_actions"]
        if action.get("command") == "forma explain profile --target claude-code"
    )
    assert "existing-profile incremental review" in profile_action["description"]


def test_explain_profile_renderer_boundaries() -> None:
    runner = CliRunner()

    human = runner.invoke(
        main,
        ["explain", "profile", "--format", "human", "--target", "codex"],
    )
    agent = runner.invoke(
        main,
        ["explain", "profile", "--format", "agent", "--target", "codex"],
    )
    json_result = runner.invoke(
        main,
        ["explain", "profile", "--format", "json", "--target", "codex"],
    )

    assert human.exit_code == 0, human.output
    assert "Profile Renderer Boundary" in human.output
    assert "after `forma explain agent` routes the work" in human.output
    assert "explains how to extract candidate rules" in human.output
    assert "incremental coverage review" in human.output
    assert "must use these exact headings" in human.output
    assert "`Covered`, `Missing`, `Stale`, `Redundant`, `Stage Placement`" in human.output
    assert "`Recommended Next Step`" in human.output
    assert "exactly two child lines" in human.output
    assert "`Recommendation: <one concrete next action>`" in human.output
    assert "`Offer: Should I <perform that action> now?`" in human.output
    assert "structured user-input" in human.output
    assert "Required Confirmation" in human.output
    assert "Stop after that incremental review" in human.output
    assert "Use `--format agent` for the full executable authoring contract" in human.output
    assert "## Constraint Placement" not in human.output

    assert agent.exit_code == 0, agent.output
    assert "ACTIONABLE REPORT" in agent.output
    assert "[guidance] Forma Profile Guidance" in agent.output
    assert "## Candidate Draft From Project Facts" in agent.output
    assert "## Existing Profile Incremental Review" in agent.output
    assert "`Covered`" in agent.output
    assert "`Missing`" in agent.output
    assert "minimal YAML delta" in agent.output
    assert "`Recommended Next Step`" in agent.output
    assert "Do not collapse" in agent.output
    assert "passive note" in agent.output
    assert "multi-part list" in agent.output
    assert "command approval UI is" in agent.output
    assert "actual tool or shell actions" in agent.output
    assert "do not run build, verify, or drift" in agent.output
    assert "## Project Purpose And Maintenance Semantics" in agent.output
    assert "Doctor `ready` means" in agent.output
    assert "project-ready" in agent.output
    assert "label the draft `operability-only`" in agent.output
    assert "### Profile Review Packet: Project Understanding" in agent.output
    assert "## Constraint Placement" in agent.output
    assert "settle reusable reinstall facts" in agent.output
    assert "artifact kind" in agent.output
    assert "visibility check" in agent.output
    assert "next_actions:" in agent.output

    assert json_result.exit_code == 0, json_result.output
    payload = json.loads(json_result.output)
    assert payload["schema"] == "forma.actionable-report.v1"
    assert payload["command"] == "forma explain profile"
    assert payload["metadata"]["topic"] == "profile"
    assert {section["kind"] for section in payload["sections"]} == {
        "guidance",
        "sources",
    }
    assert "diagnostic-findings" not in {
        section["kind"] for section in payload["sections"]
    }
    assert "facts" not in payload
    assert "findings" not in payload
    assert "evidence" not in payload
    assert any(
        action["title"] == "settle reusable reinstall facts"
        for action in payload["next_actions"]
    )


def test_old_create_commands_are_rejected_with_current_command_names() -> None:
    runner = CliRunner()

    create = runner.invoke(main, ["create", "--help"])
    create_bundle = runner.invoke(main, ["create-bundle", "--help"])
    create_plugin = runner.invoke(main, ["create-plugin", "--help"])

    assert create.exit_code != 0
    assert "No such command 'create'" in create.output
    assert create_bundle.exit_code != 0
    assert "No such command 'create-bundle'" in create_bundle.output
    assert create_plugin.exit_code != 0
    assert "No such command 'create-plugin'" in create_plugin.output


def test_actionable_report_renders_human_agent_and_json() -> None:
    report = ActionableReport(
        command="forma build plugin",
        subject="profiles/sample/profile.yaml",
        status="needs-agent",
        summary="plugin source was generated",
        sections=(
            ReportSection(
                kind="produced-artifact",
                title="Produced Artifact",
                payload={"path": "/tmp/plugin", "target": "codex"},
            ),
        ),
        next_actions=(
            NextAction(
                title="verify generated plugin",
                command="forma verify /tmp/plugin",
                stop_condition="verification fails",
                forbidden=("do not install Codex plugins with forma install",),
            ),
        ),
    )

    human = render_report(report, "human")
    agent = render_report(report, "agent")
    payload = json.loads(render_report(report, "json"))

    assert "forma build plugin: plugin source was generated" in human
    assert "Produced Artifact" in human
    assert "verify generated plugin: forma verify /tmp/plugin" not in human
    assert "Next:" not in human
    assert "ACTIONABLE REPORT" in agent
    assert "[produced-artifact] Produced Artifact" in agent
    assert "stop_condition: verification fails" in agent
    assert "forbidden: do not install Codex plugins with forma install" in agent
    assert payload["schema"] == "forma.actionable-report.v1"
    assert payload["status"] == "needs-agent"
    assert payload["sections"][0]["kind"] == "produced-artifact"
    assert "facts" not in payload
    assert "findings" not in payload
    assert "evidence" not in payload


def test_actionable_report_rejects_unsupported_format() -> None:
    report = ActionableReport(
        command="forma explain agent",
        subject="codex",
        status="ready",
        summary="guidance is available",
    )

    try:
        report.render("markdown")  # type: ignore[arg-type]
    except ValueError as exc:
        assert "unsupported report format" in str(exc)
        assert "human, agent, json" in str(exc)
    else:
        raise AssertionError("expected unsupported format to raise")


def test_next_action_rejects_unknown_interaction() -> None:
    try:
        NextAction(title="bad", interaction="modal")  # type: ignore[arg-type]
    except ValueError as exc:
        assert "unsupported interaction" in str(exc)
        assert INTERACTION_CHOICE in str(exc)
    else:
        raise AssertionError("expected invalid interaction to raise")


def _report_section(payload: dict[str, object], kind: str) -> dict[str, object]:
    for section in payload["sections"]:  # type: ignore[index]
        if section["kind"] == kind:
            return section["payload"]  # type: ignore[return-value]
    raise AssertionError(f"missing report section {kind!r}")


def test_verify_json_emits_machine_readable_report_for_failures() -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["verify", "--json", str(INVALID_BUNDLE)])

    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["schema"] == "forma.verify.report.v1"
    assert data["passed"] is False
    assert data["summary"]["errors"] > 0
    assert data["results"][0]["failure_class"]
    assert data["next_actions"][0]["title"] == "fix verifier errors"
    assert "ask whether the user wants you to apply" in data["next_actions"][0]["description"]
    assert data["next_actions"][0]["requires_confirmation"] is True
    assert data["next_actions"][0]["interaction"] == INTERACTION_CHOICE
    assert "verifier errors" in data["next_actions"][0]["confirmation_prompt"]
    assert "Error:" not in result.output


def test_build_bundle_default_profile_emits_forma_workflow(tmp_path: Path) -> None:
    output = tmp_path / "bundle"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build",
            "bundle",
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


def test_build_bundle_opencode_emits_native_skill_frontmatter(
    tmp_path: Path,
) -> None:
    output = tmp_path / "opencode-bundle"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build",
            "bundle",
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


def test_profile_backed_build_bundle_outputs_script_status(tmp_path: Path) -> None:
    output = tmp_path / "profile-bundle"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build",
            "bundle",
            "--target",
            "codex",
            "--profile",
            str(SAMPLE_PROFILE),
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Produced Artifact" in result.output
    assert "Profile-Local Reinstall Workflow" not in result.output
    assert f"profile_dir: {SAMPLE_PROFILE.parent}" not in result.output
    assert "script: reinstall-workflow.sh" not in result.output
    assert "state: bootstrap-required" not in result.output
    assert "bootstrap profile-local reinstall workflow" not in result.output
    assert "Next:" not in result.output


def test_profile_backed_build_bundle_agent_format_outputs_next_actions(
    tmp_path: Path,
) -> None:
    output = tmp_path / "profile-bundle"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build",
            "bundle",
            "--target",
            "codex",
            "--profile",
            str(SAMPLE_PROFILE),
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
            "--format",
            "agent",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "ACTIONABLE REPORT" in result.output
    assert "[profile-local-reinstall-workflow] Profile-Local Reinstall Workflow" in result.output
    assert "settle install facts and complete profile-local reinstall workflow" in result.output
    assert "required_install_facts" in result.output
    assert "artifact kind" in result.output
    assert "marketplace source" in result.output
    assert "drift generated output against profile" in result.output
    assert f"forma drift {output} --profile {SAMPLE_PROFILE}" in result.output
    assert "forbidden: do not report the manual flow as reusable" in result.output
    assert "forbidden: do not put Codex marketplace listing in the stable reinstall script" in result.output


def test_build_plugin_emits_codex_plugin_layout(tmp_path: Path) -> None:
    output = tmp_path / "plugin"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build",
            "plugin",
            "--target",
            "codex",
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
        ],
    )

    assert result.exit_code == 0, result.output
    assert "Produced Artifact" in result.output
    assert "Codex plugin generated, not installed." not in result.output
    assert "Before install:" not in result.output
    assert "Recommended Codex install path:" not in result.output
    assert "run drift before any postprocess" not in result.output
    assert "codex plugin marketplace list" not in result.output
    assert "codex plugin add forma@<marketplace-name>" not in result.output
    assert "Forma does not install Codex plugins" not in result.output
    assert "Next:" not in result.output
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


def test_build_plugin_json_outputs_codex_handoff_next_actions(tmp_path: Path) -> None:
    output = tmp_path / "plugin"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build",
            "plugin",
            "--target",
            "codex",
            "--output",
            str(output),
            "--methodology",
            str(METHODOLOGY),
            "--format",
            "json",
        ],
    )

    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["schema"] == "forma.actionable-report.v1"
    assert payload["command"] == "forma build plugin"
    assert _report_section(payload, "produced-artifact")["artifact_kind"] == "codex-plugin"
    commands = {
        action.get("command")
        for action in payload["next_actions"]
        if "command" in action
    }
    assert "forma verify " + str(output) in commands
    assert "codex plugin marketplace list" not in commands
    assert "codex plugin add <confirmed-plugin-id>@<confirmed-marketplace>" in commands
    assert any(
        action["title"] == "confirm Codex plugin install facts"
        and "marketplace source" in action.get("description", "")
        for action in payload["next_actions"]
    )
    assert any(
        "do not install Codex plugins with forma install" in action.get("forbidden", [])
        for action in payload["next_actions"]
    )
    assert any(
        "do not leave plugin id, marketplace, selector, or source refresh decisions open"
        in " ".join(action.get("forbidden", []))
        for action in payload["next_actions"]
    )


def test_build_plugin_with_forma_self_profile_uses_emitted_skills(
    tmp_path: Path,
) -> None:
    output = tmp_path / "plugin"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build",
            "plugin",
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
    assert "Produced Artifact" in result.output
    assert "Profile-Local Reinstall Workflow" not in result.output
    assert f"profile_dir: {ROOT / '.forma'}" not in result.output
    assert "script: reinstall-workflow.sh" not in result.output
    assert "state: reusable" not in result.output
    assert "run profile-local reinstall workflow" not in result.output
    assert "Next:" not in result.output
    assert (output / "skills" / "plan" / "SKILL.md").is_file()
    assert (output / "skills" / "showhand" / "SKILL.md").is_file()
    assert (output / "skills" / "reconcile" / "SKILL.md").is_file()
    assert (output / "skills" / "rework" / "SKILL.md").is_file()
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
            "build",
            "bundle",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "plugin",
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
            "build",
            "bundle",
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
    assert fresh_data["next_actions"][0]["title"] == "no drift remediation required"

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
    assert stale_data["next_actions"][0]["title"] == "regenerate stale artifact"
    assert stale_data["next_actions"][0]["requires_confirmation"] is True
    assert stale_data["next_actions"][0]["interaction"] == INTERACTION_CHOICE
    assert "regenerate and verify" in stale_data["next_actions"][0]["confirmation_prompt"]


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
    assert data["next_actions"][0]["title"] == "provide source for full drift proof"


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
    assert not any("/dist/skills/" in path for path in paths)
    assert any(path.endswith("dist/skill-bundles/opencode") for path in paths)
    assert any(path.endswith("dist/plugins/codex/forma") for path in paths)
    assert any(path.endswith("dist/plugins/claude-code/forma") for path in paths)
    assert {item["status"] for item in data["artifacts"]} <= {
        "fresh",
        "stale",
        "invalid",
        "unknown-source",
    }
    assert data["next_actions"]


def test_doctor_rejects_removed_subcommands(tmp_path: Path) -> None:
    runner = CliRunner()

    repo = runner.invoke(main, ["doctor", "repo", str(tmp_path)])
    artifact = runner.invoke(main, ["doctor", "artifact", str(VALID_BUNDLE)])

    assert repo.exit_code != 0
    assert artifact.exit_code != 0


def test_doctor_reports_ready_without_forma_profile_when_core_contracts_exist(
    tmp_path: Path,
) -> None:
    (tmp_path / "AGENTS.md").write_text(
        """# AGENTS

## Read First
- README.md
- STRUCTURE.md

## Source Boundaries
- Source lives in src.
- Generated output lives in dist and should not be edited by default.

## Validation
- Run `uv run --extra dev python -m pytest -p no:cacheprovider tests/`.

## Human Gates
- Ask for human approval before destructive, release, credential, or external-write actions.

## Handoff
- Return findings and proof before completion.
""",
        encoding="utf-8",
    )
    (tmp_path / "STRUCTURE.md").write_text(
        "source: src\ngenerated: dist\nwritable: tests\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "Validate with `uv run --extra dev python -m pytest -p no:cacheprovider tests/`.\n",
        encoding="utf-8",
    )
    (tmp_path / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
    (tmp_path / "plans").mkdir()
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    validate = scripts / "validate.sh"
    validate.write_text("#!/usr/bin/env sh\npytest\n", encoding="utf-8")
    validate.chmod(0o755)
    runner = CliRunner()

    human = runner.invoke(main, ["doctor", str(tmp_path)])
    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert human.exit_code == 0, human.output
    assert "repo has core agent-operability contracts" in human.output
    assert "status: ready" in human.output
    assert "forma explain agent --target codex|claude-code|opencode" in human.output
    assert "forma doctor --format agent <repo>" in human.output
    assert "Doctor readiness covers operability" in human.output
    assert "Hand the agent report" not in human.output
    assert "Workflow adoption:" in human.output
    assert "Forma adoption:" in human.output
    assert "Forma turns this repository's engineering rules into a reusable agent workflow" in human.output
    assert "work is less likely to drift, easier to review, and more consistently validated" in human.output
    assert "Do not ask whether to keep `.forma`; keep it by default" in human.output
    assert "Tell the owner Forma can manage this repo's engineering rules" in human.output
    data = json.loads(result.output)
    assert result.exit_code == 0, result.output
    assert data["schema"] == "forma.repo-doctor.report.v1"
    assert data["command"] == "forma doctor"
    assert data["status"] == "ready"
    assert data["agent_handoffs"] == []
    assert data["programmatic_actions"]
    assert data["facts"]["forma_adoption"]["status"] == "missing"
    assert "create `.forma` workflow source" in data["facts"]["forma_adoption"][
        "owner_confirmations"
    ][0]
    assert (
        "reviewed project engineering rules can become an installable agent workflow"
        in data["programmatic_actions"][0]["description"]
    )
    findings = {item["domain"]: item for item in data["findings"]}
    assert findings["entrypoint"]["status"] == "contract"
    assert findings["validation"]["status"] == "contract"
    assert findings["agent-specific-integrations.forma"]["status"] == "optional"
    assert findings["agent-specific-integrations.forma"]["evidence"] == []
    assert "create it to manage project rules as an installable agent workflow" in findings[
        "agent-specific-integrations.forma"
    ]["summary"]
    assert data["facts"]["agent_instruction_quality"]["status"] == "contract"
    assert "OpenAI Codex AGENTS.md guidance" in data["facts"]["agent_instruction_quality"]["basis"]
    assert "purpose_sources" in data["facts"]
    assert "maintenance_semantic_prompts" in data["facts"]
    assert "repository purpose and primary deliverables" in data["facts"][
        "maintenance_semantic_prompts"
    ]


def test_doctor_follows_entrypoint_document_links_for_handoff_and_evidence(
    tmp_path: Path,
) -> None:
    (tmp_path / "AGENTS.md").write_text(
        """# AGENTS

Before work, read [docs/INDEX.md](docs/INDEX.md).
Ask for human approval before destructive, release, credential, or external-write actions.
""",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    references = docs / "references"
    references.mkdir(parents=True)
    (docs / "INDEX.md").write_text(
        """# Docs Index

| Document | Purpose |
| --- | --- |
| [ARCHITECTURE.md](./ARCHITECTURE.md) | source boundaries and dependency rules |
| [references/OPERATIONS.md](./references/OPERATIONS.md) | validation commands |
""",
        encoding="utf-8",
    )
    (docs / "ARCHITECTURE.md").write_text(
        """Source boundaries: source lives in src, generated output lives in dist.

Read [deep boundary rules](./references/BOUNDARIES.md).
""",
        encoding="utf-8",
    )
    (references / "BOUNDARIES.md").write_text(
        "Generated output rules live in [generated policy](./GENERATED.md).\n",
        encoding="utf-8",
    )
    (references / "GENERATED.md").write_text(
        """Do not edit generated output directly.

Example implementation: [api_topic.go](../../common/banner/handler/api_topic.go).
""",
        encoding="utf-8",
    )
    code_dir = tmp_path / "common" / "banner" / "handler"
    code_dir.mkdir(parents=True)
    (code_dir / "api_topic.go").write_text("package handler\n", encoding="utf-8")
    (references / "OPERATIONS.md").write_text(
        "Run `GOCACHE=/tmp/mimir-gocache go test <touched-packages> -count=1`.\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# sample\n", encoding="utf-8")
    (tmp_path / "go.mod").write_text("module sample\n\ngo 1.23.7\n", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert "STRUCTURE.md" not in data["agent_handoffs"][0]["read_first"]
    assert data["facts"]["entrypoint_references"] == [
        "docs/INDEX.md",
        "docs/ARCHITECTURE.md",
        "docs/references/OPERATIONS.md",
        "docs/references/BOUNDARIES.md",
        "docs/references/GENERATED.md",
    ]
    assert "common/banner/handler/api_topic.go" not in data["facts"]["entrypoint_references"]
    assert data["agent_handoffs"][0]["read_first"] == [
        "AGENTS.md",
        "README.md",
        "docs/INDEX.md",
        "docs/ARCHITECTURE.md",
        "docs/references/OPERATIONS.md",
        "docs/references/BOUNDARIES.md",
        "docs/references/GENERATED.md",
    ]
    assert "docs/INDEX.md" in data["facts"]["purpose_sources"]
    assert "docs/ARCHITECTURE.md" in data["facts"]["purpose_sources"]
    findings = {item["domain"]: item for item in data["findings"]}
    assert findings["entrypoint"]["status"] == "contract"
    assert "docs/INDEX.md" in findings["entrypoint"]["evidence"]
    assert findings["entrypoint-reference-quality"]["status"] == "contract"
    assert data["facts"]["entrypoint_reference_quality"]["status"] == "contract"
    assert "reported references must be existing local Markdown files" in data["facts"][
        "entrypoint_reference_quality"
    ]["criteria"]
    assert data["facts"]["agent_instruction_quality"]["status"] == "contract"
    assert "provider discovery should be explicit" in " ".join(
        data["facts"]["agent_instruction_quality"]["criteria"]
    )
    assert findings["source-boundaries"]["status"] == "contract"
    assert "docs/ARCHITECTURE.md" in findings["source-boundaries"]["evidence"]
    assert "docs/references/GENERATED.md" in findings["source-boundaries"]["evidence"]
    assert findings["validation"]["status"] == "contract"
    assert findings["validation"]["evidence"] == ["docs/references/OPERATIONS.md"]
    agent = runner.invoke(main, ["doctor", "--format", "agent", str(tmp_path)])
    assert agent.exit_code == 0, agent.output
    assert "instruction_quality:" in agent.output
    assert "standard: provider-informed heuristic, not a universal agent standard" in agent.output
    assert "OpenAI Codex AGENTS.md guidance" in agent.output
    assert "Claude Code reads CLAUDE.md" in agent.output
    assert "reference_quality:" in agent.output
    assert "standard: traversal-safety diagnostic for agent read-first Markdown" in agent.output
    assert "reported references must be existing local Markdown files" in agent.output
    assert "issues:" in agent.output
    assert "forma_adoption:" in agent.output
    assert "Forma turns this repository's engineering rules into a reusable agent workflow" in agent.output
    assert "The agent no longer needs repeated reminders about boundaries" in agent.output


def test_doctor_stops_entrypoint_document_cycles(
    tmp_path: Path,
) -> None:
    (tmp_path / "AGENTS.md").write_text(
        """# AGENTS

Before work, read [docs/INDEX.md](docs/INDEX.md).
Ask for human approval before destructive actions.
""",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "INDEX.md").write_text(
        """# Docs Index

Read [architecture](./ARCHITECTURE.md).
""",
        encoding="utf-8",
    )
    (docs / "ARCHITECTURE.md").write_text(
        """Source boundaries: source lives in src, generated output lives in dist.

Read [operations](./OPERATIONS.md).
""",
        encoding="utf-8",
    )
    (docs / "OPERATIONS.md").write_text(
        """Run `go test <touched-packages>`.

Read [architecture](./ARCHITECTURE.md).
""",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("# sample\n", encoding="utf-8")
    (tmp_path / "go.mod").write_text("module sample\n\ngo 1.23.7\n", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["facts"]["entrypoint_references"] == [
        "docs/INDEX.md",
        "docs/ARCHITECTURE.md",
        "docs/OPERATIONS.md",
    ]
    assert data["facts"]["entrypoint_reference_cycles"] == [
        {
            "path": [
                "AGENTS.md",
                "docs/INDEX.md",
                "docs/ARCHITECTURE.md",
                "docs/OPERATIONS.md",
                "docs/ARCHITECTURE.md",
            ]
        }
    ]
    assert data["facts"]["entrypoint_references"].count("docs/ARCHITECTURE.md") == 1
    assert data["facts"]["entrypoint_reference_quality"]["status"] == "warning"
    assert data["facts"]["entrypoint_reference_quality"]["issues"] == [
        "cycle(s) detected; repeated Markdown edges were skipped"
    ]
    findings = {item["domain"]: item for item in data["findings"]}
    assert findings["entrypoint"]["status"] == "contract"
    assert findings["entrypoint-reference-quality"]["status"] == "warning"
    assert "docs/OPERATIONS.md" in findings["entrypoint-reference-quality"]["evidence"]


def test_doctor_reports_provider_informed_instruction_quality_issues(
    tmp_path: Path,
) -> None:
    (tmp_path / "AGENTS.md").write_text(
        "\n".join(["plain instruction text without Markdown structure"] * 201),
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    quality = data["facts"]["agent_instruction_quality"]
    assert quality["status"] == "warning"
    assert "AGENTS.md exceeds 200 lines" in quality["issues"]
    assert "AGENTS.md is not clearly structured Markdown" in quality["issues"]
    assert "no concrete validation command found in entrypoints or referenced Markdown" in quality[
        "issues"
    ]
    findings = {item["domain"]: item for item in data["findings"]}
    assert findings["instruction-quality"]["status"] == "warning"
    assert "provider-informed criteria" in findings["instruction-quality"]["handoff"]


def test_doctor_discovers_nested_agent_entrypoints(
    tmp_path: Path,
) -> None:
    service = tmp_path / "services" / "checkout"
    service.mkdir(parents=True)
    (service / "AGENTS.md").write_text(
        """# Checkout Agent Rules

Read first: README.md.
Validation: run `go test ./services/checkout -count=1`.
Ask a human before destructive operations.
""",
        encoding="utf-8",
    )
    ignored = tmp_path / "vendor" / "pkg"
    ignored.mkdir(parents=True)
    (ignored / "AGENTS.md").write_text("Read first: ignored.\n", encoding="utf-8")
    (tmp_path / "README.md").write_text("# sample\n", encoding="utf-8")
    (tmp_path / "go.mod").write_text("module sample\n\ngo 1.23.7\n", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["facts"]["root_entrypoints"] == []
    assert data["facts"]["local_entrypoints"] == ["services/checkout/AGENTS.md"]
    assert data["facts"]["entrypoints"] == ["services/checkout/AGENTS.md"]
    findings = {item["domain"]: item for item in data["findings"]}
    assert findings["entrypoint"]["status"] == "contract"
    assert findings["validation"]["status"] == "contract"


def test_doctor_does_not_treat_forma_profile_as_core_readiness(
    tmp_path: Path,
) -> None:
    (tmp_path / "pyproject.toml").write_text("[project]\nname='sample'\n", encoding="utf-8")
    profile_dir = tmp_path / ".forma"
    profile_dir.mkdir()
    (profile_dir / "profile.yaml").write_text("profile:\n  id: sample\n", encoding="utf-8")
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["status"] == "needs-agent"
    findings = {item["domain"]: item for item in data["findings"]}
    assert findings["entrypoint"]["status"] == "missing"
    assert findings["validation"]["status"] == "signal"
    assert findings["agent-specific-integrations.forma"]["status"] == "optional"
    assert findings["agent-specific-integrations.forma"]["evidence"] == [".forma/profile.yaml"]
    assert data["facts"]["forma_adoption"]["status"] == "present"
    assert "Do not ask whether to keep `.forma`; keep it by default" in data["facts"][
        "forma_adoption"
    ]["cleanup_policy"]
    assert "confirm profile refinement from the current project rules" in data["facts"][
        "forma_adoption"
    ]["owner_confirmations"]


def test_doctor_routes_existing_forma_profile_to_coverage_review(
    tmp_path: Path,
) -> None:
    (tmp_path / "AGENTS.md").write_text(
        """# AGENTS

Read first: [docs/AGENTS.md](docs/AGENTS.md).

## Source Boundaries
- Source lives in src.
- Generated output lives in dist.

## Validation
- Run `pytest`.

## Human Gates
- Ask for human approval before destructive, release, credential, or external-write actions.

## Handoff
- Return findings and proof before completion.
""",
        encoding="utf-8",
    )
    docs = tmp_path / "docs"
    docs.mkdir()
    (docs / "AGENTS.md").write_text(
        """# Docs Rules

Read [frontend constraints](dev/frontend.md) before frontend work.
Generated output belongs in dist.
Ask for approval before durable rule adoption.
""",
        encoding="utf-8",
    )
    (docs / "dev").mkdir()
    (docs / "dev" / "frontend.md").write_text(
        "Run rendered UI checks before accepting frontend work.\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text("Validate with `pytest`.\n", encoding="utf-8")
    (tmp_path / "STRUCTURE.md").write_text(
        "source: src\ngenerated: dist\nwritable: tests\n",
        encoding="utf-8",
    )
    (tmp_path / "plans").mkdir()
    scripts = tmp_path / "scripts"
    scripts.mkdir()
    validate = scripts / "validate.sh"
    validate.write_text("#!/usr/bin/env sh\nexit 0\n", encoding="utf-8")
    validate.chmod(0o755)
    profile_dir = tmp_path / ".forma"
    profile_dir.mkdir()
    (profile_dir / "profile.yaml").write_text(
        "profile:\n  id: sample\nconstraints:\n  default:\n    - Keep source and generated output separate.\n",
        encoding="utf-8",
    )
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["status"] == "ready"
    assert data["terminal"] is False
    assert data["terminal_reason"] == "primary_handoff_required"
    assert data["next_required_action"] == HANDOFF_KIND_PROFILE_REFINEMENT
    assert data["agent_handoffs"][0]["title"] == HANDOFF_TITLE_PROFILE_REFINEMENT
    assert data["agent_handoffs"][0]["handoff_kind"] == HANDOFF_KIND_PROFILE_REFINEMENT
    assert data["agent_handoffs"][0]["read_first"] == [
        "AGENTS.md",
        "docs/AGENTS.md",
        "README.md",
        "docs/dev/frontend.md",
        ".forma/profile.yaml",
    ]
    assert (
        "forma explain profile --format agent --target <target>"
        in data["agent_handoffs"][0]["questions"][0]
    )
    assert "Compare existing Forma profile source" in data["agent_handoffs"][0]["questions"][1]
    assert "exact headings" in data["agent_handoffs"][0]["questions"][2]
    assert "generic findings or suggestions" in data["agent_handoffs"][0]["questions"][2]
    assert "exactly two child lines" in data["agent_handoffs"][0]["questions"][3]
    assert "Offer: Should I <perform that action> now?" in data["agent_handoffs"][0][
        "questions"
    ][3]
    assert "structured user-input" in data["agent_handoffs"][0]["questions"][4]
    assert "Required Confirmation" in data["agent_handoffs"][0]["questions"][4]
    assert "artifact validation" in data["agent_handoffs"][0]["forbidden"][0]
    assert data["agent_handoffs"][0]["return_shape"]["profile_review"].startswith(
        "incremental review"
    )
    assert data["agent_handoffs"][0]["return_shape"]["proposal"].startswith(
        "minimal Profile YAML Proposal"
    )
    assert data["agent_handoffs"][0]["return_shape"]["recommended_next_step"].startswith(
        "exactly two child lines"
    )
    assert "Offer is an explicit question" in data["agent_handoffs"][0]["return_shape"][
        "recommended_next_step"
    ]
    assert data["agent_handoffs"][0]["return_shape"]["user_interaction"].startswith(
        "use host structured confirmation"
    )
    assert data["agent_handoffs"][0]["next_action"]["handoff_kind"] == HANDOFF_KIND_PROFILE_REFINEMENT
    assert data["agent_handoffs"][0]["next_action"]["requires_confirmation"] is True
    assert data["agent_handoffs"][0]["next_action"]["interaction"] == INTERACTION_CHOICE
    assert "profile delta" in data["agent_handoffs"][0]["next_action"][
        "confirmation_prompt"
    ]

    agent = runner.invoke(main, ["doctor", "--format", "agent", str(tmp_path)])

    assert agent.exit_code == 0, agent.output
    assert "terminal: false" in agent.output
    assert "terminal_reason: primary_handoff_required" in agent.output
    assert f"next_required_action: {HANDOFF_KIND_PROFILE_REFINEMENT}" in agent.output
    assert f"primary_handoff: {HANDOFF_TITLE_PROFILE_REFINEMENT}" in agent.output
    assert f"primary_handoff_kind: {HANDOFF_KIND_PROFILE_REFINEMENT}" in agent.output
    assert "Follow the primary handoff before summarizing findings" in agent.output
    assert "load `forma explain profile --format agent --target <target>` next" in agent.output
    assert "final answer must use the exact section headings" in agent.output
    assert "host structured user-input" in agent.output
    assert "do not reroute back through `forma explain agent`" in agent.output
    assert f"handoff: {HANDOFF_TITLE_PROFILE_REFINEMENT}" in agent.output
    assert f"handoff_kind: {HANDOFF_KIND_PROFILE_REFINEMENT}" in agent.output
    assert agent.output.index(f"primary_handoff: {HANDOFF_TITLE_PROFILE_REFINEMENT}") < agent.output.index(
        "continuation:"
    )
    assert agent.output.index(f"handoff: {HANDOFF_TITLE_PROFILE_REFINEMENT}") < agent.output.index(
        "findings:"
    )
    assert "Load `forma explain profile --format agent --target <target>`" in agent.output
    assert "profile_review: incremental review from `forma explain profile`" in agent.output
    assert "recommended_next_step: exactly two child lines" in agent.output
    assert "user_interaction: use host structured confirmation" in agent.output
    assert "next_action:" in agent.output
    assert "requires_confirmation: true" in agent.output
    assert "confirmation_prompt: Should I apply the reviewed profile delta now?" in agent.output
    assert "Offer is an explicit question" in agent.output

    human = runner.invoke(main, ["doctor", str(tmp_path)])

    assert human.exit_code == 0, human.output
    assert "Continue the profile refinement review" in human.output
    assert "End with a recommended next step" in human.output


def test_doctor_reports_needs_agent_for_sparse_repo(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    data = json.loads(result.output)
    assert data["status"] == "needs-agent"
    assert data["schema"] == "forma.repo-doctor.report.v1"
    findings = {item["domain"]: item for item in data["findings"]}
    assert {
        "entrypoint",
        "task-state",
        "source-boundaries",
        "validation",
        "setup-contract",
        "human-gates",
        "noise-control",
        "instruction-quality",
        "tooling-signals",
    } <= set(findings)
    assert findings["entrypoint"]["status"] == "missing"
    assert data["agent_handoffs"][0]["questions"]

    human = runner.invoke(main, ["doctor", str(tmp_path)])
    agent = runner.invoke(main, ["doctor", "--format", "agent", str(tmp_path)])
    assert human.exit_code == 0, human.output
    assert "Continue the Agent remediation review" in human.output
    assert "do not return unresolved findings as the final diagnosis" in human.output
    assert agent.exit_code == 0, agent.output
    assert "guide: forma explain agent" in agent.output
    assert "targeted_guide: forma explain agent --target codex|claude-code|opencode" in agent.output
    assert "terminal: false" in agent.output
    assert "Treat findings as investigation inputs" in agent.output
    assert "Follow the primary handoff before summarizing findings" in agent.output
    assert "Assign dispositions to non-contract core findings after the primary handoff" in agent.output
    assert "valid dispositions are confirmed, resolved, not applicable" in agent.output
    assert "project_understanding:" in agent.output
    assert "semantic_dimensions:" in agent.output
    assert "what this repository is for and what it delivers" in agent.output
    assert "profile_boundary: if a candidate profile only encodes doctor findings" in agent.output
    assert "actions:" in agent.output
    assert "Do not return this handoff unchanged as the final user answer" in agent.output


def test_init_dry_run_reports_git_trackable_profile_source_without_writing(
    tmp_path: Path,
) -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["init", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    assert not (tmp_path / ".forma").exists()
    assert not (tmp_path / ".forma-profile").exists()
    data = json.loads(result.output)
    assert data["command"] == "forma init"
    assert data["status"] == "needs-human"
    assert "does not review or approve a profile" in data["warnings"][0]
    changes = _report_section(data, "planned-changes")
    items = changes["items"]
    assert any(item["path"] == ".forma/.gitignore" for item in items)
    assert any(item["path"] == ".forma/profile.yaml" for item in items)
    assert any(item["path"] == ".forma/reinstall-workflow.sh" for item in items)
    assert not any("review-packet.md" in item["path"] for item in items)
    assert not any(item["path"] == ".forma/config.yaml" for item in items)
    assert not any(".forma-profile" in item["path"] for item in items)
    assert not any("agent-handoff" in item["path"] for item in items)
    assert not any("/handoff/" in item["path"] for item in items)
    assert all(item["action"] == "plan-create" for item in items)


def test_init_apply_creates_draft_profile_skeletons(tmp_path: Path) -> None:
    runner = CliRunner()

    result = runner.invoke(main, ["init", "--apply", "--format", "json", str(tmp_path)])

    assert result.exit_code == 0, result.output
    profile = tmp_path / ".forma" / "profile.yaml"
    gitignore = tmp_path / ".forma" / ".gitignore"
    agent_handoff = tmp_path / ".forma" / "handoff" / "agent-handoff.md"
    reinstall = tmp_path / ".forma" / "reinstall-workflow.sh"
    assert not (tmp_path / ".forma" / "config.yaml").exists()
    assert gitignore.read_text(encoding="utf-8") == "/state/\n"
    assert not (tmp_path / ".forma-profile").exists()
    assert "Draft local Forma profile" in profile.read_text(encoding="utf-8")
    assert not (tmp_path / ".forma" / "review" / "review-packet.md").exists()
    assert not agent_handoff.exists()
    reinstall_text = reinstall.read_text(encoding="utf-8")
    assert "FORMA_REINSTALL_WORKFLOW_BOOTSTRAP_INCOMPLETE=1" in reinstall_text
    assert "This reinstall-workflow.sh is bootstrap-incomplete." in reinstall_text
    assert "artifact kind" in reinstall_text
    assert "marketplace source" in reinstall_text
    assert "install selector" in reinstall_text
    assert "visibility check" in reinstall_text
    assert "not list marketplaces" in reinstall_text
    assert "exit 3" in reinstall_text
    assert "FORMA_ARTIFACT" not in reinstall_text
    assert "codex plugin marketplace list" not in reinstall_text
    assert reinstall.stat().st_mode & 0o111
    data = json.loads(result.output)
    changes = _report_section(data, "applied-changes")
    assert all(item["action"] == "create" for item in changes["items"])


def test_init_from_report_dry_run_plans_agent_operability_inputs(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    doctor = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])
    report_path = tmp_path / "forma-doctor.json"
    report_path.write_text(doctor.output, encoding="utf-8")

    result = runner.invoke(
        main,
        [
            "init",
            "--from-report",
            str(report_path),
            "--format",
            "json",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert not (tmp_path / ".forma").exists()
    data = json.loads(result.output)
    assert data["status"] == "needs-agent"
    assert any("workflow source and handoff files" in item for item in data["warnings"])
    assert any("Agent remediation is still required" in item for item in data["warnings"])
    changes = _report_section(data, "planned-changes")
    paths = {item["path"] for item in changes["items"]}
    assert ".forma/agent-operability/doctor-report.json" in paths
    assert ".forma/agent-operability/agent-handoff.md" in paths
    assert ".forma/agent-operability/human-decisions.md" in paths
    handoff = _report_section(data, "agent-operability-handoff")
    assert handoff["facts_file"] == ".forma/agent-operability/doctor-report.json"
    assert handoff["agent_handoff"] == ".forma/agent-operability/agent-handoff.md"
    assert handoff["human_decisions"] == ".forma/agent-operability/human-decisions.md"


def test_init_from_report_apply_writes_sanitized_handoff_inputs(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    doctor = runner.invoke(main, ["doctor", "--format", "json", str(tmp_path)])
    report_path = tmp_path / "forma-doctor.json"
    report_path.write_text(doctor.output, encoding="utf-8")

    result = runner.invoke(
        main,
        [
            "init",
            "--from-report",
            str(report_path),
            "--apply",
            "--format",
            "json",
            str(tmp_path),
        ],
    )

    assert result.exit_code == 0, result.output
    assert (tmp_path / ".forma" / "profile.yaml").exists()
    assert (tmp_path / ".forma" / ".gitignore").exists()
    assert (tmp_path / ".forma" / "reinstall-workflow.sh").exists()
    tracked_report = tmp_path / ".forma" / "agent-operability" / "doctor-report.json"
    agent_handoff = tmp_path / ".forma" / "agent-operability" / "agent-handoff.md"
    human_decisions = tmp_path / ".forma" / "agent-operability" / "human-decisions.md"
    assert tracked_report.exists()
    assert agent_handoff.exists()
    assert human_decisions.exists()
    report_text = tracked_report.read_text(encoding="utf-8")
    report_data = json.loads(report_text)
    assert report_data["subject"] == "."
    assert str(tmp_path) not in report_text
    handoff_text = agent_handoff.read_text(encoding="utf-8")
    assert "handoff input for Agent remediation" in handoff_text
    assert "not approved durable project rules" in handoff_text
    assert "Owner confirmations" in handoff_text
    assert (tmp_path / ".forma" / "agent-operability" / "human-decisions.md").read_text(
        encoding="utf-8"
    ).startswith("# Owner Confirmations")


def test_init_from_report_rejects_wrong_schema(tmp_path: Path) -> None:
    runner = CliRunner()
    report_path = tmp_path / "forma-doctor.json"
    report_path.write_text(
        json.dumps(
            {
                "schema": "wrong",
                "command": "forma doctor",
                "subject": str(tmp_path),
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(main, ["init", "--from-report", str(report_path), str(tmp_path)])

    assert result.exit_code == 1
    assert "unsupported doctor report schema" in result.output


def test_init_from_report_rejects_subject_mismatch(tmp_path: Path) -> None:
    runner = CliRunner()
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.mkdir()
    target.mkdir()
    doctor = runner.invoke(main, ["doctor", "--format", "json", str(source)])
    report_path = tmp_path / "forma-doctor.json"
    report_path.write_text(doctor.output, encoding="utf-8")

    result = runner.invoke(main, ["init", "--from-report", str(report_path), str(target)])

    assert result.exit_code == 1
    assert "doctor report does not match init target" in result.output


def test_build_plugin_emits_claude_code_plugin_layout(tmp_path: Path) -> None:
    runner = CliRunner()
    output = tmp_path / "plugin"

    result = runner.invoke(
        main,
        [
            "build",
            "plugin",
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
    assert "forma install --target claude-code" not in result.output
    assert "Next:" not in result.output
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

    agent = runner.invoke(
        main,
        [
            "build",
            "plugin",
            "--target",
            "claude-code",
            "--output",
            str(tmp_path / "plugin-agent"),
            "--methodology",
            str(METHODOLOGY),
            "--format",
            "agent",
        ],
    )
    assert agent.exit_code == 0, agent.output
    assert "forma install --target claude-code" in agent.output


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
            "build",
            "bundle",
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
            "build",
            "bundle",
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
            "build",
            "bundle",
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
            "build",
            "bundle",
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
            "build",
            "bundle",
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
            "build",
            "plugin",
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
    assert "codex plugin marketplace list" not in install.output
    assert "Ask the user to choose an existing marketplace" not in install.output
    assert "When the reusable install path is missing or incomplete" in install.output
    assert "marketplace source" in install.output
    assert "developers.openai.com/codex/plugins/build#install-a-local-plugin-manually" in install.output
    assert "developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli" in install.output
    assert "codex plugin add forma@<confirmed-marketplace>" in install.output
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
            "build",
            "plugin",
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
    assert (
        "codex plugin add sample-backend-go-github-issue-tracked@<confirmed-marketplace>"
        in install.output
    )
