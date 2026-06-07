# Task Evidence

- Task: [docs-agent-discovery] Update README, docs, AGENTS.md, CLAUDE.md, and discovery copy for the new release surface
- Completed At (UTC): 2026-06-07T13:56:47Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- AGENTS.md
- CLAUDE.md
- README.md
- README.zh-CN.md
- STRUCTURE.md
- dist/skills/claude-code/forma-creator/.forma-manifest.json
- dist/skills/claude-code/forma-creator/SKILL.md
- dist/skills/codex/forma-creator/.forma-manifest.json
- dist/skills/codex/forma-creator/SKILL.md
- dist/skills/codex/forma-creator/agents/openai.yaml
- docs/examples.md
- docs/examples.zh-CN.md
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
- plans/issue-bundle-plugin-install-surface/implement-notes.md
- pyproject.toml
- source/skill-creator/SKILL.md
- source/skill-creator/interfaces/codex/openai.yaml
- tests/test_runtime_assets.py

## Validation Results
- PASS [task]: uv run --extra dev pytest -p no:cacheprovider tests/test_docs_links.py
- PASS [task]: rg -n -e "create-bundle|create-plugin|forma install|forma-plan|forma-showhand|Codex plugin|Claude Code" README.md README.zh-CN.md docs AGENTS.md CLAUDE.md pyproject.toml source/skill-creator/interfaces/codex/openai.yaml
- PASS [final]: uv run --extra dev pytest -p no:cacheprovider tests/
- PASS [final]: uv run --extra dev forma verify source/skill-creator/
- PASS [final]: uv run --extra dev forma verify dist/skills/codex/forma-creator
- PASS [final]: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
- PASS [final]: uv run --extra dev forma verify dist/skill-bundles/codex
- PASS [final]: uv run --extra dev forma verify dist/skill-bundles/claude-code
- PASS [final]: uv run --extra dev forma verify dist/plugins/codex/forma
- PASS [final]: git diff --check

## Risks / Unresolved Items
- None recorded.
