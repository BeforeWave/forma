# Task Evidence

- Task: [docs-and-final-gates] Update docs, command help, and final validation
- Completed At (UTC): 2026-06-13T06:22:58Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- docs/AGENTS.md
- docs/quick-start.md
- docs/quick-start.zh-CN.md
- docs/usage.md
- docs/usage.zh-CN.md
- src/forma/explain.py
- tests/test_cli.py
- tests/test_creator.py
- tests/test_runtime_assets.py

## Validation Results
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
- PASS [shared-check:cli-report-focused]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
- PASS [shared-check:source-creator-verify, final]: uv run --extra dev forma verify source/skill-creator/
- PASS [final]: uv run --extra dev python -m pytest -p no:cacheprovider tests/
- PASS [final]: git diff --check

## Risks / Unresolved Items
- None recorded.
