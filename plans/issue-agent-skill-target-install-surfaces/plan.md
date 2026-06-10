# Issue Plan

## Goal

- Fix Forma's agent skill install and plugin surfaces so project-scoped Codex direct skills install to the current `.agents/skills` location, OpenCode works through that compatible direct-skill surface, and Claude Code plugin artifacts can be generated, verified, documented, and directly installed.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- cross-layer

## Scope

- In scope: developer CLI behavior, bundled `forma-creator` behavior, Layer 2 verifier rules, release drift/adopt/doctor metadata, CLI help and `forma explain agent`, Markdown docs, and committed `dist/` release artifacts affected by install or plugin semantics.
- In scope: Codex direct skill installs use project `.agents/skills/<name>/SKILL.md` and user `~/.agents/skills/<name>/SKILL.md`; Claude Code direct skill installs remain `.claude/skills` and `~/.claude/skills`.
- In scope: OpenCode support is documented and tested as compatibility through `.agents/skills`; Forma does not add `--target opencode` and does not generate OpenCode JS/TS runtime plugins.
- In scope: Claude Code plugin output uses `.claude-plugin/plugin.json`, root `skills/<skill>/SKILL.md`, and direct install into `.claude/skills/<plugin-name>` or `~/.claude/skills/<plugin-name>`.
- Out of scope: URL download installs, Codex plugin installation inside `forma install`, OpenCode plugin runtime hook output, marketplace publishing, and behavior changes to the plan-first methodology stages beyond generated target metadata and docs.

## Approach

- Update install classification and destination logic so Codex direct skill and bundle installs land under `.agents/skills`, Claude direct installs stay under `.claude/skills`, Codex plugin artifacts remain rejected with marketplace guidance, and Claude Code plugin artifacts are copied as whole plugin roots into the requested Claude skills directory with existing `--replace` semantics.
- Refactor plugin generation into target-aware Codex and Claude Code builders. Codex plugin output keeps `.codex-plugin/plugin.json` and existing internal skill names such as `forma-plan` because Codex docs and observed behavior do not establish `plugin:skill` explicit invocation. Claude Code plugin output adds `.claude-plugin/plugin.json` and strips the exact `<plugin-name>-` prefix from plugin-local workflow skill names, so plugin `forma` emits `plan`, `ground`, `lock`, `execute`, and `showhand`.
- Extend Layer 1 creator scripts, Layer 2 verifier rules, base-origin metadata, drift, adopt, doctor, adapters, and tests to understand `claude-code-plugin` while preserving direct bundle names and target-specific metadata rules.
- Update CLI help, `forma explain agent`, root governance docs, Markdown docs, and usage examples to describe `.agents/skills`, OpenCode compatibility without `--target opencode`, Claude Code plugin generation/direct install, and Codex plugin invocation without colon syntax.
- Regenerate and verify committed release artifacts: creator skills, direct skill bundles where drift requires them, existing `dist/plugins/codex/forma`, and new `dist/plugins/claude-code/forma`.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user confirmations take precedence, then official Codex/Claude Code/OpenCode docs grounding already captured in the conversation, then repository grounding facts from `forma-ground`.
- Artifact paths: source changes are committed in `src/forma/`, `source/skill-creator/`, `tests/`, docs, and root governance files as needed. Generated release artifacts under `dist/skills/`, `dist/skill-bundles/`, `dist/plugins/codex/forma`, and `dist/plugins/claude-code/forma` are committed only after regeneration and verification. Temporary generation or comparison output stays under `/tmp` or `$TMPDIR` and is not committed.
- Evidence paths: task proof is recorded under `plans/issue-agent-skill-target-install-surfaces/runs/` by the workflow runner. `plans/issue-agent-skill-target-install-surfaces/implement-notes.md` may be added only for decisions that help review later tasks.
- State policy: preserve unrelated work, do not write local home/workspace paths into tracked files, and do not hand-edit generated release artifacts when a generator should own them.
- Validation gates: task-local tests must cover changed behavior, generated artifacts must pass `forma verify`, and issue closure must pass the full test and release-surface drift gates listed below.
- Metadata/provenance: emitted plugin manifests and Forma manifests must record target/plugin artifact kind consistently, and verifier/adopt/drift code must agree on those artifact kinds.

## Constraints

- Keep direct skill bundle names stable as `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand`.
- Do not strip Codex plugin skill names for this issue; Codex plugin bundled skills keep the existing `forma-*` names unless a later confirmed Codex trigger model requires a different contract.
- Strip only an exact `<plugin-name>-` prefix for Claude Code plugin-local skill names; reject empty, invalid, or duplicate stripped names.
- Keep Layer 2 verifier code stdlib-only and usable from the bundled creator.
- Keep docs and help consistent in English and Chinese where matching files exist.

## Acceptance Criteria

- `forma install --target codex --scope project|user` installs single skills and skill bundles into `.agents/skills` / `~/.agents/skills`, and tests prove `.codex/skills` is no longer the Codex direct-skill destination.
- `forma install --target claude-code` still installs direct skills and bundles into `.claude/skills`, and additionally installs verified Claude Code plugin roots into `.claude/skills/<plugin-name>` or `~/.claude/skills/<plugin-name>`.
- `forma create-plugin --target claude-code` and bundled Claude Code `forma-creator --artifact plugin` emit valid `.claude-plugin` plugin artifacts with prefix-stripped plugin-local workflow skill names.
- `forma create-plugin --target codex` and bundled Codex creator plugin output continue to emit valid `.codex-plugin` artifacts with `forma-*` bundled skill names.
- OpenCode is presented as supported through generated/installed Codex direct skills in `.agents/skills`, not as a new Forma target or runtime plugin format.
- Markdown docs, CLI help, and `forma explain agent` describe the corrected install paths, plugin support matrix, and Codex/Claude invocation semantics without claiming Codex supports colon-triggered plugin skills.
- Committed `dist/` release artifacts match the updated generators and verifier rules, including a new Claude Code plugin release artifact.

## Validation

Check: cli-install-help
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Note: covers install routing, command help, plugin install rejection/support, and agent-facing help expectations.

Check: creator-verifier
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_verifier.py tests/test_layer_1_dogfood.py
Note: covers developer generator, bundled creator, verifier, metadata, and dogfood paths.

Check: docs-links
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Note: covers Markdown link integrity after documentation updates.

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma drift --release-surface
uv run --extra dev forma verify dist/skills/codex/forma-creator
uv run --extra dev forma verify dist/skills/claude-code/forma-creator
uv run --extra dev forma verify dist/skill-bundles/codex
uv run --extra dev forma verify dist/skill-bundles/claude-code
uv run --extra dev forma verify dist/plugins/codex/forma
uv run --extra dev forma verify dist/plugins/claude-code/forma
git diff --check
```

## Risks / Notes

- The existing `plans/issue-bundle-plugin-install-surface/` plan records older `.codex/skills` and Codex-only plugin assumptions; this issue supersedes those install/plugin-surface assumptions without rewriting that historical record.
