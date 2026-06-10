# Task Evidence

- Task: [docs-and-agent-help] Update docs, governance text, and CLI agent guidance
- Completed At (UTC): 2026-06-10T16:16:04Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- AGENTS.md
- README.md
- README.zh-CN.md
- STRUCTURE.md
- docs/concepts.md
- docs/concepts.zh-CN.md
- docs/forma-creator.md
- docs/forma-creator.zh-CN.md
- docs/quick-start.md
- docs/quick-start.zh-CN.md
- docs/skill-bundle.md
- docs/skill-bundle.zh-CN.md
- docs/targets.md
- docs/targets.zh-CN.md
- docs/usage.md
- docs/usage.zh-CN.md
- docs/verifier.md
- docs/verifier.zh-CN.md
- plans/issue-agent-skill-target-install-surfaces/implement-notes.md
- src/forma/explain.py
- src/forma/plugins.py
- tests/test_cli.py

## Validation Results
- PASS [task]: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_docs_links.py

## Risks / Unresolved Items
- None recorded.
