# Task Evidence

- Task: [cli-agent-help-surface] Update CLI help and no-argument routing behavior
- Completed At (UTC): 2026-06-09T08:36:24Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- src/forma/cli.py
- tests/test_cli.py

## Validation Results
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
- PASS [task]: uv run --extra dev forma
- PASS [task]: uv run --extra dev forma --help
- PASS [task]: ! uv run --extra dev forma create --help
- PASS [shared-check:creator-template-tests]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_layer_1_dogfood.py tests/test_creator_builder.py

## Risks / Unresolved Items
- None recorded.
