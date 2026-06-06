# Task Evidence

- Task: [profile-execution-classification] Apply the classification contract to profiles and generated bundles
- Completed At (UTC): 2026-06-05T10:00:00Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files

- examples/profiles/sample-backend/base.yaml
- examples/profiles/sample-software/base.yaml
- profiles/forma-self/base.yaml
- profiles/forma-self/iteration-overlays.yaml
- MANIFEST.in
- setup.py
- pyproject.toml
- src/forma/assets/
- src/forma/runtime_assets.py
- src/forma/adapters/skill.py
- src/forma/creator/emitter.py
- src/forma/creator/manifest.py
- src/forma/explain.py
- src/forma/cli.py
- tests/test_creator.py
- tests/test_creator_builder.py
- tests/test_runtime_assets.py
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
- plans/issue-workflow-injection-contracts/

## Validation Results

- PASS [final]: `uv run --extra dev pytest -p no:cacheprovider tests/`
- PASS [final]: `uv run --extra dev pytest -p no:cacheprovider tests/test_runtime_assets.py`
- PASS [final]: `uv run --extra dev forma explain profile --target codex`
- PASS [final]: `uv run --extra dev forma explain temporary-injection --format json --target codex`
- PASS [final]: `uv run --extra dev forma build-creator --output /tmp/forma-creator-dist-default --target codex`
- PASS [final]: `uv run --extra dev forma create --target codex --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml --output /tmp/forma-create-default-methodology-codex`
- PASS [final]: `uv run --extra dev forma verify source/skill-creator/`
- PASS [final]: `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/`
- PASS [final]: `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/`
- PASS [final]: `uv run --extra dev forma verify /tmp/forma-self-iteration-codex/`
- PASS [final]: `uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator/`
- PASS [final]: `uv run --extra dev forma verify /tmp/forma-creator-dist-default/codex/forma-creator/`
- PASS [final]: `uv run --extra dev forma verify /tmp/forma-create-default-methodology-codex/`
- PASS [final]: installed bundle inspection
- PASS [final]: `git diff --check`
- PASS [final]: commit dates explicit, equal per commit, and strictly increasing

## Risks / Unresolved Items

- None recorded.
