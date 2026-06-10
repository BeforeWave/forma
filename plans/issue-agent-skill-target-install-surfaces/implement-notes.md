# Implement Notes

## Task 1: install-surface-routing

Outcome:
- Codex direct installs now target `.agents/skills`, and Claude Code plugin roots can be verified and installed into `.claude/skills/<plugin-name>`.

Decision Notes:
- Added minimal `.claude-plugin/plugin.json` verifier coverage in this task instead of bypassing verification during install. Options considered were deferring Claude plugin installation until full plugin generation support, installing without verification, or adding the smallest structure rule now; the selected option keeps `forma install` consistent with its verified-local-artifact contract while leaving full Claude plugin generation and metadata support to the next task.

Plan Gaps Found:
- The first task needed a minimal verifier rule for Claude Code plugin roots even though broader verifier and generation work is assigned to the next task.

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Expand plugin generation, metadata, drift/adopt/doctor coverage, and release artifacts in the planned follow-up tasks.

## Task 2: plugin-generation-verification

Outcome:
- Developer plugin generation, bundled creator plugin generation, verifier rules, base-origin provenance, drift, adopt, and doctor paths now understand `codex-plugin` and `claude-code-plugin`.

Decision Notes:
- Kept `build_codex_plugin` as a compatibility wrapper and added a target-aware `build_plugin` plus `build_claude_code_plugin`. This keeps existing imports stable while letting CLI/adopt/drift call the shared target-aware path.
- Claude Code plugin manifests use the minimal Forma-verified fields `name`, `version`, `description`, `author`, and `skills`; Codex plugin manifests keep the richer Codex `interface` object and `id`.
- Codex plugin skill names are not localized because Codex colon-style plugin skill triggering is not established in the current docs or observed behavior. Claude Code plugin output strips only the exact `<plugin-name>-` prefix from plugin-local skill names.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Documentation and CLI agent guidance still need to be updated in the next task to explain the new support matrix and invocation semantics.

## Task 3: docs-and-agent-help

Outcome:
- CLI agent guidance, command help expectations, root governance docs, and Markdown docs now describe `.agents/skills`, OpenCode compatibility, Claude Code plugin generation/install, and Codex plugin invocation boundaries.

Decision Notes:
- Kept Codex-specific plugin marketplace guidance where it is still the correct install route, but changed general workflow-output wording from "Codex plugin" to "plugin" when both Codex and Claude Code are now supported.
- Documented OpenCode as a compatibility path through Codex direct skills in `.agents/skills`, not as a Forma target.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Regenerate committed release artifacts so `dist/` reflects the updated creator, plugin, verifier, docs, and install semantics.

## Task 4: regenerate-release-surface

Outcome:
- Rebuilt `dist/skills/*`, `dist/skill-bundles/*`, `dist/plugins/codex/forma`, and added `dist/plugins/claude-code/forma`.

Decision Notes:
- Regenerated default no-profile release artifacts through the public CLI commands instead of hand-editing `dist/`. The release-surface drift command reports the default bundles/plugins as `unknown-source` with `base_origin=fresh`, matching the existing no-injection creator-source drift model.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- None

Closed Prior Follow-ups:
- Task 3 follow-up closed by this task: regenerated committed release artifacts so `dist/` reflects the updated creator, plugin, verifier, docs, and install semantics.

## Follow-up: opencode-native-skill-target

Outcome:
- OpenCode is now a native direct-skill generation and install target for skill bundles and `forma-creator`; Forma still does not generate OpenCode JS/TS runtime plugins.
- OpenCode project installs target `.opencode/skills`; OpenCode user installs target `$HOME/.config/opencode/skills`.
- Codex user installs target `$HOME/.codex/skills`; Codex project installs remain `.agents/skills`.
- Added committed OpenCode release artifacts under `dist/skills/opencode/forma-creator` and `dist/skill-bundles/opencode`.

Decision Notes:
- Earlier OpenCode compatibility wording through `.agents/skills` was too weak for Forma's install target. OpenCode can read compatible direct skills from `.agents/skills`, but `forma install --target opencode` should write OpenCode-native roots.
- Kept plugin targets limited to Codex and Claude Code because OpenCode plugins are `.opencode/plugins/*.js|ts` runtime hooks, not the same skill-bundle manifest shape.

Validation:
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py`
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py`
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator_builder.py`
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py`
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_runtime_assets.py`
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py`
- `uv run --extra dev forma drift --release-surface`

Follow-ups:
- None
