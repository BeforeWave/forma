# Issue Plan

## Goal

- Make Forma CLI help clear enough for coding agents to choose the right command path without trial-and-error, including making `forma` with no arguments a successful discovery entrypoint.

## Plan Strategy

- Plan Strategy: step-execution

## Scope

- In scope:
  - Update root CLI help and no-argument behavior in `src/forma/cli.py`.
  - Make `forma` with no arguments return exit `0` and print agent-facing routing guidance.
  - Expand help for the full command manual: `build-creator`, `create-bundle`, `create-plugin`, `install`, `verify`, `explain profile`, and `explain temporary-injection`.
  - Add or update `tests/test_cli.py` coverage for the help behavior, no-args exit code, command routing text, and old `forma create` rejection.
  - Update `docs/usage.md` and `docs/usage.zh-CN.md` so the written command reference matches the CLI help surface.
- Out of scope:
  - Changing the runtime behavior of `create-bundle`, `create-plugin`, `install`, `verify`, `build-creator`, or `explain` beyond help/no-args text.
  - Reintroducing `forma create` or adding compatibility aliases for it.
  - Adding URL install support or Codex plugin installation inside `forma install`.
  - Changing methodology, verifier rules, profiles, committed generated baselines, or `dist/` release artifacts.
  - Rewriting Quick Start docs unless a docs-link or consistency check proves a small pointer is required.

## Approach

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
- Committed artifacts: only source, test, docs, and this issue's plan files should change.
- Forbidden generated paths for this issue: `dist/`, `examples/generated/`, `source/methodology/`, `source/skill-creator/`, and `profiles/`.
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
- No generated baseline, profile, methodology, verifier, or `dist/` release artifact is changed.

## Validation

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
test -z "$(git diff --name-only -- dist examples/generated source/methodology source/skill-creator profiles)"
git diff --check
```

## Risks / Notes

- Click may wrap help text differently across terminal widths, so tests should assert stable routing phrases rather than complete rendered help snapshots.
