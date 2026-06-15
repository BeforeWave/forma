from __future__ import annotations

from importlib.metadata import version as package_version
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from click.testing import CliRunner

from forma import DISTRIBUTION_NAME, __version__
from forma.adapters import workflow_adapter
from forma.base_origin import creator_base_origin
from forma.cli import main
from forma.creator import build_bundle, load_profile
from forma.creator.composer import load_stage_sources
from forma.creator.manifest import find_methodology_dir
from forma.plugins import build_claude_code_plugin, build_codex_plugin
from forma_verifier import verify


ROOT = Path(__file__).resolve().parents[1]
METHODOLOGY = ROOT / "source" / "methodology"
SAMPLE_PROFILE = ROOT / "examples" / "profiles" / "sample-backend" / "sample-backend-go-github-issue-tracked.yaml"
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
FORMA_SELF_PROFILE = ROOT / ".forma" / "profile.yaml"
FORMA_GENERATOR = {
    "name": "forma",
    "version": __version__,
    "repository_url": "https://github.com/BeforeWave/forma",
}
KINDS = ("shape", "gauge", "seal", "pour", "flow")
SAMPLE_STAGE_DIRS = {
    "shape": "backend-plan-first-plan",
    "gauge": "backend-plan-first-ground",
    "seal": "backend-plan-first-lock",
    "pour": "backend-plan-first-execute",
    "flow": "backend-plan-first-showhand",
}
SOFTWARE_STAGE_DIRS = {
    "shape": "software-plan-first-plan",
    "gauge": "software-plan-first-ground",
    "seal": "software-plan-first-lock",
    "pour": "software-plan-first-execute",
    "flow": "software-plan-first-showhand",
}
FORMA_SELF_STAGE_DIRS = {
    "shape": "forma-plan",
    "gauge": "forma-ground",
    "seal": "forma-lock",
    "pour": "forma-execute",
    "flow": "forma-showhand",
    "hone": "forma-reconcile",
    "mend": "forma-rework",
}


def _assert_base_origin(
    manifest: dict[str, object],
    target: str,
    artifact_kind: str,
) -> None:
    base_origin = manifest["base_origin"]
    assert isinstance(base_origin, dict)
    assert base_origin["schema"] == "forma.base-origin.v1"
    assert base_origin["target"] == target
    assert base_origin["artifact_kind"] == artifact_kind
    assert base_origin["normalization_id"] == "forma.normalized-output.v1"
    assert base_origin == creator_base_origin(
        target,
        artifact_kind,
        methodology_dir=METHODOLOGY,
    )


def test_forma_version_comes_from_package_metadata() -> None:
    assert __version__ == package_version(DISTRIBUTION_NAME)


def test_load_profile_resolves_sample_backend_go() -> None:
    profile = load_profile(SAMPLE_PROFILE)

    assert profile.profile_id == "sample-backend-go-github-issue-tracked"
    assert profile.bundle_name == "sample-backend-go-github-issue-tracked"
    assert profile.org_name == "Example Team"
    assert profile.resolved_order == (
        "sample-base",
        "sample-dev",
        "sample-backend",
        "sample-go",
        "sample-backend-go-github-issue-tracked",
    )
    assert "repository" in profile.terminology
    assert "go test ./..." in profile.validation_commands["default"]
    assert any("API" in item for item in profile.constraints["shape"])
    assert not any("README.md" in item for item in profile.constraints["default"])
    assert not any(
        "generated baseline" in item.lower()
        for item in profile.constraints["default"]
    )
    assert any(
        "stage-specific constraints or conditional overlays" in item
        for item in profile.constraints["default"]
    )
    assert any(
        "user-provided special constraints" in item
        for item in profile.constraints["pour"]
    )
    assert profile.stages["shape"].name == "backend-plan-first-plan"
    assert profile.stages["flow"].directory == "backend-plan-first-showhand"
    assert {
        resource.dest
        for resource in profile.resources["shape"]
    } == {
        "references/backend-rules.md",
        "references/backend-review-checks.md",
        "references/script-resource-adapter.md",
        "scripts/github_issue_context.py",
    }
    assert {
        resource.dest
        for resource in profile.resources["seal"]
    } >= {
        "references/script-resource-adapter.md",
        "scripts/github_issue_context.py",
    }
    local_home_prefix = "/" + "Users" + "/"
    assert all(local_home_prefix not in item for item in profile.constraints["default"])


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
    assert profile.stages["shape"].name == "software-plan-first-plan"
    assert profile.stages["flow"].directory == "software-plan-first-showhand"
    assert "$software-plan-first-showhand" in profile.stages["flow"].default_prompt
    assert "Impact Profile" in profile.decision_gate_extras
    assert any("frontend, backend, fullstack, or generic" in item for item in profile.constraints["default"])
    assert not any("generated baselines" in item for item in profile.constraints["default"])
    assert any(
        "Classify natural-language constraints" in item
        for item in profile.constraints["shape"]
    )
    assert any(
        "routine task execution" in item
        for item in profile.constraints["pour"]
    )
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
    assert profile.stages["shape"].name == "forma-plan"
    assert profile.stages["flow"].directory == "forma-showhand"
    assert "$forma-showhand" in profile.stages["flow"].default_prompt
    assert profile.stages["hone"].enabled is True
    assert profile.stages["hone"].directory == "forma-reconcile"
    assert "$forma-reconcile" in profile.stages["hone"].default_prompt
    assert profile.stages["mend"].enabled is True
    assert profile.stages["mend"].directory == "forma-rework"
    assert "$forma-rework" in profile.stages["mend"].default_prompt
    assert "Affected surfaces" in profile.decision_gate_extras
    assert not any("README.md" in item for item in profile.constraints["default"])
    assert any("dirty worktree" in item for item in profile.constraints["default"])
    assert any("active issue plan and tasks" in item for item in profile.constraints["default"])
    assert any("structured user-input" in item for item in profile.constraints["default"])
    assert any("README.md" in item for item in profile.constraints["shape"])
    assert any(
        "creator-side temporary injection" in item
        for item in profile.constraints["shape"]
    )
    assert any(".forma" in item for item in profile.constraints["gauge"])
    assert any("asking for another confirmation" in item for item in profile.constraints["seal"])
    assert not any(
        "scripts/forma-workflow.sh next" in item
        for item in profile.constraints.get("pour", ())
    )
    assert not any(
        "scripts/forma-workflow.sh next" in item
        for item in profile.constraints.get("flow", ())
    )
    assert not any(
        "recent Forma skill trigger context" in item
        for item in profile.constraints.get("hone", ())
    )
    assert not any(
        "rework.md" in item for item in profile.constraints.get("mend", ())
    )
    assert not profile.constraints.get("hone")
    assert not profile.workflow_adds.get("hone")
    assert not profile.output_adds.get("hone")
    assert any("report the committed contract path" in item for item in profile.workflow_adds["mend"])
    assert any("commit only the rework contract file(s)" in item for item in profile.workflow_adds["mend"])
    assert any("forked_from_thread_id" in item for item in profile.workflow_adds["mend"])
    assert any("do not list or search recent threads" in item for item in profile.workflow_adds["mend"])
    assert any("blocked-no-parent-thread" in item for item in profile.workflow_adds["mend"])
    assert any("blocked-no-thread-tool" in item for item in profile.workflow_adds["mend"])
    assert any("rework-result report" in item for item in profile.workflow_adds["mend"])
    assert any("originating host" in item for item in profile.workflow_adds["mend"])
    assert any("do not implement the rework" in item for item in profile.workflow_adds["mend"])
    assert not any("bounded host-thread search" in item for item in profile.workflow_adds["mend"])
    assert not any("search-authorized-not-found" in item for item in profile.workflow_adds["mend"])
    assert any("blocked-no-parent-thread" in item for item in profile.output_adds["mend"])
    assert not any("search-authorized-not-found" in item for item in profile.output_adds["mend"])
    assert profile.conditional_overlays is not None
    assert profile.conditional_overlays.decision.name == "Iteration Area"
    assert [route.id for route in profile.conditional_overlays.routes] == [
        "docs-only",
        "governance",
        "methodology-verifier",
        "creator-profile",
        "generated-baseline",
        "cross-surface",
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


def test_profile_rejects_unknown_plugin_keys(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad.yaml"
    profile_file.write_text(
        """
profile:
  id: bad
plugin:
  displayName: Wrong shape
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="plugin has unknown keys: displayName"):
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
        dest: forma-workflow.sh
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
workflow_adds:
  pour:
    - Base workflow gate.
output_adds:
  pour:
    - Base output field.
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
workflow_adds:
  pour:
    - Base workflow gate.
    - Top workflow gate.
output_adds:
  pour:
    - Base output field.
    - Top output field.
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
    assert profile.workflow_adds["pour"] == [
        "Base workflow gate.",
        "Top workflow gate.",
    ]
    assert profile.output_adds["pour"] == [
        "Base output field.",
        "Top output field.",
    ]
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

    local_home_prefix = "/" + "Users" + "/"
    assert local_home_prefix not in profile_text
    assert "--inject" not in profile_text
    assert ".plan-first" not in profile_text


def test_sample_conditional_overlay_profile_emits_valid_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-conditional-overlay-codex"

    build_bundle(
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


def test_sample_software_plan_first_profile_emits_valid_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-software-plan-first-codex"

    manifest_path = build_bundle(
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

    assert 'name: "software-plan-first-plan"' in shape_text
    assert "references/software-impact-profiles.md" in shape_text
    assert "frontend, backend, fullstack, or generic" in shape_text
    assert "review-ready after validation" in pour_text
    assert "showhand skip grounding" in flow_text
    assert "$software-plan-first-showhand" in flow_agent
    assert ".plan-first" not in shape_text
    assert ".plan-first" not in flow_agent

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["profile"]["top_level_id"] == "sample-software-plan-first"
    assert manifest["profile"]["resolved_order"] == [
        "sample-software-base",
        "sample-software",
        "sample-software-plan-first",
    ]
    assert (
        manifest["emitted_skills"]["shape"]["directory"]
        == "software-plan-first-plan"
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


def test_forma_self_iteration_profile_emits_valid_bundles(tmp_path: Path) -> None:
    codex_dir = tmp_path / "forma-iteration-codex"
    claude_dir = tmp_path / "forma-iteration-claude-code"

    codex_manifest_path = build_bundle(
        profile_file=FORMA_SELF_PROFILE,
        output_dir=codex_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    build_bundle(
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
    hone_text = (
        codex_dir / FORMA_SELF_STAGE_DIRS["hone"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    mend_text = (
        codex_dir / FORMA_SELF_STAGE_DIRS["mend"] / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert 'name: "forma-plan"' in shape_text
    assert "references/forma-iteration-boundaries.md" in shape_text
    assert "Settle `Iteration Area`" in shape_text
    assert "If `Iteration Area` is `cross-surface`, apply `generated` overlay constraint" in pour_text
    assert "Use `scripts/forma-workflow.sh next <issue-id>`" in pour_text
    assert "Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, and the active plans/issue-<id>/ files as the project governance surface." not in pour_text
    assert "If `Iteration Area` is `docs-only`, apply `docs` overlay constraint: Read README.md" in pour_text
    assert "If `Iteration Area` is `governance`, apply `governance` overlay constraint: Read README.md" in pour_text
    assert "$forma-showhand" in flow_agent
    assert 'name: "forma-reconcile"' in hone_text
    assert "references/reconcile-rules.md" in hone_text
    assert "stage evaluation frame" in hone_text.lower()
    assert "issue plan/tasks/notes/runs" in hone_text
    assert "both fits the contract and is the best practical outcome" in hone_text
    assert "delivery-revision" in hone_text
    assert 'name: "forma-rework"' in mend_text
    assert "references/rework-rules.md" in mend_text
    assert "plans/issue-<id>/rework.md" in mend_text
    assert "rework-*" in mend_text
    assert "forma-showhand" in mend_text
    assert (
        codex_dir / FORMA_SELF_STAGE_DIRS["mend"] / "scripts" / "forma-workflow.sh"
    ).is_file()

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
        == "forma-plan"
    )
    assert manifest["emitted_skills"]["hone"]["directory"] == "forma-reconcile"
    assert manifest["emitted_skills"]["mend"]["directory"] == "forma-rework"
    assert manifest["conditional_overlays"]["decision"]["name"] == "Iteration Area"
    assert manifest["conditional_overlays"]["routes"][5]["overlays"] == [
        "methodology",
        "verifier",
        "creator",
        "profiles",
        "generated",
        "docs",
    ]
    assert verify(codex_dir).passed
    assert verify(claude_dir).passed


def test_forma_self_workflow_adds_require_contract_check_before_commits(
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "forma-self-contract-check"

    build_bundle(
        profile_file=FORMA_SELF_PROFILE,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    seal_text = (
        output_dir / FORMA_SELF_STAGE_DIRS["seal"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    mend_text = (
        output_dir / FORMA_SELF_STAGE_DIRS["mend"] / "SKILL.md"
    ).read_text(encoding="utf-8")

    assert "`scripts/forma-workflow.sh check <issue-id>`" in seal_text
    assert "before staging or asking for commit permission" in seal_text
    assert "Contract Check:" in seal_text
    assert "`scripts/forma-workflow.sh check <issue-id>`" in mend_text
    assert "before staging or asking for commit permission" in mend_text
    assert "Contract Check:" in mend_text


def test_find_methodology_dir_accepts_explicit_path() -> None:
    assert find_methodology_dir(METHODOLOGY) == METHODOLOGY.resolve()


def test_workflow_build_emits_valid_codex_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-backend-go-github-issue-tracked-plan-first-codex"

    manifest_path = build_bundle(
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
            output_dir / SAMPLE_STAGE_DIRS[kind] / "scripts" / "forma-workflow.sh"
        ).is_file()
    shape_text = (
        output_dir / SAMPLE_STAGE_DIRS["shape"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    gauge_text = (
        output_dir / SAMPLE_STAGE_DIRS["gauge"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    seal_text = (
        output_dir / SAMPLE_STAGE_DIRS["seal"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    pour_text = (
        output_dir / SAMPLE_STAGE_DIRS["pour"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    flow_text = (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "SKILL.md"
    ).read_text(encoding="utf-8")
    automated_execution = (
        output_dir
        / SAMPLE_STAGE_DIRS["flow"]
        / "references"
        / "automated-execution.md"
    ).read_text(encoding="utf-8")
    task_runner = (
        output_dir
        / SAMPLE_STAGE_DIRS["pour"]
        / "references"
        / "task-runner.md"
    ).read_text(encoding="utf-8")
    flow_workflow_script = (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "scripts" / "forma-workflow.sh"
    ).read_text(encoding="utf-8")
    seal_planning_rules = (
        output_dir
        / SAMPLE_STAGE_DIRS["seal"]
        / "references"
        / "planning-rules.md"
    ).read_text(encoding="utf-8")
    seal_plan_template = (
        output_dir
        / SAMPLE_STAGE_DIRS["seal"]
        / "references"
        / "plan-template.md"
    ).read_text(encoding="utf-8")
    decision_gate = (
        output_dir
        / SAMPLE_STAGE_DIRS["shape"]
        / "references"
        / "proposal-decision-gate.md"
    ).read_text(encoding="utf-8")
    assert "## Requirements" in shape_text
    assert "public API behavior" in shape_text
    assert 'name: "backend-plan-first-plan"' in shape_text
    assert "references/backend-rules.md" in shape_text
    assert "references/backend-review-checks.md" in shape_text
    assert "references/script-resource-adapter.md" in shape_text
    assert "scripts/github_issue_context.py" in shape_text
    assert "Load and follow `references/proposal-decision-gate.md`" in shape_text
    assert "Mandatory Decision Gate" not in shape_text
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["shape"] / "script" / "github_issue_context.py"
    ).exists()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["shape"] / "scripts" / "github_issue_context.py"
    ).is_file()
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["seal"] / "script" / "github_issue_context.py"
    ).exists()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["seal"] / "scripts" / "github_issue_context.py"
    ).is_file()
    assert (
        output_dir
        / SAMPLE_STAGE_DIRS["shape"]
        / "references"
        / "script-resource-adapter.md"
    ).is_file()
    assert (
        output_dir
        / SAMPLE_STAGE_DIRS["seal"]
        / "references"
        / "script-resource-adapter.md"
    ).is_file()
    adapter_text = (
        output_dir
        / SAMPLE_STAGE_DIRS["shape"]
        / "references"
        / "script-resource-adapter.md"
    ).read_text(encoding="utf-8")
    assert "Script Resource Adapter" in adapter_text
    assert "stage-local helper script" in adapter_text
    assert "gh issue view" not in adapter_text
    assert "GitHub issue URLs are source-of-truth refs" in shape_text
    assert "Source Material`, `Confirmed Facts`, `Inferences`" in gauge_text
    assert "Every confirmed fact must name the exact source path or ref" in gauge_text
    assert "every inference or recommendation is non-authoritative" in gauge_text
    assert "Recommended Lock Handoff" in gauge_text
    assert "Stage only the finalized `plan.md` and `tasks.md`" in seal_text
    assert "show the staged diff to the user" in seal_text
    assert (
        "After this entry gate passes, `references/planning-rules.md` is the canonical detailed finalization gate"
        in seal_text
    )
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
    implement_notes = (
        output_dir
        / SAMPLE_STAGE_DIRS["pour"]
        / "references"
        / "implement-notes.md"
    ).read_text(encoding="utf-8")
    assert (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "execution-rules.md"
    ).is_file()
    assert (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "implement-notes.md"
    ).is_file()
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "workflow-rules.md"
    ).exists()
    assert "Add or update Go tests" in pour_text
    assert "contract, compatibility, data, or operational risk" in pour_text
    assert "Do not record a process-gate exception as an execution decision" in implement_notes
    assert "command/API shape, CLI compatibility route, output schema" in implement_notes
    assert "install, bootstrap, handoff, or reinstall automation" in implement_notes
    assert "If a reviewer would ask why this shape, boundary, default" in implement_notes
    assert "Before review, decide whether `plans/issue-<id>/implement-notes.md` is required" in pour_text
    assert "Before `review-ready`, decide whether `implement-notes.md` is required" in task_runner
    assert "absence of notes means no such decision occurred" in task_runner
    assert "canonical detailed finalization gate" in seal_planning_rules
    assert "if another lock-stage" in seal_planning_rules
    assert "this reference wins" in seal_planning_rules
    assert "confirmed grounding handoffs or source-adapter outputs" in seal_planning_rules
    assert "show the staged diff to the user before leaving planning" in seal_planning_rules
    assert "Commit only that staged plan/task snapshot" in seal_planning_rules
    assert "Each `## Final Validation` command line must be self-contained" in seal_planning_rules
    assert "standalone variable assignment, `cd`, or `export` lines" in seal_plan_template
    assert "already-locked plan" in flow_text
    assert (
        "Run every `scripts/forma-workflow.sh ...` command from this installed skill package"
        in flow_text
    )
    assert "never relative to the target repository" in flow_text
    assert "Run the bundled `scripts/forma-workflow.sh next <issue-id>`" in flow_text
    assert "Do not run `scripts/forma-workflow.sh init <issue-id>`" in flow_text
    assert "The workflow runner is mandatory for task selection" in flow_text
    assert "do not recover by parsing `tasks.md` manually" in flow_text
    assert "If `next` reports that `plan.md` or `tasks.md` is missing" in flow_text
    assert "references/automated-execution.md" in flow_text
    assert "record the options, selected best choice, and rationale" in flow_text
    assert "Treat `scripts/forma-workflow.sh next <issue-id>` as the only task selector" in automated_execution
    assert "do not require a target-repository `scripts/forma-workflow.sh`" in automated_execution
    assert "Do not compensate for a failed `review-ready` or `complete`" in automated_execution
    assert "Do not run `git add`, `git rm`, or any other index-mutating command" in automated_execution
    assert "include `Recorded Decisions` only when this invocation recorded autonomous execution choices" in automated_execution
    assert "git restore --staged <path>" in flow_workflow_script
    assert "references/showhand-automation.md" not in flow_text
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "plan-template.md"
    ).exists()
    assert not (
        output_dir / SAMPLE_STAGE_DIRS["flow"] / "references" / "tasks-template.md"
    ).exists()
    assert "showhand is execution-only for an already-locked plan" in flow_workflow_script

    report = verify(output_dir)
    assert report.passed, report.format_human()

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["format"] == "forma-bundle-manifest-v1"
    assert manifest["mode"] == "solo"
    assert manifest["bundle_kind"] == "plan-first-workflow"
    assert manifest["target"] == "codex"
    assert manifest["methodology_version"] == "0.1.0"
    assert manifest["generator"] == FORMA_GENERATOR
    assert manifest["generator_version"] == __version__
    assert manifest["methodology_source_revision_type"] == "git-short-sha"
    assert manifest["methodology_source_revision"]
    assert manifest["methodology_tree_digest"]
    _assert_base_origin(manifest, "codex", "skill-bundle")
    generated_at = _parse_generated_at(manifest["generated_at"])
    assert generated_at <= datetime.now(timezone.utc) + timedelta(minutes=1)
    assert manifest["profile"]["top_level_id"] == "sample-backend-go-github-issue-tracked"
    assert manifest["emitted_skills"]["shape"]["name"] == "backend-plan-first-plan"
    assert (
        manifest["emitted_skills"]["flow"]["directory"]
        == "backend-plan-first-showhand"
    )
    assert manifest["profile"]["resolved_order"] == [
        "sample-base",
        "sample-dev",
        "sample-backend",
        "sample-go",
        "sample-backend-go-github-issue-tracked",
    ]
    assert "sample-backend-go-github-issue-tracked.yaml" in manifest["profile"]["file_hashes"]
    assert "backend.yaml" in manifest["profile"]["file_hashes"]
    assert (
        manifest["profile"]["resource_hashes"]["shape:references/backend-rules.md"]
        == manifest["profile"]["resource_hashes"]["seal:references/backend-rules.md"]
    )
    assert manifest["skills"] == list(KINDS)


def test_workflow_build_emits_valid_claude_code_bundle(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-backend-go-github-issue-tracked-plan-first-claude-code"

    build_bundle(
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
    _assert_base_origin(manifest, "claude-code", "skill-bundle")


def test_default_profile_and_codex_plugin_metadata(tmp_path: Path) -> None:
    profile = ROOT / "profiles" / "default" / "forma-plan-first.yaml"
    bundle_dir = tmp_path / "bundle"
    plugin_dir = tmp_path / "plugin"

    build_bundle(
        profile_file=profile,
        output_dir=bundle_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    plugin_json = build_codex_plugin(
        profile_file=profile,
        output_dir=plugin_dir,
        methodology_dir=METHODOLOGY,
    )

    assert (bundle_dir / "forma-plan" / "SKILL.md").is_file()
    assert (bundle_dir / "forma-ground" / "SKILL.md").is_file()
    assert (bundle_dir / "forma-lock" / "SKILL.md").is_file()
    assert (bundle_dir / "forma-execute" / "SKILL.md").is_file()
    assert (bundle_dir / "forma-showhand" / "SKILL.md").is_file()
    assert not (bundle_dir / "forma-reconcile").exists()
    assert not (bundle_dir / "forma-rework").exists()
    default_plan_template = (
        bundle_dir / "forma-lock" / "references" / "plan-template.md"
    ).read_text(encoding="utf-8")
    assert "{{ conditional_decision_section }}" not in default_plan_template
    assert "## Conditional Decision" not in default_plan_template
    assert verify(bundle_dir).passed
    assert verify(plugin_dir).passed
    assert not (plugin_dir / "skills" / "forma-reconcile").exists()
    assert not (plugin_dir / "skills" / "forma-rework").exists()
    assert not (plugin_dir / "skills" / "rework").exists()

    plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
    assert plugin["id"] == "forma"
    assert plugin["name"] == "forma"
    assert plugin["version"] == __version__
    assert plugin["author"]["name"] == "Forma"
    assert plugin["interface"]["displayName"] == "Forma"
    assert "Plan-First" in plugin["description"]
    assert plugin["skills"] == "./skills/"
    bundle_manifest = json.loads(
        (bundle_dir / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    plugin_manifest = json.loads(
        (plugin_dir / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    _assert_base_origin(bundle_manifest, "codex", "skill-bundle")
    _assert_base_origin(plugin_manifest, "codex", "codex-plugin")


def test_forma_self_profile_and_codex_plugin_metadata(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"

    plugin_json = build_codex_plugin(
        profile_file=FORMA_SELF_PROFILE,
        output_dir=plugin_dir,
        methodology_dir=METHODOLOGY,
    )

    assert verify(plugin_dir).passed
    assert (plugin_dir / "skills" / "plan" / "SKILL.md").is_file()
    assert (plugin_dir / "skills" / "showhand" / "SKILL.md").is_file()
    assert (plugin_dir / "skills" / "reconcile" / "SKILL.md").is_file()
    assert (plugin_dir / "skills" / "rework" / "SKILL.md").is_file()
    assert not (plugin_dir / "skills" / "forma-plan").exists()
    plan_template = (
        plugin_dir / "skills" / "lock" / "references" / "plan-template.md"
    ).read_text(encoding="utf-8")
    assert "## Iteration Area" in plan_template
    assert "`creator-profile`: Profile composer, target adapter, profile schema, or profile stack changes." in plan_template
    assert "{{ conditional_decision_section }}" not in plan_template
    plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
    assert plugin["id"] == "forma"
    assert plugin["name"] == "forma"
    assert plugin["interface"]["displayName"] == "Forma"
    assert "scoped planning" in plugin["description"]
    assert plugin["interface"]["defaultPrompt"] == [
        "Draft a scoped plan for this change.",
        "Execute the locked task plan.",
    ]
    assert plugin["skills"] == "./skills/"
    manifest = json.loads(
        (plugin_dir / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["profile"]["bundle_name"] == "forma"
    assert manifest["emitted_skills"]["shape"]["name"] == "plan"
    assert manifest["emitted_skills"]["shape"]["directory"] == "plan"
    assert manifest["emitted_skills"]["shape"]["qualified_name"] == "forma:plan"
    assert manifest["emitted_skills"]["hone"]["name"] == "reconcile"
    assert manifest["emitted_skills"]["hone"]["directory"] == "reconcile"
    assert manifest["emitted_skills"]["hone"]["qualified_name"] == "forma:reconcile"
    assert manifest["emitted_skills"]["mend"]["name"] == "rework"
    assert manifest["emitted_skills"]["mend"]["directory"] == "rework"
    assert manifest["emitted_skills"]["mend"]["qualified_name"] == "forma:rework"
    openai_yaml = (
        plugin_dir / "skills" / "plan" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert "$forma:plan" in openai_yaml
    assert "$forma:forma-plan" not in openai_yaml
    assert "$forma-plan" not in openai_yaml
    _assert_base_origin(manifest, "codex", "codex-plugin")


def test_forma_self_profile_and_claude_code_plugin_localizes_skill_names(
    tmp_path: Path,
) -> None:
    plugin_dir = tmp_path / "plugin"

    plugin_json = build_claude_code_plugin(
        profile_file=FORMA_SELF_PROFILE,
        output_dir=plugin_dir,
        methodology_dir=METHODOLOGY,
    )

    assert verify(plugin_dir).passed
    assert plugin_json == plugin_dir / ".claude-plugin" / "plugin.json"
    assert not (plugin_dir / ".codex-plugin").exists()
    assert (plugin_dir / "skills" / "plan" / "SKILL.md").is_file()
    assert (plugin_dir / "skills" / "showhand" / "SKILL.md").is_file()
    assert (plugin_dir / "skills" / "reconcile" / "SKILL.md").is_file()
    assert (plugin_dir / "skills" / "rework" / "SKILL.md").is_file()
    assert not (plugin_dir / "skills" / "forma-plan").exists()
    assert not (plugin_dir / "skills" / "plan" / "agents" / "openai.yaml").exists()
    plan_text = (plugin_dir / "skills" / "plan" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert "name: plan" in plan_text
    plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
    assert plugin["name"] == "forma"
    assert plugin["skills"] == "./skills/"
    manifest = json.loads(
        (plugin_dir / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["target"] == "claude-code"
    assert manifest["emitted_skills"]["shape"]["name"] == "plan"
    assert manifest["emitted_skills"]["shape"]["directory"] == "plan"
    assert manifest["emitted_skills"]["hone"]["name"] == "reconcile"
    assert manifest["emitted_skills"]["mend"]["name"] == "rework"
    _assert_base_origin(manifest, "claude-code", "claude-code-plugin")


def test_sample_profile_codex_plugin_uses_bundle_name(tmp_path: Path) -> None:
    plugin_dir = tmp_path / "plugin"

    plugin_json = build_codex_plugin(
        profile_file=SAMPLE_PROFILE,
        output_dir=plugin_dir,
        methodology_dir=METHODOLOGY,
    )

    assert verify(plugin_dir).passed
    plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
    assert plugin["id"] == "sample-backend-go-github-issue-tracked"
    assert plugin["name"] == "sample-backend-go-github-issue-tracked"
    assert plugin["interface"]["displayName"] == "Sample Backend Go Github Issue Tracked"
    assert plugin["skills"] == "./skills/"


def test_codex_plugin_profile_can_set_plugin_display_name(tmp_path: Path) -> None:
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
    plugin_dir = tmp_path / "plugin"

    plugin_json = build_codex_plugin(
        profile_file=profile_file,
        output_dir=plugin_dir,
        methodology_dir=METHODOLOGY,
    )

    assert verify(plugin_dir).passed
    plugin = json.loads(plugin_json.read_text(encoding="utf-8"))
    assert plugin["id"] == "api-tools"
    assert plugin["name"] == "api-tools"
    assert plugin["interface"]["displayName"] == "API Tools"
    assert plugin["skills"] == "./skills/"


def test_codex_plugin_rejects_non_kebab_bundle_name(tmp_path: Path) -> None:
    profile_file = tmp_path / "bad-plugin-id.yaml"
    profile_file.write_text(
        """
profile:
  id: bad-plugin-id
bundle:
  name: Bad Plugin
""".lstrip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="bundle.name must be lower kebab-case"):
        build_codex_plugin(
            profile_file=profile_file,
            output_dir=tmp_path / "plugin",
            methodology_dir=METHODOLOGY,
        )


def test_workflow_adapter_rejects_opencode_plugin_target() -> None:
    with pytest.raises(ValueError, match="unsupported plugin target: opencode"):
        workflow_adapter("opencode").assert_plugin_supported()


def test_workflow_build_honors_custom_stage_names_and_enabled_matrix(
    tmp_path: Path,
) -> None:
    profile_file = tmp_path / "custom.yaml"
    profile_file.write_text(
        """
profile:
  id: custom
stages:
  shape:
    name: custom-plan
    directory: custom-plan
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

    build_bundle(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert (output_dir / "custom-plan" / "SKILL.md").is_file()
    assert not (output_dir / "shape").exists()
    skill_text = (output_dir / "custom-plan" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert 'name: "custom-plan"' in skill_text
    manifest = json.loads((output_dir / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["skills"] == ["shape"]
    assert manifest["emitted_skills"]["shape"]["directory"] == "custom-plan"
    assert verify(output_dir).passed


def test_optional_hone_stage_is_known_but_disabled_by_default(tmp_path: Path) -> None:
    profile_file = tmp_path / "optional-hone.yaml"
    profile_file.write_text(
        """
profile:
  id: optional-hone
stages:
  hone:
    name: custom-reconcile
    directory: custom-reconcile
    display_name: Custom Reconcile
constraints:
  hone:
    - Evaluate delivery feedback against the current stage contract.
skills:
  hone:
    description: Reconcile delivery feedback.
""".lstrip(),
        encoding="utf-8",
    )
    output_dir = tmp_path / "optional-hone-output"

    profile = load_profile(profile_file)
    assert profile.stages["hone"].enabled is False
    assert profile.stages["hone"].name == "custom-reconcile"
    assert profile.constraints["hone"] == [
        "Evaluate delivery feedback against the current stage contract."
    ]
    assert profile.skill_descriptions["hone"] == "Reconcile delivery feedback."

    build_bundle(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert not (output_dir / "custom-reconcile").exists()
    manifest = json.loads((output_dir / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["skills"] == list(KINDS)
    assert "hone" not in manifest["emitted_skills"]
    assert verify(output_dir).passed


def test_optional_mend_stage_is_known_but_disabled_by_default(tmp_path: Path) -> None:
    profile_file = tmp_path / "optional-mend.yaml"
    profile_file.write_text(
        """
profile:
  id: optional-mend
stages:
  mend:
    name: custom-rework
    directory: custom-rework
    display_name: Custom Rework
constraints:
  mend:
    - Materialize same-issue corrective feedback into ordinary follow-up tasks.
skills:
  mend:
    description: Record a rework contract without implementing it.
""".lstrip(),
        encoding="utf-8",
    )
    output_dir = tmp_path / "optional-mend-output"

    profile = load_profile(profile_file)
    assert profile.stages["mend"].enabled is False
    assert profile.stages["mend"].name == "custom-rework"
    assert profile.constraints["mend"] == [
        "Materialize same-issue corrective feedback into ordinary follow-up tasks."
    ]
    assert profile.skill_descriptions["mend"] == (
        "Record a rework contract without implementing it."
    )

    build_bundle(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert not (output_dir / "custom-rework").exists()
    manifest = json.loads((output_dir / ".forma-manifest.json").read_text(encoding="utf-8"))
    assert manifest["skills"] == list(KINDS)
    assert "mend" not in manifest["emitted_skills"]
    assert verify(output_dir).passed


def test_profile_workflow_and_output_adds_render_in_stage_sections(
    tmp_path: Path,
) -> None:
    profile_file = tmp_path / "stage-adds.yaml"
    profile_file.write_text(
        """
profile:
  id: stage-adds
stages:
  mend:
    enabled: true
workflow_adds:
  mend:
    - Resolve parent-thread handoff before stopping.
output_adds:
  mend:
    - Include `Execution Handoff:` disposition.
""".lstrip(),
        encoding="utf-8",
    )
    output_dir = tmp_path / "stage-adds-output"

    build_bundle(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    manifest = json.loads((output_dir / ".forma-manifest.json").read_text(encoding="utf-8"))
    skill_dir = manifest["emitted_skills"]["mend"]["directory"]
    text = (output_dir / skill_dir / "SKILL.md").read_text(encoding="utf-8")
    workflow = text.split("## Workflow", 1)[1].split("## Load As Needed", 1)[0]
    requirements = text.split("## Requirements", 1)[1].split("## Output", 1)[0]
    output = text.split("## Output", 1)[1]

    assert "- Resolve parent-thread handoff before stopping." in workflow
    assert "Resolve parent-thread handoff before stopping." not in requirements
    assert "- Include `Execution Handoff:` disposition." in output
    assert "Include `Execution Handoff:` disposition." not in requirements
    assert verify(output_dir).passed


def test_plugin_localization_supports_optional_mend_stage(tmp_path: Path) -> None:
    skills_dir = tmp_path / "skills"
    skill_dir = skills_dir / "forma-rework"
    agents_dir = skill_dir / "agents"
    agents_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        """---
name: forma-rework
description: Record rework contract.
---

# Forma Rework
""",
        encoding="utf-8",
    )
    (agents_dir / "openai.yaml").write_text(
        """interface:
  display_name: "Forma Rework"
  short_description: "Record rework contract."
  default_prompt: "$forma-rework: Record rework."
""",
        encoding="utf-8",
    )
    manifest = {
        "emitted_skills": {
            "mend": {
                "name": "forma-rework",
                "directory": "forma-rework",
                "display_name": "Forma Rework",
            }
        }
    }

    localized = workflow_adapter("codex").localize_plugin_skills(
        manifest=manifest,
        skills_dir=skills_dir,
        plugin_name="forma",
    )

    assert not (skills_dir / "forma-rework").exists()
    assert (skills_dir / "rework" / "SKILL.md").is_file()
    skill_text = (skills_dir / "rework" / "SKILL.md").read_text(encoding="utf-8")
    openai_yaml = (
        skills_dir / "rework" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    assert "name: rework" in skill_text
    assert "$forma:rework" in openai_yaml
    assert localized["emitted_skills"]["mend"]["name"] == "rework"
    assert localized["emitted_skills"]["mend"]["directory"] == "rework"
    assert localized["emitted_skills"]["mend"]["qualified_name"] == "forma:rework"


def test_hone_methodology_defines_stage_aware_reconcile_rules() -> None:
    sources = load_stage_sources(METHODOLOGY, ("hone",))
    hone = sources["hone"]
    rules = (
        METHODOLOGY / "resources" / "hone" / "references" / "reconcile-rules.md"
    ).read_text(encoding="utf-8")

    assert "Reconcile delivered workflow results" in hone.description
    assert any("recent Forma skill trigger context" in line for line in hone.workflow_lines)
    assert any("stage evaluation frame" in line.lower() for line in hone.workflow_lines)
    assert any("delivery-revision" in line for line in hone.workflow_lines)
    assert "## Target Resolution" in rules
    assert "## Stage Evaluation Frame" in rules
    assert "## Quality Gate" in rules
    assert "Passing tests" in rules
    assert "a literal" in rules
    assert "`Accept:` line alone" in rules
    assert "low-standard completion" in rules
    assert "weaker surrogate" in rules
    assert "browser-only evidence where real runtime or" in rules
    assert "wrong source layer" in rules
    assert "Best practical outcome" in rules
    assert "do not return `aligned`" in rules
    assert "`plans/issue-<id>/implement-notes.md`" in rules
    assert "`plans/issue-<id>/runs/task-*.md`" in rules
    assert "`delivery-revision`" in rules
    assert "standard current-task `implement-notes.md` section" in rules
    assert "not a custom top-level section" in rules
    assert "## Delivery Revision" not in rules


def test_mend_methodology_defines_rework_contract_rules() -> None:
    sources = load_stage_sources(METHODOLOGY, ("mend",))
    mend = sources["mend"]
    rules = (
        METHODOLOGY / "resources" / "mend" / "references" / "rework-rules.md"
    ).read_text(encoding="utf-8")

    assert "same-issue corrective feedback" in mend.description
    assert any("explicit human feedback first" in line for line in mend.workflow_lines)
    assert any("plans/issue-<id>/rework.md" in line for line in mend.workflow_lines)
    assert any("rework-*" in line for line in mend.workflow_lines)
    assert any(
        "Run every `scripts/forma-workflow.sh ...` command from this installed skill package"
        in line
        for line in mend.workflow_lines
    )
    assert any(
        "the bundled `scripts/forma-workflow.sh check <issue-id>`" in line
        for line in mend.workflow_lines
    )
    assert any("explicit user confirmation" in line for line in mend.workflow_lines)
    assert any("forma-execute" in line for line in mend.workflow_lines)
    assert any("forma-showhand" in line for line in mend.workflow_lines)
    assert "## Intake Sources" in rules
    assert "`plans/issue-<id>/rework.md`" in rules
    assert "`plans/issue-<id>/tasks.md`" in rules
    assert "do not add a `## Rework Tasks` heading" in rules
    assert "do not require or use a target-repository `scripts/forma-workflow.sh`" in rules
    assert "the bundled `scripts/forma-workflow.sh check <issue-id>`" in rules
    assert "require explicit user confirmation before committing" in rules
    assert "`forma-execute`" in rules
    assert "`forma-showhand`" in rules


def test_workflow_profile_supports_conditional_overlays(tmp_path: Path) -> None:
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
    build_bundle(
        profile_file=profile_file,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    shape_text = (output_dir / "shape" / "SKILL.md").read_text(encoding="utf-8")
    seal_text = (output_dir / "seal" / "SKILL.md").read_text(encoding="utf-8")
    pour_text = (output_dir / "pour" / "SKILL.md").read_text(encoding="utf-8")
    plan_template = (
        output_dir / "seal" / "references" / "plan-template.md"
    ).read_text(encoding="utf-8")
    assert (output_dir / "shape" / "references" / "backend-rules.md").is_file()
    assert "## Conditional References" in shape_text
    assert "Use the recorded `Plan Type`" in shape_text
    assert "## Plan Type" in plan_template
    assert "`backend-non-go`: Backend work outside the Go stack." in plan_template
    assert "{{ conditional_decision_section }}" not in plan_template
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


def test_build_bundle_cli_requires_target_and_removes_old_create_command(
    tmp_path: Path,
) -> None:
    runner = CliRunner()
    default_profile = runner.invoke(
        main,
        [
            "build",
            "bundle",
            "--target",
            "codex",
            "--output",
            str(tmp_path / "out"),
            "--methodology",
            str(METHODOLOGY),
        ],
    )
    missing_target = runner.invoke(
        main,
        ["build",
            "bundle", "--profile", str(SAMPLE_PROFILE), "--output", str(tmp_path / "out")],
    )
    old_create = runner.invoke(main, ["create", "--help"])

    assert default_profile.exit_code == 0, default_profile.output
    assert missing_target.exit_code != 0
    assert "Missing option '--target'" in missing_target.output
    assert old_create.exit_code != 0
    assert "No such command 'create'" in old_create.output


def test_explain_profile_outputs_canonical_guidance() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["explain", "profile", "--format", "agent", "--target", "codex"],
    )

    assert result.exit_code == 0
    assert "ACTIONABLE REPORT" in result.output
    assert "# Forma Profile Guidance" in result.output
    assert "Target: `codex`" in result.output
    assert (
        "source/agent-guide/references/profile-authoring-principles.md"
        in result.output
    )
    assert "source/skill-creator/references/temporary-injection-generation.md" not in (
        result.output
    )
    assert "Candidate Draft From Project Facts" in result.output
    assert "does not inspect the repository" in result.output
    assert "source-backed" in result.output
    assert "candidate profile rules" in result.output
    assert "already owned by base methodology" in result.output
    assert "Stage Key Boundary" in result.output
    assert "`hone` and `mend` are optional stages." in result.output
    assert "Generated output names" in result.output
    assert "`constraints.default`: Keep this minimal." in result.output
    assert "`constraints.hone`: Read-only reconciliation" in result.output
    assert "`conditional_overlays`: Heavy route-specific rules" in result.output
    assert "| Candidate rule | Profile target or omitted route |" in result.output
    assert "does not maintain a second copy of the guidance" in result.output


def test_explain_stage_outputs_methodology_boundary() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["explain", "stage", "hone", "--format", "agent", "--target", "codex"],
    )

    assert result.exit_code == 0, result.output
    assert "ACTIONABLE REPORT" in result.output
    assert "# Forma Stage Guidance" in result.output
    assert "Target: `codex`" in result.output
    assert "Stage: `hone`" in result.output
    assert "source/methodology/stages/hone.md" in result.output
    assert "## Base Stage Contract" in result.output
    assert "## Profile Injection Boundary" in result.output
    assert "Use `constraints.hone` only for durable project rules" in result.output
    assert "Do not inject rules that merely restate the base stage contract" in result.output
    assert "propose a methodology update instead of hiding the fix in a profile" in result.output
    assert "`hone` is an optional stage." in result.output


def test_explain_temporary_injection_json_outputs_sources() -> None:
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "explain",
            "temporary-injection",
            "--format",
            "json",
            "--target",
            "codex",
        ],
    )

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["schema"] == "forma.actionable-report.v1"
    assert payload["command"] == "forma explain temporary-injection"
    assert payload["metadata"]["topic"] == "temporary-injection"
    assert payload["metadata"]["target"] == "codex"
    assert [
        source["path"]
        for source in payload["metadata"]["sources"]
    ] == [
        "source/skill-creator/references/temporary-injection-generation.md",
    ]
    assert (
        "Temporary Injection Generation Standard"
        in payload["metadata"]["sources"][0]["content"]
    )
    assert "Stage Key Boundary" in payload["metadata"]["sources"][0]["content"]
    assert "`hone`, and `mend`" in payload["metadata"]["sources"][0]["content"]
    assert "classification table" in payload["metadata"]["markdown"]
    assert "constraints.default" in payload["metadata"]["markdown"]
    assert "Script Resource Injection Template" in payload["metadata"]["markdown"]
    assert "resources.<stage>.scripts" in payload["metadata"]["markdown"]
    assert "python3 scripts/adapter_tool.py" in payload["metadata"]["markdown"]


def test_create_rejects_unknown_target(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unsupported target"):
        build_bundle(
            profile_file=SAMPLE_PROFILE,
            output_dir=tmp_path / "out",
            target_agent="unknown",
            methodology_dir=METHODOLOGY,
        )


def test_workflow_build_output_is_deterministic_except_manifest_time(
    tmp_path: Path,
) -> None:
    first = tmp_path / "first"
    second = tmp_path / "second"
    build_bundle(
        profile_file=SAMPLE_PROFILE,
        output_dir=first,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    build_bundle(
        profile_file=SAMPLE_PROFILE,
        output_dir=second,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )

    assert _file_map(first) == _file_map(second)


def test_workflow_build_refuses_non_forma_output_files(tmp_path: Path) -> None:
    output_dir = tmp_path / "not-empty"
    output_dir.mkdir()
    (output_dir / "notes.txt").write_text("keep me\n", encoding="utf-8")

    with pytest.raises(ValueError, match="non-Forma files: notes.txt"):
        build_bundle(
            profile_file=SAMPLE_PROFILE,
            output_dir=output_dir,
            target_agent="codex",
            methodology_dir=METHODOLOGY,
        )


def test_workflow_build_can_replace_known_generated_paths(tmp_path: Path) -> None:
    output_dir = tmp_path / "sample-backend-go-github-issue-tracked-plan-first-codex"
    build_bundle(
        profile_file=SAMPLE_PROFILE,
        output_dir=output_dir,
        target_agent="codex",
        methodology_dir=METHODOLOGY,
    )
    stale_file = output_dir / SAMPLE_STAGE_DIRS["shape"] / "stale.txt"
    stale_file.write_text("stale\n", encoding="utf-8")

    build_bundle(
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
