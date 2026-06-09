# Task Evidence

- Task: [docs-profile-policy] Update public guidance, self-profile policy, and local user-path cleanup
- Completed At (UTC): 2026-06-09T11:57:09Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- docs/targets.md
- docs/targets.zh-CN.md
- docs/usage.md
- docs/usage.zh-CN.md
- docs/verifier.md
- docs/verifier.zh-CN.md
- plans/issue-trust-handoff-diagnostics/implement-notes.md
- profiles/forma-self/base.yaml
- profiles/forma-self/iteration-overlays.yaml

## Validation Results
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py tests/test_creator.py
- PASS [task, shared-check:local-user-path-policy]: ! rg -ni --fixed-strings "$HOME" . --glob '!.git'

## Risks / Unresolved Items
- None recorded.
