from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner

from forma.cli import main
from forma.creator import load_profile
from forma.profile_draft import DRAFT_FILE_NAMES, collect_source_files, create_profile_draft


def test_cli_contract_writes_three_file_draft_package(tmp_path: Path) -> None:
    source = tmp_path / "AGENTS.md"
    source.write_text(
        "\n".join(
            [
                "# Agent Rules",
                "- Preserve unrelated user work.",
                "- Before implementation, clarify scope and validation.",
                "- Validate with `python -m pytest tests/`.",
            ]
        ),
        encoding="utf-8",
    )
    output = tmp_path / "draft"
    runner = CliRunner()

    result = runner.invoke(
        main,
        [
            "profile",
            "draft",
            "--profile-id",
            "sample-profile",
            "--source",
            str(source),
            "--output",
            str(output),
        ],
    )

    assert result.exit_code == 0, result.output
    assert {path.name for path in output.iterdir()} == set(DRAFT_FILE_NAMES)
    assert "forma profile draft: wrote draft package:" in result.output
    assert "self-check: passed load_profile()" in result.output
    profile = load_profile(output / "profile.draft.yaml")
    assert profile.profile_id == "sample-profile"
    assert profile.bundle_name == "sample-profile"
    assert "python -m pytest tests/" in profile.validation_commands["pour"]
    review = (output / "agent-review.md").read_text(encoding="utf-8")
    assert "not durable source until it is reviewed" in review


def test_cli_contract_rejects_invalid_ids_and_missing_source(tmp_path: Path) -> None:
    runner = CliRunner()

    invalid_id = runner.invoke(
        main,
        [
            "profile",
            "draft",
            "--profile-id",
            "Bad_Profile",
            "--source",
            str(tmp_path / "missing.md"),
            "--output",
            str(tmp_path / "draft"),
        ],
    )
    assert invalid_id.exit_code != 0
    assert "profile-id must be lower kebab-case" in invalid_id.output

    missing_source = runner.invoke(
        main,
        [
            "profile",
            "draft",
            "--profile-id",
            "sample-profile",
            "--source",
            str(tmp_path / "missing.md"),
            "--output",
            str(tmp_path / "draft"),
        ],
    )
    assert missing_source.exit_code != 0
    assert "missing source:" in missing_source.output


def test_source_boundary_collects_supported_files_and_skips_forbidden_dirs(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    (root / "docs").mkdir(parents=True)
    (root / ".git").mkdir()
    (root / "dist").mkdir()
    (root / "examples" / "generated").mkdir(parents=True)
    (root / "__pycache__").mkdir()
    (root / "docs" / "rules.md").write_text("- Preserve unrelated work.", encoding="utf-8")
    (root / "docs" / "notes.txt").write_text("- Clarify scope.", encoding="utf-8")
    (root / "docs" / "config.yaml").write_text("profile:\n  id: x\n", encoding="utf-8")
    (root / "docs" / "ignored.json").write_text("{}", encoding="utf-8")
    (root / ".git" / "rules.md").write_text("- Hidden.", encoding="utf-8")
    (root / "dist" / "rules.md").write_text("- Generated.", encoding="utf-8")
    (root / "examples" / "generated" / "rules.md").write_text(
        "- Baseline.",
        encoding="utf-8",
    )
    (root / "__pycache__" / "rules.md").write_text("- Cache.", encoding="utf-8")

    collection = collect_source_files([root])

    source_names = {Path(item.display_path).name for item in collection.files}
    assert source_names == {"config.yaml", "notes.txt", "rules.md"}
    skipped = "\n".join(collection.skipped_paths)
    assert "ignored.json" in skipped
    assert ".git/rules.md" in skipped
    assert "dist/rules.md" in skipped
    assert "examples/generated/rules.md" in skipped
    assert "__pycache__/rules.md" in skipped


def test_output_policy_rejects_existing_dir_without_replace_and_cleans_with_replace(
    tmp_path: Path,
) -> None:
    source = tmp_path / "rules.md"
    source.write_text("- Preserve unrelated user work.", encoding="utf-8")
    output = tmp_path / "draft"
    output.mkdir()
    (output / "stale.txt").write_text("stale", encoding="utf-8")
    runner = CliRunner()

    blocked = runner.invoke(
        main,
        [
            "profile",
            "draft",
            "--profile-id",
            "sample-profile",
            "--source",
            str(source),
            "--output",
            str(output),
        ],
    )
    assert blocked.exit_code != 0
    assert "output directory already exists" in blocked.output

    replaced = runner.invoke(
        main,
        [
            "profile",
            "draft",
            "--profile-id",
            "sample-profile",
            "--source",
            str(source),
            "--output",
            str(output),
            "--replace",
        ],
    )
    assert replaced.exit_code == 0, replaced.output
    assert {path.name for path in output.iterdir()} == set(DRAFT_FILE_NAMES)
    assert not (output / "stale.txt").exists()


def test_load_profile_self_check_accepts_generated_draft_yaml(tmp_path: Path) -> None:
    source = tmp_path / "rules.md"
    source.write_text(
        "- Before implementation, clarify scope.\n- Validate with `uv run pytest tests/`.",
        encoding="utf-8",
    )

    result = create_profile_draft(
        profile_id="review-profile",
        bundle_name="review-bundle",
        org_name="Review Team",
        source_paths=[source],
        output_dir=tmp_path / "draft",
    )

    assert result.self_check == "passed load_profile()"
    profile = load_profile(result.profile_file)
    assert profile.profile_id == "review-profile"
    assert profile.bundle_name == "review-bundle"
    assert profile.org_name == "Review Team"


def test_extractor_classification_places_stage_specific_rules_and_commands(
    tmp_path: Path,
) -> None:
    source = tmp_path / "rules.md"
    source.write_text(
        "\n".join(
            [
                "# Planning",
                "- Before implementation, clarify scope and acceptance criteria.",
                "# Evidence",
                "- Inspect code and docs before deciding.",
                "# Execution",
                "- Preserve unrelated user work.",
                "- Record proof under `plans/issue-<id>/runs/`.",
                "- Validate with `python -m pytest tests/`.",
            ]
        ),
        encoding="utf-8",
    )

    result = create_profile_draft(
        profile_id="classified-profile",
        source_paths=[source],
        output_dir=tmp_path / "draft",
    )

    profile = load_profile(result.profile_file)
    assert any("clarify scope" in item for item in profile.constraints["shape"])
    assert any("Inspect code and docs" in item for item in profile.constraints["gauge"])
    assert any("Preserve unrelated user work" in item for item in profile.constraints["default"])
    assert any("Record proof" in item for item in profile.constraints["pour"])
    assert "python -m pytest tests/" in profile.validation_commands["pour"]


def test_missing_decisions_keep_ambiguous_heavy_route_and_adapter_out_of_yaml(
    tmp_path: Path,
) -> None:
    source = tmp_path / "rules.md"
    source.write_text(
        "\n".join(
            [
                "# Read First",
                "- Always read README.md and STRUCTURE.md before every task.",
                "# Generated Baselines",
                "- Always compare generated baselines before implementation.",
                "# Adapter Rules",
                "- Use the source adapter for repository facts.",
                "# Route Rules",
                "- Apply this only for backend Impact Profile work.",
                "# Local Material",
                "- Never copy <user-home>/private/token.txt into generated artifacts.",
                "# Safe Rule",
                "- Preserve unrelated user work.",
            ]
        ),
        encoding="utf-8",
    )

    result = create_profile_draft(
        profile_id="review-profile",
        source_paths=[source],
        output_dir=tmp_path / "draft",
    )

    profile = load_profile(result.profile_file)
    yaml_constraints = "\n".join(
        item
        for values in profile.constraints.values()
        for item in values
    )
    assert "README.md" not in yaml_constraints
    assert "source adapter" not in yaml_constraints
    assert "Impact Profile" not in yaml_constraints
    assert "<user-home>" not in yaml_constraints
    assert profile.constraints["default"] == ["Preserve unrelated user work."]
    missing = (result.missing_decisions_file).read_text(encoding="utf-8")
    assert "[broad-reading]" in missing
    assert "[generated-baseline-or-release]" in missing
    assert "[adapter-like]" in missing
    assert "[route-specific]" in missing
    assert "[private-or-local]" in missing


def test_validation_commands_extracts_supported_commands_without_promoting_paths(
    tmp_path: Path,
) -> None:
    source = tmp_path / "rules.md"
    source.write_text(
        "\n".join(
            [
                "- Record proof under `plans/issue-<id>/runs/`.",
                "- Check with `uv run pytest tests/`.",
                "- Run `forma verify /private/tmp/example` only as a local smoke.",
            ]
        ),
        encoding="utf-8",
    )

    result = create_profile_draft(
        profile_id="command-profile",
        source_paths=[source],
        output_dir=tmp_path / "draft",
    )

    profile = load_profile(result.profile_file)
    assert any("Record proof" in item for item in profile.constraints["pour"])
    assert "uv run pytest tests/" in profile.validation_commands["pour"]
    assert all(
        "forma verify /private/tmp/example" not in command
        for commands in profile.validation_commands.values()
        for command in commands
    )
    missing = (result.missing_decisions_file).read_text(encoding="utf-8")
    assert "forma verify /private/tmp/example" in missing


def test_unsupported_source_rejects_explicit_unsupported_file(tmp_path: Path) -> None:
    source = tmp_path / "rules.json"
    source.write_text("{}", encoding="utf-8")

    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "profile",
            "draft",
            "--profile-id",
            "sample-profile",
            "--source",
            str(source),
            "--output",
            str(tmp_path / "draft"),
        ],
    )

    assert result.exit_code != 0
    assert "unsupported source type:" in result.output
