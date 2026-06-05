from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from forma.cli import main
from forma.creator import create_suite, load_profile
from forma.creator.manifest import find_methodology_dir
from forma_verifier import verify


ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = ROOT / "source" / "methodology"
SAMPLE_PROFILE = ROOT / "examples" / "profiles" / "sample-backend" / "sample-backend-go.yaml"
SAMPLE_CONDITIONAL_PROFILE = (
    ROOT / "examples" / "profiles" / "sample-backend" / "sample-conditional-overlay.yaml"
)
SAMPLE_SOFTWARE_PROFILE = (
    ROOT
    / "examples"
    / "profiles"
    / "sample-software"
    / "sample-software-plan-first.yaml"
)
FORMA_SELF_PROFILE = ROOT / "profiles" / "forma-self" / "forma-self-iteration.yaml"
COMMITTED_CODEX_OUTPUT = ROOT / "examples" / "generated" / "sample-backend-go-plan-first-codex"
COMMITTED_CLAUDE_OUTPUT = ROOT / "examples" / "generated" / "sample-backend-go-plan-first-claude-code"
KINDS = ("shape", "gauge", "seal", "pour", "flow")
SAMPLE_STAGE_DIRS = {
    "shape": "backend-plan-first-plan-issue",
    "gauge": "backend-plan-first-ground-plan",
    "seal": "backend-plan-first-finalize-plan",
    "pour": "backend-plan-first-implement-feature",
    "flow": "backend-plan-first-showhand",
}
SOFTWARE_STAGE_DIRS = {
    "shape": "software-plan-first-plan-issue",
    "gauge": "software-plan-first-ground-plan",
    "seal": "software-plan-first-finalize-plan",
    "pour": "software-plan-first-implement-feature",
    "flow": "software-plan-first-showhand",
}
FORMA_SELF_STAGE_DIRS = {
    "shape": "forma-shape",
    "gauge": "forma-gauge",
    "seal": "forma-seal",
    "pour": "forma-pour",
    "flow": "forma-flow",
}


def test_load_profile_resolves_sample_backend_go() -> None:
    profile = load_profile(SAMPLE_PROFILE)

    assert profile.profile_id == "sample-backend-go"
    assert profile.bundle_name == "sample-backend-go"
    assert profile.org_name == "Example Team"
    assert profile.resolved_order == (
        "sample-base",
        "sample-dev",
        "sample-backend",
        "sample-go",
        "sample-backend-go",
    )
    assert "repository" in profile.terminology
    assert "go test ./..." in profile.validation_commands["default"]
    assert any("API" in item for item in profile.constraints["shape"])
    assert profile.stages["shape"].name == "backend-plan-first-plan-issue"
    assert profile.stages["flow"].directory == "backend-plan-first-showhand"
    assert {
        resource.dest
        for resource in profile.resources["shape"]
    } == {"references/backend-rules.md", "references/backend-review-checks.md"}
    assert all("project-specific workflow" not in item for item in profile.constraints["default"])


def test_load_profile_resolves_sample_software_plan_first() -> None:
    profile = load_profile(SAMPLE_SOFTWARE_PROFILE)

    assert profile.profile_id == "sample-software-plan-first"
    assert profile.bundle_name == "sample-software-plan-first"
    assert profile.org_name == "Example Team"
    assert profile.resolved_order == (
        "sample-software-base",
        "sample-software",
        "sample-software-plan-first",
    )
    assert profile.stages["shape"].name == "software-plan-first-plan-issue"
    assert profile.stages["flow"].directory == "software-plan-first-showhand"
    assert "$software-plan-first-showhand" in profile.stages["flow"].default_prompt
    assert "Impact Profile" in profile.decision_gate_extras
    assert any("frontend, backend, fullstack, or generic" in item for item in profile.constraints["default"])
    assert {
        resource.dest
        for resource in profile.resources["shape"]
    } == {
        "references/software-control-model.md",
        "references/software-impact-profiles.md",
        "references/software-artifact-evidence-boundary.md",
        "references/software-feedback-and-proof.md",
    }


def test_load_profile_resolves_forma_self_iteration() -> None:
    profile = load_profile(FORMA_SELF_PROFILE)

    assert profile.profile_id == "forma-self-iteration"
    assert profile.bundle_name == "forma"
    assert profile.org_name == "Forma Maintainers"
    assert profile.resolved_order == (
        "forma-self-base",
        "forma-self-project",
        "forma-self-iteration-overlays",
        "forma-self-iteration",
    )
    assert profile.stages["shape"].name == "forma-shape"
    assert profile.stages["flow"].directory == "forma-flow"
    assert "$forma-flow" in profile.stages["flow"].default_prompt
    assert "Layer impact" in profile.decision_gate_extras
    assert any("profiles/forma-self" in item for item in profile.constraints["gauge"])
    assert profile.conditional_overlays is not None
    assert profile.conditional_overlays.decision.name == "Iteration Area"
    assert [route.id for route in profile.conditional_overlays.routes] == [
        "docs-only",
        "methodology-verifier",
        "creator-profile",
        "generated-baseline",
        "cross-layer",
    ]
    assert {
        resource.dest
        for resource in profile.resources["default"]
    } == {
        "references/forma-iteration-boundaries.md",
        "references/forma-validation-matrix.md",
        "references/forma-profile-policy.md",
    }


def test_profile_rejects_unknown_top_level_keys(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad.yaml"
    profile_file.write_text(
        """
profile:
  id: bad
mode: layered
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown top-level keys: mode"):
        load_profile(profile_file)


def test_profile_rejects_missing_include(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad.yaml"
    profile_file.write_text(
        """
profile:
  id: bad
includes:
  - missing
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="missing included profile"):
        load_profile(profile_file)


def test_profile_rejects_unknown_nested_keys(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad.yaml"
    profile_file.write_text(
        """
profile:
  id: bad
skills:
  shape:
    markdown: arbitrary template escape hatch
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="skills.shape has unknown keys: markdown"):
        load_profile(profile_file)


def test_profile_rejects_unknown_stage_keys(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad.yaml"
    profile_file.write_text(
        """
profile:
  id: bad
validation_commands:
  deploy:
    - make deploy
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="unknown keys: deploy"):
        load_profile(profile_file)


def test_profile_rejects_unknown_stage_config_keys(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad.yaml"
    profile_file.write_text(
        """
profile:
  id: bad
stages:
  shape:
    prompt_template: no arbitrary templates
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="stages.shape has unknown keys: prompt_template"):
        load_profile(profile_file)


def test_profile_rejects_missing_resource_source(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad.yaml"
    profile_file.write_text(
        """
profile:
  id: bad
resources:
  seal:
    scripts:
      - source: missing.sh
        dest: issue-workflow.sh
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="source does not exist"):
        load_profile(profile_file)


def test_profile_rejects_include_cycle(tmp_path: Path) -> None:
    (tmp_path / "a.yaml").write_text(
        """
profile:
  id: a
includes:
  - b
""".lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "b.yaml").write_text(
        """
profile:
  id: b
includes:
  - a
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="include cycle"):
        load_profile(tmp_path / "a.yaml")


def test_profile_merge_order_is_explicit_and_deterministic(tmp_path: Path) -> None:
    (tmp_path / "base.yaml").write_text(
        """
profile:
  id: base
bundle:
  name: base-bundle
constraints:
  default:
    - shared base rule
validation_commands:
  default:
    - pytest
skills:
  pour:
    description: Base pour description.
""".lstrip(),
        encoding="utf-8",
    )
    (tmp_path / "top.yaml").write_text(
        """
profile:
  id: top
includes:
  - base
bundle:
  name: top-bundle
constraints:
  default:
    - shared base rule
    - top rule
validation_commands:
  default:
    - pytest
    - mypy
skills:
  pour:
    description: Top pour description.
""".lstrip(),
        encoding="utf-8",
    )

    profile = load_profile(tmp_path / "top.yaml")

    assert profile.resolved_order == ("base", "top")
    assert profile.bundle_name == "top-bundle"
    assert profile.constraints["default"] == ["shared base rule", "top rule"]
    assert profile.validation_commands["default"] == ["pytest", "mypy"]
    assert profile.skill_descriptions["pour"] == "Top pour description."


def test_sample_profiles_are_sanitized() -> None:
    profile_text = "\n".join(
        path.read_text(encoding="utf-8")
        for pattern in ("*.yaml", "*.md")
        for path in sorted(
            (ROOT / "examples" / "profiles").rglob(pattern)
        )
    )

    assert "project-specific workflow" not in profile_text
    local_home_prefix = "/" + "Users" + "/"
    assert local_home_prefix not in profile_text
    assert "workflow skills" not in profile_text
    assert "sample-" not in profile_text


def test_sample_conditional_overlay_profile_emits_valid_suite(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-conditional-overlay-codex"

    create_suite(
        profile_file=SAMPLE_CONDITIONAL_PROFILE,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    shape_text = (output_dir / "forma-shape" / "SKILL.md").read_text(encoding="utf-8")
    seal_text = (output_dir / "forma-seal" / "SKILL.md").read_text(encoding="utf-8")
    pour_text = (output_dir / "forma-pour" / "SKILL.md").read_text(encoding="utf-8")

    assert (output_dir / "forma-shape" / "references" / "backend-rules.md").is_file()
    assert (output_dir / "forma-shape" / "references" / "dev-rules.md").is_file()
    assert (output_dir / "forma-shape" / "references" / "go-rules.md").is_file()
    assert 'name: "forma-shape"' in shape_text
    assert "Use the recorded `Plan Type`" in shape_text
    assert "If `Plan Type` is `generic-dev`, do not load overlay references." in shape_text
    assert "If `Plan Type` is `backend-non-go`, load:" in shape_text
    assert "If `Plan Type` is `backend-go`, load:" in shape_text
    assert "references/backend-rules.md" not in shape_text.split(
        "## Conditional References",
        1,
    )[0]
    conditional_section = shape_text.split("## Conditional References", 1)[1]
    assert "references/dev-rules.md" in conditional_section
    assert "references/backend-rules.md" in conditional_section
    assert "references/go-rules.md" in conditional_section
    assert "Record finalized `Plan Type` in `plan.md`" in seal_text
    assert "stop-for-plan-correction" in pour_text
    assert "pytest" in pour_text
    assert "python -m pytest tests/" in pour_text
    assert "go test ./..." in pour_text

    manifest = json.loads(
        (output_dir / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["profile"]["top_level_id"] == "sample-conditional-overlay"
    assert manifest["profile"]["resolved_order"] == ["sample-conditional-overlay"]
    assert manifest["emitted_skills"]["shape"]["directory"] == "forma-shape"
    assert manifest["conditional_overlays"]["decision"]["name"] == "Plan Type"
    assert manifest["conditional_overlays"]["routes"][1]["overlays"] == ["backend"]
    assert manifest["conditional_overlays"]["routes"][2]["overlays"] == [
        "dev",
        "backend",
        "go",
    ]
    assert manifest["conditional_overlays"]["routes"][1]["references"]["shape"] == [
        "references/backend-rules.md"
    ]
    assert manifest["conditional_overlays"]["routes"][2]["references"]["shape"] == [
        "references/dev-rules.md",
        "references/backend-rules.md",
        "references/go-rules.md",
    ]

    report = verify(output_dir)
    assert report.passed, report.format_human()


def test_sample_software_plan_first_profile_emits_valid_suite(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-software-plan-first-codex"

    manifest_path = create_suite(
        profile_file=SAMPLE_SOFTWARE_PROFILE,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    for kind, directory in SOFTWARE_STAGE_DIRS.items():
        assert (output_dir / directory / "SKILL.md").is_file()
        assert (output_dir / directory / "agents" / "openai.yaml").is_file()
    shape_text = (
        output_dir / SOFTWARE_STAGE_DIRS["shape"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    pour_text = (
        output_dir / SOFTWARE_STAGE_DIRS["pour"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    flow_text = (
        output_dir / SOFTWARE_STAGE_DIRS["flow"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    flow_agent = (
        output_dir / SOFTWARE_STAGE_DIRS["flow"] / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")

    assert 'name: "software-plan-first-plan-issue"' in shape_text
    assert "references/software-impact-profiles.md" in shape_text
    assert "frontend, backend, fullstack, or generic" in shape_text
    assert "review-ready after validation" in pour_text
    assert "showhand skip grounding" in flow_text
    assert "$software-plan-first-showhand" in flow_agent
    assert "sample-" not in shape_text
    assert "sample-" not in flow_agent

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["profile"]["top_level_id"] == "sample-software-plan-first"
    assert manifest["profile"]["resolved_order"] == [
        "sample-software-base",
        "sample-software",
        "sample-software-plan-first",
    ]
    assert (
        manifest["emitted_skills"]["shape"]["directory"]
        == "software-plan-first-plan-issue"
    )
    assert (
        "sample-software-plan-first.yaml"
        in manifest["profile"]["file_hashes"]
    )
    assert (
        "shape:references/software-impact-profiles.md"
        in manifest["profile"]["resource_hashes"]
    )
    report = verify(output_dir)
    assert report.passed, report.format_human()


def test_forma_self_iteration_profile_emits_valid_suites(tmp_path: Path) -> None:
    codex_dir = tmp_path / "forma-iteration-codex"
    claude_dir = tmp_path / "forma-iteration-claude-code"

    codex_manifest_path = create_suite(
        profile_file=FORMA_SELF_PROFILE,
        output_dir=codex_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    create_suite(
        profile_file=FORMA_SELF_PROFILE,
        output_dir=claude_dir,
        target_agent="claude-code",
        methodology_dir=METHODOLOGY,
    )

    for kind, directory in FORMA_SELF_STAGE_DIRS.items():
        assert (codex_dir / directory / "SKILL.md").is_file()
        assert (codex_dir / directory / "agents" / "openai.yaml").is_file()
        assert (claude_dir / directory / "SKILL.md").is_file()
        assert not (claude_dir / directory / "agents").exists()

    shape_text = (
        codex_dir / FORMA_SELF_STAGE_DIRS["shape"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    pour_text = (
        codex_dir / FORMA_SELF_STAGE_DIRS["pour"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    flow_agent = (
        codex_dir / FORMA_SELF_STAGE_DIRS["flow"] / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")

    assert 'name: "forma-shape"' in shape_text
    assert "references/forma-iteration-boundaries.md" in shape_text
    assert "Settle `Iteration Area`" in shape_text
    assert "If `Iteration Area` is `cross-layer`, apply `generated` overlay constraint" in pour_text
    assert "$forma-flow" in flow_agent

    manifest = json.loads(codex_manifest_path.read_text(encoding="utf-8"))
    assert manifest["profile"]["top_level_id"] == "forma-self-iteration"
    assert manifest["profile"]["resolved_order"] == [
        "forma-self-base",
        "forma-self-project",
        "forma-self-iteration-overlays",
        "forma-self-iteration",
    ]
    assert (
        manifest["emitted_skills"]["shape"]["directory"]
        == "forma-shape"
    )
    assert manifest["conditional_overlays"]["decision"]["name"] == "Iteration Area"
    assert manifest["conditional_overlays"]["routes"][4]["overlays"] == [
        "methodology",
        "verifier",
        "creator",
        "profiles",
        "generated",
        "docs",
    ]
    assert verify(codex_dir).passed
    assert verify(claude_dir).passed


def test_find_methodology_dir_accepts_explicit_path() -> None:
    assert find_methodology_dir(METHODOLOGY) == METHODOLOGY.resolve()


def test_creator_pipeline_emits_valid_codex_suite(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-backend-go-plan-first-codex"

    manifest_path = create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert manifest_path == output_dir / ".forma-manifest.json"
    for kind, directory in SAMPLE_STAGE_DIRS.items():
        assert (output_dir / directory / "SKILL.md").is_file()
        assert (output_dir / directory / "references" / "output-format.md").is_file()
        assert (output_dir / directory / "agents" / "openai.yaml").is_file()
    for kind in ("seal", "pour", "flow"):
        assert (
            output_dir / SAMPLE_STAGE_DIRS[kind] / "scripts" / "issue-workflow.sh"
        ).is_file()
    shape_text = (
        output_dir / SAMPLE_STAGE_DIRS["shape"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    pour_text = (
        output_dir / SAMPLE_STAGE_DIRS["pour"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    flow_text = (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    decision_gate = (
        output_dir
        / SAMPLE_STAGE_DIRS["shape"]
        / "references"
        / "proposal-decision-gate.md"
    ).read_text(encoding="utf-8")
    assert "## Requirements" in shape_text
    assert "public API behavior" in shape_text
    assert 'name: "backend-plan-first-plan-issue"' in shape_text
    assert "references/backend-rules.md" in shape_text
    assert "references/backend-review-checks.md" in shape_text
    assert "Load and follow `references/proposal-decision-gate.md`" in shape_text
    assert "Mandatory Decision Gate" not in shape_text
    assert "Mandatory Decision Gate" in decision_gate
    assert (
        output_dir / SAMPLE_STAGE_DIRS["seal"] / "references" / "task-structure.md"
    ).is_file()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["pour"] / "references" / "task-runner.md"
    ).is_file()
    assert (
        output_dir
        / SAMPLE_STAGE_DIRS["flow"]
        / "references"
        / "automated-execution.md"
    ).is_file()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["seal"] / "references" / "planning-rules.md"
    ).is_file()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["pour"] / "references" / "execution-rules.md"
    ).is_file()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["pour"] / "references" / "implement-notes.md"
    ).is_file()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "execution-rules.md"
    ).is_file()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "implement-notes.md"
    ).is_file()
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "workflow-rules.md"
    ).exists()
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "implement_notes.md"
    ).exists()
    assert "Add or update Go tests" in pour_text
    assert "contract, compatibility, data, or operational risk" in pour_text
    assert "already-finalized plan" in flow_text
    assert "Do not run `scripts/issue-workflow.sh init <issue-id>`" in flow_text
    assert "references/automated-execution.md" in flow_text
    assert "references/showhand-automation.md" not in flow_text
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "plan-template.md"
    ).exists()
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "tasks-template.md"
    ).exists()
    assert "showhand is execution-only for an already-finalized plan" in (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "scripts" / "issue-workflow.sh"
    ).read_text(encoding="utf-8")

    report = verify(output_dir)
    assert report.passed, report.format_human()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["format"] == "forma-suite-manifest-v1"
    assert manifest["mode"] == "solo"
    assert manifest["suite_kind"] == "plan-first"
    assert manifest["target"] == "codex"
    assert manifest["methodology_version"] == "0.1.0"
    assert manifest["generator_version"] == "0.1.0"
    assert manifest["methodology_source_revision_type"] == "git-short-sha"
    assert manifest["methodology_source_revision"]
    assert manifest["methodology_tree_digest"]
    generated_at = _parse_generated_at(manifest["generated_at"])
    assert generated_at <= datetime.now(timezone.utc) + timedelta(minutes=1)
    assert manifest["profile"]["top_level_id"] == "sample-backend-go"
    assert manifest["emitted_skills"]["shape"]["name"] == "backend-plan-first-plan-issue"
    assert (
        manifest["emitted_skills"]["flow"]["directory"]
        == "backend-plan-first-showhand"
    )
    assert manifest["profile"]["resolved_order"] == [
        "sample-base",
        "sample-dev",
        "sample-backend",
        "sample-go",
        "sample-backend-go",
    ]
    assert "sample-backend-go.yaml" in manifest["profile"]["file_hashes"]
    assert "backend.yaml" in manifest["profile"]["file_hashes"]
    assert (
        manifest["profile"]["resource_hashes"]["shape:references/backend-rules.md"]
        == manifest["profile"]["resource_hashes"]["seal:references/backend-rules.md"]
    )
    assert manifest["skills"] == list(KINDS)


def test_creator_pipeline_emits_valid_claude_code_suite(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-backend-go-plan-first-claude-code"

    create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=output_dir,
        target_agent="claude-code",
        methodology_dir=METHODOLOGY,
    )

    for directory in SAMPLE_STAGE_DIRS.values():
        assert (output_dir / directory / "SKILL.md").is_file()
        assert not (output_dir / directory / "agents").exists()
        assert not (output_dir / directory / "interfaces").exists()
    report = verify(output_dir)
    assert report.passed, report.format_human()
    manifest = json.loads((output_dir / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["target"] == "claude-code"


def test_creator_honors_custom_stage_names_and_enabled_matrix(tmp_path: Path) -> None:
    profile_file = tmp_path / "custom.yaml"
    profile_file.write_text(
        """
profile:
  id: custom
stages:
  shape:
    name: custom-plan-issue
    directory: custom-plan-issue
    display_name: Custom Plan Issue
  gauge:
    enabled: false
  seal:
    enabled: false
  pour:
    enabled: false
  flow:
    enabled: false
""".lstrip(),
        encoding="utf-8",
    )
    output_dir = tmp_path / "custom-output"

    create_suite(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert (output_dir / "custom-plan-issue" / "SKILL.md").is_file()
    assert not (output_dir / "shape").exists()
    skill_text = (output_dir / "custom-plan-issue" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert 'name: "custom-plan-issue"' in skill_text
    manifest = json.loads((output_dir / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["skills"] == ["shape"]
    assert manifest["emitted_skills"]["shape"]["directory"] == "custom-plan-issue"
    assert verify(output_dir).passed


def test_creator_profile_supports_conditional_overlays(tmp_path: Path) -> None:
    backend_ref = tmp_path / "backend-rules.md"
    backend_ref.write_text("Backend overlay rules.\n", encoding="utf-8")
    profile_file = tmp_path / "conditional.yaml"
    profile_file.write_text(
        """
profile:
  id: conditional
conditional_overlays:
  decision:
    name: Plan Type
    must_record_in_plan: true
    missing_during_execution: stop-for-plan-correction
  routes:
    - id: generic-dev
      description: Generic development work.
      overlays: []
    - id: backend-non-go
      description: Backend work outside the Go stack.
      overlays: [backend]
  overlays:
    backend:
      description: Backend-specific planning and execution rules.
      constraints:
        shape:
          - Confirm backend-visible behavior before proposal-ready.
        pour:
          - Preserve backend runtime compatibility during implementation.
      resources:
        default:
          references:
            - source: backend-rules.md
              dest: backend-rules.md
      validation_commands:
        pour:
          - pytest
""".lstrip(),
        encoding="utf-8",
    )
    output_dir = tmp_path / "conditional-output"

    profile = load_profile(profile_file)
    assert profile.conditional_overlays is not None
    create_suite(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    shape_text = (output_dir / "shape" / "SKILL.md").read_text(encoding="utf-8")
    seal_text = (output_dir / "seal" / "SKILL.md").read_text(encoding="utf-8")
    pour_text = (output_dir / "pour" / "SKILL.md").read_text(encoding="utf-8")
    assert (output_dir / "shape" / "references" / "backend-rules.md").is_file()
    assert "## Conditional References" in shape_text
    assert "Use the recorded `Plan Type`" in shape_text
    assert "If `Plan Type` is `generic-dev`, do not load overlay references." in shape_text
    assert "If `Plan Type` is `backend-non-go`, load:" in shape_text
    assert "references/backend-rules.md" not in shape_text.split(
        "## Conditional References",
        1,
    )[0]
    assert "references/backend-rules.md" in shape_text.split(
        "## Conditional References",
        1,
    )[1]
    assert "Record finalized `Plan Type` in `plan.md`" in seal_text
    assert "stop-for-plan-correction" in pour_text
    assert "pytest" in pour_text

    manifest = json.loads((output_dir / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["conditional_overlays"]["decision"]["name"] == "Plan Type"
    assert manifest["conditional_overlays"]["routes"][1]["overlays"] == ["backend"]
    assert manifest["conditional_overlays"]["routes"][1]["references"]["shape"] == [
        "references/backend-rules.md"
    ]
    assert verify(output_dir).passed


def test_create_cli_requires_target_and_profile(tmp_path: Path) -> None:
    runner = CliRunner()
    missing_profile = runner.invoke(
        main,
        ["create", "--target", "codex", "--output", str(tmp_path / "out")],
    )
    missing_target = runner.invoke(
        main,
        ["create", "--profile", str(SAMPLE_PROFILE), "--output", str(tmp_path / "out")],
    )

    assert missing_profile.exit_code != 0
    assert "Missing option '--profile'" in missing_profile.output
    assert missing_target.exit_code != 0
    assert "Missing option '--target'" in missing_target.output


def test_create_rejects_unknown_target(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsupported target"):
        create_suite(
            profile_file=SAMPLE_PROFILE,
            output_dir=tmp_path / "out",
            target_agent="unknown",
            methodology_dir=METHODOLOGY,
        )


def test_creator_output_is_deterministic_except_manifest_time(tmp_path: Path) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=first,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=second,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert _file_map(first) == _file_map(second)


def test_committed_generated_outputs_match_creator(tmp_path: Path) -> None:
    codex = tmp_path / "sample-backend-go-plan-first-codex"
    claude = tmp_path / "sample-backend-go-plan-first-claude-code"
    create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=codex,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=claude,
        target_agent="claude-code",
        methodology_dir=METHODOLOGY,
    )

    assert _file_map(COMMITTED_CODEX_OUTPUT) == _file_map(codex)
    assert _file_map(COMMITTED_CLAUDE_OUTPUT) == _file_map(claude)


def test_committed_generated_outputs_verify() -> None:
    codex = verify(COMMITTED_CODEX_OUTPUT)
    claude = verify(COMMITTED_CLAUDE_OUTPUT)

    assert codex.passed, codex.format_human()
    assert claude.passed, claude.format_human()


def test_creator_refuses_non_forma_output_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "not-empty"
    output_dir.mkdir()
    (output_dir / "notes.txt").write_text("keep me\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non-Forma files: notes.txt"):
        create_suite(
            profile_file=SAMPLE_PROFILE,
            output_dir=output_dir,
            target_agent="codex",
            methodology_dir=METHODOLOGY,
        )


def test_creator_can_replace_known_generated_paths(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-backend-go-plan-first-codex"
    create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    stale_file = output_dir / SAMPLE_STAGE_DIRS["shape"] / "stale.txt"
    stale_file.write_text("stale\n", encoding="utf-8")

    create_suite(
        profile_file=SAMPLE_PROFILE,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert not stale_file.exists()
    assert verify(output_dir).passed


def _parse_generated_at(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
        tzinfo=timezone.utc
    )


def _file_map(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if path.is_file():
            rel = path.relative_to(root).as_posix()
            text = path.read_text(encoding="utf-8")
            if rel == ".forma-manifest.json":
                manifest = json.loads(text)
                manifest.pop("generated_at", None)
                manifest.pop("methodology_source_revision", None)
                text = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
            result[rel] = text
    return result
