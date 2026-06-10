- [x] [install-surface-routing] Fix direct skill and plugin install destinations
Accept: Task Type=step; Codex direct skill and bundle installs use `.agents/skills` for project scope and `~/.agents/skills` for user scope, Claude Code direct installs remain under `.claude/skills`, Claude Code plugin roots install into the requested Claude skills directory, and Codex plugin artifacts remain non-installable through `forma install`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Depends: none
Constraint: do not add URL install support, `--target opencode`, or Codex plugin installation inside `forma install`

- [x] [plugin-generation-verification] Add target-aware plugin generation and verification
Accept: Task Type=step; developer CLI, bundled creator, verifier, base-origin metadata, drift/adopt/doctor paths, and tests support both `codex-plugin` and `claude-code-plugin` artifact kinds while preserving Codex `forma-*` plugin skill names and stripping exact `<plugin-name>-` prefixes only for Claude Code plugin-local skill names
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_verifier.py tests/test_layer_1_dogfood.py
Validate: uv run --extra dev forma verify source/skill-creator/
Depends: install-surface-routing
Constraint: Layer 2 verifier changes must stay stdlib-only; direct skill bundle names must stay `forma-*`

- [x] [docs-and-agent-help] Update docs, governance text, and CLI agent guidance
Accept: Task Type=step; Markdown docs, root governance files, command help, and `forma explain agent` describe `.agents/skills`, OpenCode compatibility without an OpenCode target, Claude Code plugin generation/direct install, Codex plugin marketplace install, and the corrected Codex versus Claude Code plugin invocation/naming semantics
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_docs_links.py
Depends: plugin-generation-verification
Constraint: do not claim Codex supports `plugin:skill` or `$plugin:skill` colon triggering

- [x] [regenerate-release-surface] Regenerate and verify committed release artifacts
Accept: Task Type=step; committed `dist/` creator skills, direct skill bundles where drift requires updates, `dist/plugins/codex/forma`, and new `dist/plugins/claude-code/forma` are regenerated from source, verified, and reflected in release-surface drift checks
Validate: uv run --extra dev forma drift --release-surface
Validate: uv run --extra dev forma verify dist/plugins/codex/forma
Validate: uv run --extra dev forma verify dist/plugins/claude-code/forma
Depends: docs-and-agent-help
Constraint: do not hand-edit generated release artifacts except as a temporary debugging step that is replaced by generator output before review
