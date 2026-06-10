from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from forma import __version__
from forma.adapters import build_creator
from forma.cli import main
from forma.origin import normalized_payload_digest
from forma_verifier import verify


ROOT = Path(__file__).resolve().parents[1]
META_SOURCE = ROOT / "source" / "skill-creator"
METHODOLOGY = ROOT / "source" / "methodology"
SKILL_NAME = "forma-creator"
FORMA_GENERATOR = {
    "name": "forma",
    "version": __version__,
    "repository_url": "https://github.com/BeforeWave/forma",
}


def _assert_base_origin(
    manifest: dict[str, object],
    root: Path,
    target: str,
    artifact_kind: str,
) -> None:
    base_origin = manifest["base_origin"]
    assert isinstance(base_origin, dict)
    assert base_origin["schema"] == "forma.base-origin.v1"
    assert base_origin["target"] == target
    assert base_origin["artifact_kind"] == artifact_kind
    assert base_origin["normalization_id"] == "forma.normalized-output.v1"
    assert base_origin["base_output_digest"] == normalized_payload_digest(root)


def _assert_origin_matches_baseline(
    manifest: dict[str, object],
    baseline_manifest: dict[str, object],
    baseline_root: Path,
    target: str,
    artifact_kind: str,
) -> None:
    _assert_base_origin(baseline_manifest, baseline_root, target, artifact_kind)
    assert manifest["base_origin"] == baseline_manifest["base_origin"]


def test_build_creator_emits_codex_target(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"

    output = build_creator(META_SOURCE, output_root, "codex")

    codex = output_root / "codex" / SKILL_NAME
    assert output == codex
    assert (codex / "SKILL.md").is_file()
    assert (codex / "scripts" / "create.py").is_file()
    assert (codex / "agents" / "openai.yaml").is_file()
    assert (codex / "references" / "agent-target.md").is_file()
    manifest = json.loads(
        (codex / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["format"] == "forma-creator-manifest-v1"
    assert manifest["bundle_kind"] == "creator"
    assert manifest["target"] == "codex"
    assert manifest["generator"] == FORMA_GENERATOR
    assert manifest["generator_version"] == __version__
    assert manifest["creator"]["name"] == SKILL_NAME
    assert manifest["creator"]["directory"] == SKILL_NAME
    assert manifest["methodology_tree_digest"]
    _assert_base_origin(manifest, codex, "codex", "creator")
    assert (codex / "references" / "temporary-injection-generation.md").is_file()
    assert (
        codex / "resources" / "plan-first" / "methodology" / "stages" / "shape.md"
    ).is_file()
    assert _file_map(codex / "resources" / "plan-first" / "methodology") == _file_map(
        METHODOLOGY
    )
    assert (
        codex
        / "resources"
        / "plan-first"
        / "methodology"
        / "resources"
        / "shared"
        / "scripts"
        / "forma-workflow.sh"
    ).is_file()
    assert _is_executable(
        codex
        / "resources"
        / "plan-first"
        / "methodology"
        / "resources"
        / "shared"
        / "scripts"
        / "forma-workflow.sh"
    )
    assert not (codex / "interfaces").exists()
    assert "fixed to `codex`" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "agents/openai.yaml" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "forma-plan/" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "rename.stages" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "one-off special constraints" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "temporary JSON" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "canonical-plan-first.md" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    codex_target = (codex / "references" / "agent-target.md").read_text(
        encoding="utf-8"
    )
    assert "forma-shape/" not in codex_target
    assert "temporary-injection-generation.md" in codex_target
    assert "profile-authoring-principles.md" in codex_target
    assert "classification table" in codex_target
    assert "constraints.default" in codex_target
    assert "routine `pour` / `flow`" in codex_target
    assert "--artifact bundle" in codex_target
    assert "--artifact plugin" in codex_target
    assert ".codex-plugin/plugin.json" in codex_target
    assert "Do not install generated outputs from this creator" in codex_target
    assert (codex / "references" / "profile-authoring-principles.md").is_file()
    temp_standard = (
        codex / "references" / "temporary-injection-generation.md"
    ).read_text(encoding="utf-8")
    profile_principles = (
        codex / "references" / "profile-authoring-principles.md"
    ).read_text(encoding="utf-8")
    assert "Do not copy README, AGENTS" in temp_standard
    assert "constraints.default" in temp_standard
    assert "conditional_overlays" in temp_standard
    assert "classification table" in temp_standard
    assert "source adapter" in temp_standard
    assert "Script Resource Injection Template" in temp_standard
    assert "resources.<stage>.scripts" in temp_standard
    assert "Profile Authoring Principles" in profile_principles
    assert "Keep this minimal" in profile_principles
    assert "Source Context Adapters" in profile_principles
    assert "python3 scripts/adapter_tool.py" in profile_principles
    assert not (output_root / "claude-code").exists()
    assert verify(codex).passed


def test_build_creator_defaults_to_runtime_asset_source(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"

    output = build_creator(None, output_root, "codex")

    codex = output_root / "codex" / SKILL_NAME
    assert output == codex
    assert (codex / "SKILL.md").is_file()
    assert (codex / "references" / "profile-authoring-principles.md").is_file()
    assert (
        codex / "resources" / "plan-first" / "methodology" / "stages" / "shape.md"
    ).is_file()
    assert verify(codex).passed


def test_build_creator_emits_claude_code_target(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"

    output = build_creator(META_SOURCE, output_root, "claude-code")

    claude = output_root / "claude-code" / SKILL_NAME
    assert output == claude
    assert (claude / "SKILL.md").is_file()
    assert (claude / "scripts" / "create.py").is_file()
    assert (claude / "references" / "agent-target.md").is_file()
    assert (claude / "references" / "temporary-injection-generation.md").is_file()
    assert (
        claude / "resources" / "plan-first" / "methodology" / "stages" / "shape.md"
    ).is_file()
    assert _file_map(claude / "resources" / "plan-first" / "methodology") == _file_map(
        METHODOLOGY
    )
    assert _is_executable(
        claude
        / "resources"
        / "plan-first"
        / "methodology"
        / "resources"
        / "shared"
        / "scripts"
        / "forma-workflow.sh"
    )
    assert not (claude / "agents").exists()
    assert not (claude / "interfaces").exists()
    claude_target = (claude / "references" / "agent-target.md").read_text(
        encoding="utf-8"
    )
    assert "fixed to `claude-code`" in claude_target
    assert "Do not emit Codex `agents/openai.yaml`" in claude_target
    assert "forma-plan/" in claude_target
    assert "forma-shape/" not in claude_target
    assert "rename.stages" in claude_target
    assert "one-off special constraints" in claude_target
    assert "temporary-injection-generation.md" in claude_target
    assert "profile-authoring-principles.md" in claude_target
    assert "classification table" in claude_target
    assert "source-context helper scripts" in claude_target
    assert "--artifact bundle" in claude_target
    assert "--artifact plugin" not in claude_target
    assert "Codex plugin output is unsupported" in claude_target
    assert "Do not install generated outputs from this creator" in claude_target
    assert "--artifact plugin" not in (claude / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert (claude / "references" / "profile-authoring-principles.md").is_file()
    manifest = json.loads(
        (claude / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    _assert_base_origin(manifest, claude, "claude-code", "creator")
    assert verify(claude).passed


def test_installed_creator_script_uses_temporary_injection_json(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "injection.json"
    generated = tmp_path / "generated"
    baseline = tmp_path / "baseline"
    injection.write_text(
        json.dumps(
            {
                "stages": {
                    "shape": {
                        "display_name": "Example Shape",
                        "short_description": "Converge plans before materialization",
                        "default_prompt": "Use $forma-plan for plan-first shaping.",
                    },
                    "flow": {
                        "display_name": "Example Flow",
                    },
                },
                "skills": {
                    "shape": {
                        "description": "Clarify work before plan finalization."
                    },
                    "flow": {
                        "description": "Execute remaining planned tasks automatically."
                    },
                },
                "constraints": {
                    "shape": [
                        "If external readiness is required, settle the prerequisite before `proposal-ready`.",
                    ],
                    "flow": [
                        "Before automated execution, verify the already-finalized plan passed its prerequisite gates.",
                    ],
                },
                "validation_commands": {
                    "seal": ["pytest tests/"],
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(generated),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    baseline_result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(baseline),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert baseline_result.returncode == 0, baseline_result.stderr + baseline_result.stdout
    assert (generated / "forma-plan" / "SKILL.md").is_file()
    assert (generated / "forma-showhand" / "SKILL.md").is_file()
    assert not (generated / "shape").exists()
    assert not (generated / "renamed-shape").exists()
    assert not (generated / "forma-shape").exists()
    assert 'name: "forma-plan"' in (
        generated / "forma-plan" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "settle the prerequisite" in (
        generated / "forma-plan" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "pytest tests/" in (generated / "forma-lock" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert not (generated / "forma-plan" / "script" / "github_issue_context.py").exists()
    assert not (generated / "forma-plan" / "scripts" / "github_issue_context.py").exists()
    assert "gh issue view" not in (
        generated / "forma-plan" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert (generated / "forma-plan" / "agents" / "openai.yaml").is_file()
    assert (generated / ".forma-manifest.json").is_file()
    manifest = json.loads(
        (generated / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["format"] == "forma-bundle-manifest-v1"
    assert manifest["bundle_kind"] == "plan-first-workflow"
    assert manifest["generator"] == FORMA_GENERATOR
    assert manifest["generator_version"] == __version__
    assert manifest["creator_bundle"]["format"] == "forma-creator-manifest-v1"
    assert manifest["creator_bundle"]["generator"] == FORMA_GENERATOR
    assert manifest["creator_bundle"]["creator"]["name"] == SKILL_NAME
    baseline_manifest = json.loads(
        (baseline / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    _assert_origin_matches_baseline(
        manifest,
        baseline_manifest,
        baseline,
        "codex",
        "skill-bundle",
    )
    assert manifest["base_origin"]["base_output_digest"] != normalized_payload_digest(
        generated
    )
    assert verify(generated).passed


def test_installed_codex_creator_script_can_emit_plugin_artifact(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "plugin-injection.json"
    generated = tmp_path / "generated-plugin"
    baseline = tmp_path / "baseline-plugin"
    injection.write_text(
        json.dumps(
            {
                "rename": {
                    "stages": {
                        "shape": "forma-plan",
                        "gauge": "forma-ground",
                        "seal": "forma-lock",
                        "pour": "forma-execute",
                        "flow": "forma-showhand",
                    }
                },
                "skills": {
                    "shape": {
                        "description": "Clarify goals, constraints, boundaries, and acceptance criteria."
                    },
                    "gauge": {
                        "description": "Inspect code, docs, issues, and evidence before deciding."
                    },
                    "seal": {
                        "description": "Lock the execution plan and task contract."
                    },
                    "pour": {
                        "description": "Execute one accepted task and leave verifiable evidence."
                    },
                    "flow": {
                        "description": "Continue remaining tasks, but stop when evidence is insufficient."
                    },
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--artifact",
            "plugin",
            "--output",
            str(generated),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    baseline_result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--artifact",
            "plugin",
            "--output",
            str(baseline),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert baseline_result.returncode == 0, baseline_result.stderr + baseline_result.stdout
    assert "forma creator build-plugin" in result.stdout
    assert "install hint:" in result.stdout
    assert "Codex plugin generated, not installed." in result.stdout
    assert "name: forma" in result.stdout
    assert "root:" in result.stdout
    assert "Install with Codex:" in result.stdout
    assert "codex plugin marketplace list" in result.stdout
    assert "developers.openai.com/codex/plugins/build#install-a-local-plugin-manually" in result.stdout
    assert "developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli" in result.stdout
    assert "codex plugin add forma@<marketplace-name>" in result.stdout
    assert "Codex plugin UI" in result.stdout
    assert "Start a new Codex thread" in result.stdout
    assert "Forma does not install Codex plugins" in result.stdout
    assert (generated / ".codex-plugin" / "plugin.json").is_file()
    assert (generated / ".forma-manifest.json").is_file()
    assert (generated / "skills" / "forma-plan" / "SKILL.md").is_file()
    assert (generated / "skills" / "forma-showhand" / "SKILL.md").is_file()
    assert (generated / "skills" / "forma-plan" / "agents" / "openai.yaml").is_file()
    assert not (generated / "skills" / ".forma-manifest.json").exists()
    assert not (generated / "skill-bundles").exists()
    assert not (generated / "forma-plan").exists()
    plugin = json.loads(
        (generated / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert plugin["id"] == "forma"
    assert plugin["name"] == "forma"
    assert plugin["version"] == __version__
    assert plugin["author"]["name"] == "Forma"
    assert plugin["interface"]["displayName"] == "Forma"
    assert plugin["skills"] == "./skills/"
    manifest = json.loads(
        (generated / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["target"] == "codex"
    assert manifest["emitted_skills"]["shape"]["directory"] == "forma-plan"
    baseline_manifest = json.loads(
        (baseline / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    _assert_origin_matches_baseline(
        manifest,
        baseline_manifest,
        baseline,
        "codex",
        "codex-plugin",
    )
    assert manifest["base_origin"]["base_output_digest"] != normalized_payload_digest(
        generated
    )
    assert verify(generated).passed


def test_installed_codex_creator_plugin_prefix_uses_plugin_identity(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "prefix-plugin-injection.json"
    generated = tmp_path / "generated-plugin"
    injection.write_text(
        json.dumps({"rename": {"prefix": "acme-plan-first"}}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--artifact",
            "plugin",
            "--output",
            str(generated),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert (generated / "skills" / "acme-plan-first-plan" / "SKILL.md").is_file()
    assert (generated / "skills" / "acme-plan-first-showhand" / "SKILL.md").is_file()
    plugin = json.loads(
        (generated / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
    )
    assert plugin["id"] == "acme-plan-first"
    assert plugin["name"] == "acme-plan-first"
    assert plugin["interface"]["displayName"] == "Acme Plan First"
    assert plugin["skills"] == "./skills/"
    manifest = json.loads(
        (generated / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["emitted_skills"]["shape"]["name"] == "acme-plan-first-plan"
    assert verify(generated).passed


def test_installed_claude_creator_script_rejects_plugin_artifact(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "claude-code")
    generated = tmp_path / "generated-plugin"

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--artifact",
            "plugin",
            "--output",
            str(generated),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 2
    assert "plugin artifact is only supported for codex-targeted creators" in (
        result.stderr
    )
    assert not generated.exists()


def test_installed_creator_script_supports_explicit_source_adapter_injection(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "source-adapter-injection.json"
    generated = tmp_path / "generated"
    adapter_ref = (
        METHODOLOGY
        / "resources"
        / "shared"
        / "references"
        / "script-resource-adapter.md"
    )
    adapter_script = (
        METHODOLOGY / "resources" / "shared" / "script" / "github_issue_context.py"
    )
    injection.write_text(
        json.dumps(
            {
                "resources": {
                    "shape": {
                        "references": [
                            {
                                "source": str(adapter_ref),
                                "dest": "script-resource-adapter.md",
                            }
                        ],
                        "scripts": [
                            {
                                "source": str(adapter_script),
                                "dest": "github_issue_context.py",
                            }
                        ],
                    },
                    "seal": {
                        "references": [
                            {
                                "source": str(adapter_ref),
                                "dest": "script-resource-adapter.md",
                            }
                        ],
                        "scripts": [
                            {
                                "source": str(adapter_script),
                                "dest": "github_issue_context.py",
                            }
                        ],
                    },
                },
                "constraints": {
                    "shape": [
                        "When GitHub issue URLs are source-of-truth refs, load and follow `references/script-resource-adapter.md` before deciding planning context is incomplete.",
                    ],
                    "seal": [
                        "When the planning handoff depends on GitHub issue refs, load and follow `references/script-resource-adapter.md` before finalization.",
                    ],
                },
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(generated),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    shape_text = (generated / "forma-plan" / "SKILL.md").read_text(encoding="utf-8")
    seal_text = (generated / "forma-lock" / "SKILL.md").read_text(encoding="utf-8")
    assert "references/script-resource-adapter.md" in shape_text
    assert "references/script-resource-adapter.md" in seal_text
    assert (generated / "forma-plan" / "scripts" / "github_issue_context.py").is_file()
    assert (generated / "forma-lock" / "scripts" / "github_issue_context.py").is_file()
    adapter_text = (
        generated / "forma-plan" / "references" / "script-resource-adapter.md"
    ).read_text(encoding="utf-8")
    assert "Script Resource Adapter" in adapter_text
    assert "stage-local helper script" in adapter_text
    assert "gh issue view" not in adapter_text
    assert "GitHub issue URLs are source-of-truth refs" in shape_text
    assert verify(generated).passed


def test_installed_creator_script_supports_conditional_overlays(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    backend_ref = tmp_path / "backend-rules.md"
    backend_ref.write_text("Backend overlay rules.\n", encoding="utf-8")
    injection = tmp_path / "conditional-injection.json"
    generated = tmp_path / "generated"
    injection.write_text(
        json.dumps(
            {
                "conditional_overlays": {
                    "decision": {
                        "name": "Plan Type",
                        "must_record_in_plan": True,
                        "missing_during_execution": "stop-for-plan-correction",
                    },
                    "routes": [
                        {
                            "id": "generic-dev",
                            "description": "Generic development work.",
                            "overlays": [],
                        },
                        {
                            "id": "backend-non-go",
                            "description": "Backend work outside the Go stack.",
                            "overlays": ["backend"],
                        },
                    ],
                    "overlays": {
                        "backend": {
                            "description": "Backend-specific rules.",
                            "constraints": {
                                "shape": [
                                    "Confirm backend-visible behavior before proposal-ready.",
                                ],
                                "pour": [
                                    "Preserve backend runtime compatibility during implementation.",
                                ],
                            },
                            "resources": {
                                "default": {
                                    "references": [
                                        {
                                            "source": str(backend_ref),
                                            "dest": "backend-rules.md",
                                        }
                                    ]
                                }
                            },
                            "validation_commands": {
                                "pour": ["pytest"],
                            },
                        }
                    },
                }
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(generated),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    shape_text = (generated / "forma-plan" / "SKILL.md").read_text(encoding="utf-8")
    pour_text = (generated / "forma-execute" / "SKILL.md").read_text(encoding="utf-8")
    assert (generated / "forma-plan" / "references" / "backend-rules.md").is_file()
    assert "## Conditional References" in shape_text
    assert "references/backend-rules.md" not in shape_text.split(
        "## Conditional References",
        1,
    )[0]
    assert "If `Plan Type` is `backend-non-go`, load:" in shape_text
    assert "Confirm backend-visible behavior" in shape_text
    assert "stop-for-plan-correction" in pour_text
    manifest = json.loads(
        (generated / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["conditional_overlays"]["decision"]["name"] == "Plan Type"
    assert verify(generated).passed


def test_installed_creator_script_supports_confirmed_stage_renames(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "rename-injection.json"
    generated = tmp_path / "generated"
    injection.write_text(
        json.dumps(
            {
                "rename": {
                    "stages": {
                        "shape": "renamed-shape",
                        "gauge": "renamed-gauge",
                        "seal": "renamed-seal",
                        "pour": "renamed-pour",
                        "flow": "renamed-flow",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(generated),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert (generated / "renamed-shape" / "SKILL.md").is_file()
    assert (generated / "renamed-flow" / "SKILL.md").is_file()
    assert not (generated / "forma-plan").exists()
    assert 'name: "renamed-shape"' in (
        generated / "renamed-shape" / "SKILL.md"
    ).read_text(encoding="utf-8")
    manifest = json.loads(
        (generated / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["emitted_skills"]["shape"]["name"] == "renamed-shape"
    assert verify(generated).passed


def test_installed_creator_script_prefix_uses_public_stage_names(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "prefix-injection.json"
    generated = tmp_path / "generated"
    injection.write_text(
        json.dumps({"rename": {"prefix": "acme-plan-first"}}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(generated),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert (generated / "acme-plan-first-plan" / "SKILL.md").is_file()
    assert (generated / "acme-plan-first-ground" / "SKILL.md").is_file()
    assert (generated / "acme-plan-first-lock" / "SKILL.md").is_file()
    assert (generated / "acme-plan-first-execute" / "SKILL.md").is_file()
    assert (generated / "acme-plan-first-showhand" / "SKILL.md").is_file()
    assert not (generated / "acme-plan-first-shape").exists()
    manifest = json.loads(
        (generated / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["emitted_skills"]["shape"]["name"] == "acme-plan-first-plan"
    assert verify(generated).passed


def test_installed_creator_script_rejects_profile_style_stage_renames(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "bad-injection.json"
    injection.write_text(
        json.dumps(
            {
                "stages": {
                    "shape": {
                        "name": "renamed-shape",
                        "directory": "renamed-shape",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(tmp_path / "generated"),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "unsupported creator keys" in result.stderr


def test_installed_creator_script_rejects_bare_stage_rename(
    tmp_path: Path,
) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "bad-bare-rename.json"
    injection.write_text(
        json.dumps(
            {
                "rename": {
                    "stages": {
                        "shape": "shape",
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(tmp_path / "generated"),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "must not use bare stage name" in result.stderr


def test_installed_creator_script_rejects_profile_keys(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "bad-profile-injection.json"
    injection.write_text(
        json.dumps(
            {
                "profile": True,
                "includes": [],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(tmp_path / "generated"),
            "--injection-json",
            str(injection),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0
    assert "unknown top-level keys" in result.stderr


def test_build_creator_cli(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "build-creator",
            "--output",
            str(output_root),
            "--target",
            "codex",
        ],
    )

    assert result.exit_code == 0, result.output
    assert "codex" in result.output
    assert verify(output_root / "codex" / SKILL_NAME).passed
    assert not (output_root / "claude-code").exists()


def test_build_creator_rejects_unknown_target(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"

    try:
        build_creator(META_SOURCE, output_root, "unknown")
    except ValueError as exc:
        assert "unsupported adapter target" in str(exc)
    else:
        raise AssertionError("expected ValueError")


def _file_map(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): path.read_text(encoding="utf-8")
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _is_executable(path: Path) -> bool:
    return bool(path.stat().st_mode & 0o111)
