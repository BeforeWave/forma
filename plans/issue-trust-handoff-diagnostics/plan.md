# Trust Handoff Diagnostics

## Goal

- Make generated Forma artifacts self-diagnosing for agent handoff: `forma verify --json` exposes machine-readable verification results and semantic failure classes, while `forma doctor` tells a user or agent what the artifact is, whether it can be installed by Forma, and the next correct action.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- Iteration Area: cross-layer

## Scope

- In scope: add JSON output to the shared verifier used by the developer CLI and bundled `forma-creator` verifier; add a CLI-only `forma doctor [--json] <path>` command; classify verifier failures into stable semantic classes; update focused docs and tests; update `profiles/forma-self/` so future Forma feature planning starts in the CLI, syncs creator-visible behavior into `forma-creator`, rejects the current developer home path, and requires plugin regeneration plus Codex installation after self-profile edits.
- In scope: clean current tracked occurrences of the current developer home path from repository files without broadening this issue into unrelated absolute-path cleanup.
- In scope: regenerate committed release artifacts that reflect changed creator/profile behavior: `dist/skills/codex/forma-creator`, `dist/skills/claude-code/forma-creator`, and `dist/plugins/codex/forma`.
- Out of scope: `forma diff`, `forma drift`, full release proof samples, history rewrite, marketplace publishing, URL download support, and Claude Code plugin output.

## Approach

- Extend `source/skill-creator/scripts/forma_verifier/` so `RuleResult` and `Report` carry `failure_class` and can render both existing human output and stable JSON. Keep the verifier package stdlib-only and let `source/skill-creator/scripts/verify.py --json <path>` use the same runner as `forma verify --json <path>`.
- Add `--json` to `forma verify` in `src/forma/cli.py` without changing default human output or exit-code behavior.
- Add `forma doctor [--json] <path>` in the CLI. It should reuse verifier classification and install artifact classification to report artifact kind, target, verification status, Forma installability, the correct install route, blockers, and next steps. Codex plugin artifacts must point to Codex plugin installation, not `forma install`.
- Update docs only where the public command surface changes, primarily verifier/usage/target handoff guidance. Avoid turning this issue into README repositioning.
- Update `profiles/forma-self/` policy and regenerate the affected committed release surfaces from source instead of hand-editing generated output.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user conversation decisions and the confirmed Forma grounding facts take precedence; repository docs and source files provide current implementation truth.
- Committed artifacts: source edits, tests, docs, self-profile files, and regenerated `dist/skills/codex/forma-creator`, `dist/skills/claude-code/forma-creator`, and `dist/plugins/codex/forma`.
- Transient artifacts: smoke-test generated output must use `mktemp -d` or `/tmp` and must not be committed.
- Evidence paths: task execution proof is recorded under `plans/issue-trust-handoff-diagnostics/runs/`; implementation decisions that affect later review should be recorded in `plans/issue-trust-handoff-diagnostics/implement-notes.md`.
- State policy: do not introduce tracked current-developer-home strings. Plugin installation proof may inspect the local Codex plugin registry, but local machine paths must not be written into repo files.
- Validation gates: task-local checks must cover the changed behavior before each task is completed; final validation must run full tests, verifier checks for source and regenerated release artifacts, the local user-path policy grep, Codex plugin presence, and whitespace checks.

## Constraints

- Keep Layer 1, Layer 2, Layer 3, profile, and generated-output responsibilities explicit; do not duplicate methodology source into Layer 1.
- Preserve existing `forma verify <path>` human output and exit status semantics unless `--json` is explicitly requested.
- Keep `forma doctor` CLI-only for this issue; do not add creator-facing doctor commands or generated workflow skills.
- Treat self-profile changes as durable profile source and regenerate plus reinstall the Codex plugin before closure.
- Do not clean unrelated generic placeholders, `/private/tmp`, `/absolute/path/to/...`, or synthetic non-local user examples unless they contain the current developer home path.

## Acceptance Criteria

- `forma verify --json <path>` and bundled `scripts/verify.py --json <path>` emit valid JSON with `schema`, `path`, `bundle_kind`, `passed`, `summary`, and `results`; each result includes `rule_id`, `severity`, `failure_class`, `path`, and `message`.
- Verifier rule ids map to stable semantic failure classes: artifact shape, skill metadata, skill identity, resource link, runtime boundary, methodology gate, target contract, plugin contract, and conditional overlay.
- `forma doctor <path>` explains artifact kind, target, verification status, whether `forma install` can install it, the correct install route, blockers, and next steps; `forma doctor --json <path>` exposes the same decision in JSON.
- Self-profile policy records the CLI-first development rule, creator sync rule for creator-visible behavior, current-developer-home path policy, and plugin regeneration plus Codex installation requirement after self-profile edits.
- Regenerated creator and plugin artifacts verify, and the refreshed Codex plugin is installed and visible as `forma@personal`.

## Validation

Check: verifier-focused
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py
Note: shared by verifier JSON and creator-bundled verifier changes.

Check: cli-focused
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_verifier.py
Note: shared by CLI verify and doctor behavior.

Check: local-user-path-policy
Command: ! rg -ni --fixed-strings "$HOME" . --glob '!.git'
Note: proves the tracked worktree does not contain the true local user path class.

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify dist/skills/codex/forma-creator
uv run --extra dev forma verify dist/skills/claude-code/forma-creator
uv run --extra dev forma verify dist/plugins/codex/forma
uv run --extra dev forma verify --json dist/plugins/codex/forma
uv run --extra dev forma doctor --json dist/plugins/codex/forma
! rg -ni --fixed-strings "$HOME" . --glob '!.git'
codex plugin list | rg 'forma@personal'
git diff --check
```

## Risks / Notes

- History rewrite for older commits containing local user paths is a separate destructive maintenance task and is not part of this issue.
