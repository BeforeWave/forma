from __future__ import annotations

import shutil
import json
from pathlib import Path

import pytest

from forma_verifier import verify


ROOT = Path(__file__).resolve().parents[1]
VALID_BUNDLE = ROOT / "tests" / "fixtures" / "valid-bundle"
INVALID_BUNDLE = ROOT / "tests" / "fixtures" / "invalid-bundle"


def copy_valid_bundle(tmp_path: Path) -> Path:
    dst = tmp_path / "bundle"
    shutil.copytree(VALID_BUNDLE, dst)
    return dst


def overwrite_skill(bundle: Path, kind: str, text: str) -> None:
    (bundle / kind / "SKILL.md").write_text(text.strip() + "\n", encoding="utf-8")


def skill_text(name: str, description: str, body: str) -> str:
    return f"""---
name: {name}
description: {description}
---

# {name.title()}

{body.strip()}
"""


def assert_has_error(report, rule_id: str) -> None:
    assert any(r.rule_id == rule_id for r in report.errors), report.format_human()


def test_valid_fixture_passes() -> None:
    report = verify(VALID_BUNDLE)

    assert report.passed, report.format_human()
    assert report.bundle_kind == "plan-first-bundle"


def test_forma_prefixed_stage_names_pass(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    for kind in ("shape", "gauge", "seal", "pour", "flow"):
        old_dir = bundle / kind
        new_dir = bundle / f"forma-{kind}"
        shutil.move(str(old_dir), str(new_dir))
        skill_md = new_dir / "SKILL.md"
        skill_md.write_text(
            skill_md.read_text(encoding="utf-8").replace(
                f"name: {kind}",
                f"name: forma-{kind}",
                1,
            ),
            encoding="utf-8",
        )

    report = verify(bundle)

    assert report.passed, report.format_human()
    assert report.bundle_kind == "plan-first-bundle"


def test_invalid_fixture_fails() -> None:
    report = verify(INVALID_BUNDLE)

    assert not report.passed
    assert_has_error(report, "R001")
    assert_has_error(report, "R002")
    assert_has_error(report, "R003")
    assert_has_error(report, "R004")
    assert_has_error(report, "R005")


def test_missing_frontmatter_rule(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "shape",
        """
# Shape

## Workflow

No frontmatter.
""",
    )

    assert_has_error(verify(bundle), "R001")


def test_frontmatter_rejects_extra_keys(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "shape",
        """
---
name: shape
description: Extra key.
metadata:
  type: skill
---

# Shape

## Workflow

chat-only Decision Gate Goal Scope Approach Validation Plan Strategy.
""",
    )

    report = verify(bundle)
    assert_has_error(report, "R001")
    assert "unsupported keys" in report.format_human()


def test_name_kebab_case_rule(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "shape",
        skill_text(
            "Bad Shape",
            "Invalid name.",
            """
## Workflow

chat-only Decision Gate Goal Scope Approach Validation Plan Strategy.
""",
        ),
    )

    assert_has_error(verify(bundle), "R002")


def test_plan_first_name_must_match_parent_kind(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "shape",
        skill_text(
            "org-shape",
            "Wrong parent kind.",
            """
## Workflow

chat-only Decision Gate Goal Scope Approach Validation Plan Strategy.
""",
        ),
    )

    assert_has_error(verify(bundle), "R002a")


def test_body_requires_h2_section(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "shape",
        skill_text(
            "shape",
            "No H2.",
            """
This body has no second-level section.
Decision Gate Goal Scope Approach Validation Plan Strategy chat-only.
""",
        ),
    )

    assert_has_error(verify(bundle), "R003")


def test_referenced_files_must_exist(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "shape",
        skill_text(
            "shape",
            "Missing reference.",
            """
## Workflow

chat-only Decision Gate Goal Scope Approach Validation Plan Strategy.
See `references/missing.md`.
""",
        ),
    )

    assert_has_error(verify(bundle), "R004")


def test_cross_skill_borrowing_is_forbidden(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "shape",
        skill_text(
            "shape",
            "Cross borrowing.",
            """
## Workflow

chat-only Decision Gate Goal Scope Approach Validation Plan Strategy.
Do not load `../other-skill/scripts/tool.py`.
""",
        ),
    )

    assert_has_error(verify(bundle), "R005")


def test_bundled_script_references_must_exist(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        "seal",
        skill_text(
            "seal",
            "Missing script.",
            """
## Workflow

Run `scripts/forma-workflow.sh init 1` before writing plan.md and tasks.md.
""",
        ),
    )

    assert_has_error(verify(bundle), "R006")


def test_manifest_emitted_skill_mapping_supports_custom_names(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    skill_dir = bundle / "custom-plan-issue"
    skill_dir.mkdir(parents=True)
    (bundle / ".forma-manifest.json").write_text(
        json.dumps(
            {
                "bundle_kind": "plan-first-workflow",
                "target": "claude-code",
                "emitted_skills": {
                    "shape": {
                        "name": "custom-plan-issue",
                        "directory": "custom-plan-issue",
                    }
                },
            }
        ),
        encoding="utf-8",
    )
    (skill_dir / "SKILL.md").write_text(
        skill_text(
            "custom-plan-issue",
            "Custom stage.",
            """
## Workflow

chat-only Decision Gate Goal Scope Approach Validation Plan Strategy.
""",
        ),
        encoding="utf-8",
    )

    report = verify(bundle)
    assert report.passed, report.format_human()


def test_conditional_manifest_rejects_missing_overlay_route(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    (bundle / ".forma-manifest.json").write_text(
        json.dumps(
            {
                "bundle_kind": "plan-first-workflow",
                "conditional_overlays": {
                    "decision": {
                        "name": "Plan Type",
                        "must_record_in_plan": True,
                        "missing_during_execution": "stop-for-plan-correction",
                    },
                    "routes": [
                        {
                            "id": "backend-non-go",
                            "description": "Backend work outside Go.",
                            "overlays": ["backend"],
                        }
                    ],
                    "overlays": {},
                },
            }
        ),
        encoding="utf-8",
    )

    report = verify(bundle)

    assert_has_error(report, "R301")
    assert "references missing overlay" in report.format_human()


def test_conditional_references_cannot_leak_to_unconditional_sections(
    tmp_path: Path,
) -> None:
    bundle = copy_valid_bundle(tmp_path)
    (bundle / "shape" / "references" / "backend-rules.md").write_text(
        "Backend rules.\n",
        encoding="utf-8",
    )
    (bundle / ".forma-manifest.json").write_text(
        json.dumps(
            {
                "bundle_kind": "plan-first-workflow",
                "conditional_overlays": {
                    "decision": {
                        "name": "Plan Type",
                        "must_record_in_plan": True,
                        "missing_during_execution": "stop-for-plan-correction",
                    },
                    "routes": [
                        {
                            "id": "backend-non-go",
                            "description": "Backend work outside Go.",
                            "overlays": ["backend"],
                            "references": {
                                "shape": ["references/backend-rules.md"],
                            },
                        }
                    ],
                    "overlays": {
                        "backend": {
                            "description": "Backend rules.",
                            "resources": {
                                "shape": ["references/backend-rules.md"],
                            },
                        }
                    },
                },
            }
        ),
        encoding="utf-8",
    )
    overwrite_skill(
        bundle,
        "shape",
        skill_text(
            "shape",
            "Conditional shape.",
            """
## Workflow

`shape` is chat-only. It settles the Decision Gate dimensions before
`proposal-ready`: Goal, Scope, Approach, Validation, Plan Strategy, and Plan Type.

## Always Load

- `references/backend-rules.md`

## Conditional References

Use the recorded `Plan Type` before loading overlay references.

- If `Plan Type` is `backend-non-go`, load:
  - `references/backend-rules.md`
""",
        ),
    )

    report = verify(bundle)

    assert_has_error(report, "R301")
    assert "leaks into an unconditional read section" in report.format_human()


def test_codex_target_requires_openai_metadata(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    (bundle / ".forma-manifest.json").write_text(
        json.dumps({"target": "codex"}),
        encoding="utf-8",
    )

    assert_has_error(verify(bundle), "R201")


def test_claude_code_target_rejects_codex_metadata(tmp_path: Path) -> None:
    bundle = copy_valid_bundle(tmp_path)
    (bundle / ".forma-manifest.json").write_text(
        json.dumps({"target": "claude-code"}),
        encoding="utf-8",
    )
    agents_dir = bundle / "shape" / "agents"
    agents_dir.mkdir()
    (agents_dir / "openai.yaml").write_text(
        """
interface:
  display_name: Shape
  short_description: Shape stage
  default_prompt: Use shape.
policy:
  allow_implicit_invocation: true
""".lstrip(),
        encoding="utf-8",
    )

    assert_has_error(verify(bundle), "R202")


@pytest.mark.parametrize(
    ("kind", "body", "rule_id"),
    [
        (
            "shape",
            """
## Workflow

Goal Scope Approach Validation Plan Strategy, but no required mode marker.
""",
            "R101",
        ),
        (
            "gauge",
            """
## Workflow

Repository inspection produces a handoff for seal.
""",
            "R102",
        ),
        (
            "seal",
            """
## Workflow

Writes planning files after convergence.
""",
            "R103",
        ),
        (
            "pour",
            """
## Workflow

Executes one task with a user review step.
""",
            "R104",
        ),
    ],
)
def test_methodology_marker_rules(tmp_path: Path, kind: str, body: str, rule_id: str) -> None:
    bundle = copy_valid_bundle(tmp_path)
    overwrite_skill(
        bundle,
        kind,
        skill_text(kind, f"Invalid {kind}.", body),
    )

    assert_has_error(verify(bundle), rule_id)
