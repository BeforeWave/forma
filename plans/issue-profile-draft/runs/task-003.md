# Task Evidence

- Task: [profile-draft-docs-smoke] Document the draft workflow and prove the generated draft can build a bundle
- Completed At (UTC): 2026-06-09T10:02:17Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- docs/profile-schema.md
- docs/profile-schema.zh-CN.md
- docs/usage.md
- docs/usage.zh-CN.md
- plans/issue-profile-draft/implement-notes.md

## Validation Results
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_profile_draft.py tests/test_cli.py tests/test_docs_links.py
- PASS [task]: tmp_root=/private/tmp/forma-profile-draft-task-smoke; rm -rf "$tmp_root"; mkdir -p "$tmp_root/source"; printf '%s\n' '# Agent Rules' '- Preserve unrelated user work.' '- Clarify scope before implementation.' '- Validate with `python -m pytest tests/`.' > "$tmp_root/source/AGENTS.md"; uv run --extra dev forma profile draft --profile-id task-smoke-profile --source "$tmp_root/source" --output "$tmp_root/draft"; uv run --extra dev forma create-bundle --target codex --profile "$tmp_root/draft/profile.draft.yaml" --output "$tmp_root/bundle"; uv run --extra dev forma verify "$tmp_root/bundle"
- PASS [shared-check:cli-focused]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
- PASS [shared-check:docs-links]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
- PASS [final]: uv run --extra dev python -m pytest -p no:cacheprovider tests/
- PASS [final]: tmp_root=/private/tmp/forma-profile-draft-smoke
- PASS [final]: rm -rf "$tmp_root"
- PASS [final]: mkdir -p "$tmp_root/source"
- PASS [final]: printf '%s\n' '# Agent Rules' '- Preserve unrelated user work.' '- Before implementation, clarify scope and validation.' '- Validate with `python -m pytest tests/`.' '- Record proof under `plans/issue-<id>/runs/`.' > "$tmp_root/source/AGENTS.md"
- PASS [final]: uv run --extra dev forma profile draft --profile-id smoke-profile --source "$tmp_root/source" --output "$tmp_root/draft"
- PASS [final]: uv run --extra dev forma create-bundle --target codex --profile "$tmp_root/draft/profile.draft.yaml" --output "$tmp_root/bundle"
- PASS [final]: uv run --extra dev forma verify "$tmp_root/bundle"
- PASS [final]: git diff --check

## Risks / Unresolved Items
- None recorded.
