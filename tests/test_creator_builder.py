from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from click.testing import CliRunner

from forma.adapters import build_creator
from forma.cli import main
from forma_verifier import verify


ROOT = Path(__file__).resolve().parents[1]
META_SOURCE = ROOT / "source" / "skill-creator"
METHODOLOGY = ROOT / "source" / "methodology"
SKILL_NAME = "forma-creator"


def test_build_creator_emits_codex_target(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"

    output = build_creator(META_SOURCE, output_root, "codex")

    codex = output_root / "codex" / SKILL_NAME
    assert output == codex
    assert (codex / "SKILL.md").is_file()
    assert (codex / "scripts" / "create.py").is_file()
    assert (codex / "agents" / "openai.yaml").is_file()
    assert (codex / "references" / "agent-target.md").is_file()
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
        / "issue-workflow.sh"
    ).is_file()
    assert _is_executable(
        codex
        / "resources"
        / "plan-first"
        / "methodology"
        / "resources"
        / "shared"
        / "scripts"
        / "issue-workflow.sh"
    )
    assert not (codex / "interfaces").exists()
    assert "fixed to `codex`" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "agents/openai.yaml" in (
        codex / "references" / "agent-target.md"
    ).read_text(encoding="utf-8")
    assert "forma-shape/" in (
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
    assert not (output_root / "claude-code").exists()
    assert verify(codex).passed


def test_build_creator_emits_claude_code_target(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"

    output = build_creator(META_SOURCE, output_root, "claude-code")

    claude = output_root / "claude-code" / SKILL_NAME
    assert output == claude
    assert (claude / "SKILL.md").is_file()
    assert (claude / "scripts" / "create.py").is_file()
    assert (claude / "references" / "agent-target.md").is_file()
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
        / "issue-workflow.sh"
    )
    assert not (claude / "agents").exists()
    assert not (claude / "interfaces").exists()
    claude_target = (claude / "references" / "agent-target.md").read_text(
        encoding="utf-8"
    )
    assert "fixed to `claude-code`" in claude_target
    assert "Do not emit Codex `agents/openai.yaml`" in claude_target
    assert "forma-shape/" in claude_target
    assert "rename.stages" in claude_target
    assert "one-off special constraints" in claude_target
    assert verify(claude).passed


def test_installed_creator_script_uses_temporary_injection_json(tmp_path: Path) -> None:
    output_root = tmp_path / "creator-dist"
    creator = build_creator(META_SOURCE, output_root, "codex")
    injection = tmp_path / "injection.json"
    generated = tmp_path / "generated"
    injection.write_text(
        json.dumps(
            {
                "stages": {
                    "shape": {
                        "display_name": "Backend Plan-First Shape",
                        "short_description": "Converge Go backend plans",
                        "default_prompt": "Use $forma-shape for Go backend planning.",
                    },
                    "flow": {
                        "display_name": "Backend Plan-First Flow",
                    },
                },
                "skills": {
                    "shape": {
                        "description": "Clarify Go backend work before plan finalization."
                    },
                    "flow": {
                        "description": "Execute remaining Go backend tasks automatically."
                    },
                },
                "constraints": {
                    "shape": [
                        "If an API or stream contract change is confirmed or suspected, external prerequisite readiness is a mandatory planning gate before `proposal-ready`.",
                    ],
                    "flow": [
                        "Before automated execution, verify the already-finalized plan passed the backend `finalize-plan` external prerequisite gate.",
                    ],
                },
                "validation_commands": {
                    "seal": ["go test ./..."],
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
    assert (generated / "forma-shape" / "SKILL.md").is_file()
    assert (generated / "forma-flow" / "SKILL.md").is_file()
    assert not (generated / "shape").exists()
    assert not (generated / "backend-plan-first-plan-issue").exists()
    assert 'name: "forma-shape"' in (
        generated / "forma-shape" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "external prerequisite readiness" in (
        generated / "forma-shape" / "SKILL.md"
    ).read_text(encoding="utf-8")
    assert "go test ./..." in (generated / "forma-seal" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    assert (generated / "forma-shape" / "agents" / "openai.yaml").is_file()
    assert (generated / ".forma-manifest.json").is_file()
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
    shape_text = (generated / "forma-shape" / "SKILL.md").read_text(encoding="utf-8")
    pour_text = (generated / "forma-pour" / "SKILL.md").read_text(encoding="utf-8")
    assert (generated / "forma-shape" / "references" / "backend-rules.md").is_file()
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
                        "shape": "backend-plan-first-plan-issue",
                        "gauge": "backend-plan-first-ground-plan",
                        "seal": "backend-plan-first-finalize-plan",
                        "pour": "backend-plan-first-implement-feature",
                        "flow": "backend-plan-first-showhand",
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
    assert (generated / "backend-plan-first-plan-issue" / "SKILL.md").is_file()
    assert (generated / "backend-plan-first-showhand" / "SKILL.md").is_file()
    assert not (generated / "forma-shape").exists()
    assert 'name: "backend-plan-first-plan-issue"' in (
        generated / "backend-plan-first-plan-issue" / "SKILL.md"
    ).read_text(encoding="utf-8")
    manifest = json.loads(
        (generated / ".forma-manifest.json").read_text(encoding="utf-8")
    )
    assert manifest["emitted_skills"]["shape"]["name"] == "backend-plan-first-plan-issue"
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
                        "name": "backend-plan-first-plan-issue",
                        "directory": "backend-plan-first-plan-issue",
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
                "profile": "backend-plan-first",
                "includes": ["backend-go"],
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
            "--source",
            str(META_SOURCE),
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
