# Task Evidence

- Task: [sample-profile-layout] Align sanitized sample profile layout with active-source/resource boundaries
- Completed At (UTC): 2026-06-13T06:03:26Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- examples/profiles/sample-backend/references/script-resource-adapter.md
- examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml
- examples/profiles/sample-backend/scripts/github_issue_context.py
- tests/test_creator.py

## Validation Results
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_docs_links.py

## Risks / Unresolved Items
- None recorded.
