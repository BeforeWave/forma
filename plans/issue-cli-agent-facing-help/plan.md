# Issue Plan

## Goal

- Make Forma CLI help clear enough for coding agents to choose the right command path without trial-and-error, including making `forma` with no arguments a successful discovery entrypoint.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- cross-layer

## Scope

- In scope:
  - Add the completed conditional-decision plan-template correction that prevented `showhand` from executing this issue after lock.
  - Update root CLI help and no-argument behavior in `src/forma/cli.py`.
  - Make `forma` with no arguments return exit `0` and print agent-facing routing guidance.
  - Expand help for the full command manual: `build-creator`, `create-bundle`, `create-plugin`, `install`, `verify`, `explain profile`, and `explain temporary-injection`.
  - Add or update `tests/test_cli.py` coverage for the help behavior, no-args exit code, command routing text, and old `forma create` rejection.
  - Update `docs/usage.md` and `docs/usage.zh-CN.md` so the written command reference matches the CLI help surface.
- Out of scope:
  - Changing the runtime behavior of `create-bundle`, `create-plugin`, `install`, `verify`, `build-creator`, or `explain` beyond help/no-args text.
  - Reintroducing `forma create` or adding compatibility aliases for it.
  - Adding URL install support or Codex plugin installation inside `forma install`.
  - Additional methodology, verifier, profile, committed generated baseline, or `dist/` release artifact changes beyond the completed conditional-decision template correction.
  - Rewriting Quick Start docs unless a docs-link or consistency check proves a small pointer is required.

## Approach

- For the completed template correction:
  - Keep the source `plan-template.md` mostly static, but add a conditional-decision placeholder.
  - In both `src/forma/creator/composer.py` and `source/skill-creator/scripts/create.py`, replace the placeholder at generation time.
  - If a profile has `conditional_overlays.decision`, generated `references/plan-template.md` must include a section named for that decision, such as `## Iteration Area`, plus the valid route ids.
  - If a profile has no conditional overlays, generated templates must remove the placeholder entirely.
  - Refresh affected committed generated baselines and `dist/` release artifacts from source.
- Use Click's command/group help machinery in `src/forma/cli.py`; do not add a custom parser or external runtime guidance asset.
- Make the root command invoke without a subcommand and print the same actionable guide that `forma --help` exposes.
- Root help must include these agent paths:
  - build and install `forma-creator` for agent-side workflow customization;
  - create, verify, and install a skill bundle with `create-bundle`;
  - create and verify a Codex plugin with `create-plugin`, while leaving plugin installation to Codex;
  - use `forma explain ...` when an agent needs profile or temporary-injection authoring guidance;
  - use `create-bundle` or `create-plugin`, not the removed `forma create`.
- Command help must make the next action obvious:
  - `build-creator`: generate a target-fixed creator, then verify/install the generated creator path.
  - `create-bundle`: generate a bundle from the default or tracked profile, then `forma verify`, then `forma install`.
  - `create-plugin`: Codex-only local plugin source, then `forma verify`; Codex owns marketplace/plugin install.
  - `install`: verified local skills or skill bundles only, with target/scope/replace boundaries.
  - `verify`: run before install, commit, or share generated outputs.
  - `explain profile` and `explain temporary-injection`: read-only guidance for agents drafting durable profiles or one-off workflow rules.
- Keep tests focused on durable substrings and exit codes rather than full help snapshots.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user request and the confirmed `forma-ground` handoff take precedence over repository examples; repository files provide current implementation facts.
- Committed artifacts: source, test, docs, generated baselines, `dist/` release artifacts, and this issue's plan files may change only for the accepted tasks.
- Generated paths in scope for the completed template correction:
  - `examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/`
  - `examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/`
  - `dist/skills/codex/forma-creator`
  - `dist/skills/claude-code/forma-creator`
  - `dist/skill-bundles/codex`
  - `dist/skill-bundles/claude-code`
  - `dist/plugins/codex/forma`
- Forbidden generated paths after the completed template correction: no additional `dist/`, `examples/generated/`, `source/methodology/`, `source/skill-creator/`, or `profiles/` edits unless a later task is explicitly revised to allow them.
- Evidence paths: execution evidence will be recorded under `plans/issue-cli-agent-facing-help/runs/`.
- State policy: preserve unrelated worktree changes; stop for plan rework if implementation discovers CLI help is embedded in a committed generated or release artifact that must change.

## Constraints

- Keep the change agent-facing and terse; do not turn CLI help into long product documentation.
- Keep pip/pipx installed CLI behavior independent of the source checkout.
- Preserve existing command names, required options, unsupported target behavior, install boundaries, and plugin guidance semantics.
- Keep English and Chinese command references aligned on command meaning and install boundaries.

## Acceptance Criteria

- `forma` exits `0` and prints a root guide that helps an agent choose the correct path.
- `forma --help` prints the same command-routing guidance.
- Top-level command help states the command's intended use and the next command an agent should run.
- `forma create --help` remains unsupported and continues to point agents toward `create-bundle` / `create-plugin`.
- `docs/usage.md` and `docs/usage.zh-CN.md` describe the no-args discovery behavior and full command routing without stale `forma create` assumptions.
- Generated plan templates for profiles with conditional overlays include the exact conditional decision section, and generated templates for profiles without conditional overlays do not leak placeholder text.
- No generated baseline, profile, methodology, verifier, or `dist/` release artifact is changed beyond the completed conditional-decision template correction.

## Validation

Check: creator-template-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_layer_1_dogfood.py tests/test_creator_builder.py
Note: proves conditional decision template generation, standalone creator parity, and generated baseline consistency.

Check: cli-help-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Note: proves no-args behavior, root help routing, command help routing, and old command rejection.

Check: docs-links
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Note: proves command-reference docs still link correctly after wording changes.

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
uv run --extra dev forma verify dist/skills/codex/forma-creator
uv run --extra dev forma verify dist/skills/claude-code/forma-creator
uv run --extra dev forma verify dist/skill-bundles/codex
uv run --extra dev forma verify dist/skill-bundles/claude-code
uv run --extra dev forma verify dist/plugins/codex/forma
git diff --check
```

## Risks / Notes

- Click may wrap help text differently across terminal widths, so tests should assert stable routing phrases rather than complete rendered help snapshots.
