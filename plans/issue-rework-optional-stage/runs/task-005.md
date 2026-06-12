# Task Evidence

- Task: [release-surface-drift-gate] Verify default release surfaces and update only required creator artifacts
- Completed At (UTC): 2026-06-12T09:25:13Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- dist/skills/claude-code/forma-creator/.forma-manifest.json
- dist/skills/claude-code/forma-creator/resources/plan-first/methodology/resources/mend/references/rework-rules.md
- dist/skills/claude-code/forma-creator/resources/plan-first/methodology/stages/mend.md
- dist/skills/claude-code/forma-creator/scripts/forma_verifier/report.py
- dist/skills/claude-code/forma-creator/scripts/forma_verifier/rules.py
- dist/skills/codex/forma-creator/.forma-manifest.json
- dist/skills/codex/forma-creator/resources/plan-first/methodology/resources/mend/references/rework-rules.md
- dist/skills/codex/forma-creator/resources/plan-first/methodology/stages/mend.md
- dist/skills/codex/forma-creator/scripts/forma_verifier/report.py
- dist/skills/codex/forma-creator/scripts/forma_verifier/rules.py
- dist/skills/opencode/forma-creator/.forma-manifest.json
- dist/skills/opencode/forma-creator/resources/plan-first/methodology/resources/mend/references/rework-rules.md
- dist/skills/opencode/forma-creator/resources/plan-first/methodology/stages/mend.md
- dist/skills/opencode/forma-creator/scripts/forma_verifier/report.py
- dist/skills/opencode/forma-creator/scripts/forma_verifier/rules.py

## Validation Results
- PASS [task, final]: uv run --extra dev forma drift --release-surface
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_verifier.py tests/test_cli.py
- PASS [shared-check:source-creator-verify, final]: uv run --extra dev forma verify source/skill-creator/
- PASS [shared-check:diff-check, final]: git diff --check
- PASS [final]: uv run --extra dev python -m pytest -p no:cacheprovider tests/

## Risks / Unresolved Items
- None recorded.
