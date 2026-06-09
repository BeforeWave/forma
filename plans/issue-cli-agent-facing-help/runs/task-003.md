# Task Evidence

- Task: [usage-docs-agent-manual] Align the English and Chinese command references with the new help surface
- Completed At (UTC): 2026-06-09T08:42:04Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- docs/usage.md
- docs/usage.zh-CN.md

## Validation Results
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
- PASS [task]: rg -n -e "create-bundle|create-plugin|build-creator|forma install|forma verify|forma explain" docs/usage.md docs/usage.zh-CN.md
- PASS [shared-check:cli-help-tests]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
- PASS [final]: uv run --extra dev python -m pytest -p no:cacheprovider tests/
- PASS [final]: uv run --extra dev forma verify source/skill-creator/
- PASS [final]: uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
- PASS [final]: uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
- PASS [final]: uv run --extra dev forma verify dist/skills/codex/forma-creator
- PASS [final]: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
- PASS [final]: uv run --extra dev forma verify dist/skill-bundles/codex
- PASS [final]: uv run --extra dev forma verify dist/skill-bundles/claude-code
- PASS [final]: uv run --extra dev forma verify dist/plugins/codex/forma
- PASS [final]: git diff --check

## Risks / Unresolved Items
- None recorded.
