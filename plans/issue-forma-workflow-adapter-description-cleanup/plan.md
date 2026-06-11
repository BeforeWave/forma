# Issue Plan

## Goal

- Make Forma-generated workflow output use Forma's current stage vocabulary, user-confirmed plan locking, and target-specific adapter contracts instead of legacy Engcraft-style internal descriptions.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- cross-layer

## Scope

- In scope:
  - Remove generated/user-visible `finalize-plan`, `plan-issue`, `ground-plan`, and `implement-feature` terminology from canonical methodology, creator references, runner messages, docs, tests, and committed generated release artifacts.
  - Change lock-stage planning policy so `plan.md` and `tasks.md` are shown for user confirmation and committed only after explicit user permission.
  - Add a workflow-output target adapter layer for Codex, Claude Code, and OpenCode bundle/plugin differences, while preserving existing public CLI commands.
  - Improve generated skill descriptions so short trigger/UI copy comes from `stages.<stage>.short_description` when present, while long body copy remains available for skill guidance.
  - Keep `profiles/forma-self` checks transient or local-install only; do not promote self-profile output into `dist/`.
  - Update release-boundary docs so `dist/` is consistently documented as default no-profile release output, including `dist/plugins/{codex,claude-code}/forma`.
  - Prevent `implement-notes.md` from being used to normalize bypassing workflow, runner, approval, validation, safety, plan-lock, or plan-correction gates.
  - Update tests, docs, and committed release artifacts affected by the source changes.
- Out of scope:
  - Renaming internal canonical stage keys `shape`, `gauge`, `seal`, `pour`, `flow`, and `hone`.
  - Adding new profile schema fields beyond using the existing `short_description`, `default_prompt`, `skills.description`, and `bundle` fields correctly.
  - Installing into user scope or mutating the real Codex plugin cache during tests.
  - Reopening whether any committed self-profile release path should exist.
  - Moving `profiles/forma-self` generated output into `dist/` or any other committed generated release path.

## Approach

- Replace legacy stage names with current stage semantics: `plan stage`, `ground stage`, `lock stage`, `execute stage`, and `showhand stage`; rename generated reference filenames such as `plan-issue-rules.md` to stage-neutral names where they are copied into artifacts.
- Update lock-stage methodology, shared planning references, and `forma-workflow.sh` user guidance so the generated workflow writes plan/task files, asks for review, and only commits after explicit user confirmation.
- Introduce a Layer 3 workflow adapter module under `src/forma/adapters/` with target adapters for bundle decoration, Codex `agents/openai.yaml`, OpenCode frontmatter metadata, plugin manifest shape, plugin-local skill localization, target support checks, and unsupported plugin errors.
- Mirror the adapter contract inside `source/skill-creator/scripts/create.py` because installed creator bundles must remain self-contained and cannot import Layer 3 source.
- Make generated `SKILL.md` frontmatter descriptions and Codex `openai.yaml` short descriptions prefer `stages.<stage>.short_description`; keep `skills.<stage>.description` as long-form body guidance when present.
- Harden `implement-notes.md` guidance and runner review checks so process-gate bypass notes fail before task completion.
- Update verifier rules, tests, docs, examples, and release artifacts to match the new stage vocabulary and adapter behavior.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user decisions take precedence; the immediately preceding Forma grounding handoff supplies confirmed repository facts; repository policy docs define `dist/` as default no-profile release output.
- Source edit paths: `source/methodology/`, `source/skill-creator/`, `src/forma/creator/`, `src/forma/adapters/`, `src/forma/plugins.py`, focused tests under `tests/`, `docs/`, `README*`, `STRUCTURE.md`, `AGENTS.md`, and `dist/AGENTS.md` when their release-surface policy overlaps.
- Committed generated artifact paths: default no-profile output only: `dist/skills/{codex,claude-code,opencode}/forma-creator`, `dist/skill-bundles/{codex,claude-code,opencode}`, and `dist/plugins/{codex,claude-code}/forma`.
- Transient artifact paths: all `profiles/forma-self` generation, plugin checks, and local install smokes must use `mktemp -d`, `/tmp`, or `/private/tmp`; they must not write local user-home paths into tracked files or committed `dist/`.
- Evidence paths: execution proof is recorded under `plans/issue-forma-workflow-adapter-description-cleanup/runs/`.
- State policy: preserve existing unrelated dirty worktree changes; stage or commit only in-scope files after user confirmation.
- Validation gates: source changes need focused unit tests; generated release changes need `forma verify` on each changed artifact family; final validation covers full tests, source creator verification, generated release verification, stale vocabulary checks, and whitespace checks.
- Metadata/provenance: regenerated manifests must remain deterministic and reflect the current generator, target, artifact kind, and emitted skill names.

## Constraints

- Keep Layer 1 creator source, Layer 2 verifier, Layer 3 generator/adapters, canonical methodology, profiles, docs, and generated release artifacts separated.
- Keep `source/skill-creator/scripts/forma_verifier/` stdlib-only.
- Do not hand-edit generated release artifacts except as part of a verified regeneration task.
- Do not add URL install support or Codex marketplace mutation to `forma install`.
- Do not make OpenCode plugin output; OpenCode remains bundle-only.

## Acceptance Criteria

- Generated skills, plugin manifests, docs, and tests no longer expose `finalize-plan`, `plan-issue`, `ground-plan`, or `implement-feature` as workflow stage names.
- The lock stage instructs agents to show the plan/task content for user confirmation and commit only when the user explicitly allows it.
- Codex, Claude Code, and OpenCode bundle behavior is implemented through target adapters rather than scattered inline conditionals; Codex and Claude Code plugin behavior uses the same adapter contract where applicable.
- Generated `SKILL.md` trigger descriptions and Codex `openai.yaml` short descriptions use `short_description` as the concise base case, with long-form guidance retained in the body.
- `implement-notes.md` remains a decision journal, not an exception ledger; `review-ready` rejects current-task notes that record bypassing workflow, runner, approval, validation, safety, plan-lock, or plan-correction gates as execution decisions.
- `forma create-bundle` and `forma create-plugin` still emit valid outputs for default profiles, `profiles/forma-self`, and representative renamed sample profiles.
- `dist/` release artifacts are regenerated from default no-profile source only and verified; self-profile plugin behavior is proven only through transient generation/install checks.

## Validation

Check: creator-adapter-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_cli.py tests/test_runtime_assets.py tests/test_verifier.py
Note: covers profile composition, target adapters, plugin generation, runtime assets, and verifier rules.

Check: docs-links
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Note: use after README, STRUCTURE, AGENTS, or docs link changes.

Check: source-creator-verify
Command: uv run --extra dev forma verify source/skill-creator/
Note: required after Layer 1 creator or Layer 2 verifier script changes.

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify dist/skills/codex/forma-creator
uv run --extra dev forma verify dist/skills/claude-code/forma-creator
uv run --extra dev forma verify dist/skills/opencode/forma-creator
uv run --extra dev forma verify dist/skill-bundles/codex
uv run --extra dev forma verify dist/skill-bundles/claude-code
uv run --extra dev forma verify dist/skill-bundles/opencode
uv run --extra dev forma verify dist/plugins/codex/forma
uv run --extra dev forma verify dist/plugins/claude-code/forma
if rg -n "finalize-plan|plan-issue|ground-plan|implement-feature" source/methodology source/skill-creator docs tests dist/skills dist/skill-bundles dist/plugins; then exit 1; fi
git diff --check
```

## Risks / Notes

- Current installed/generated lock resources still contain unconditional commit wording; this issue intentionally fixes that contract before any future lock workflow should enforce commit behavior.
- Existing unrelated dirty worktree files must remain untouched unless they are intentionally brought into this issue by the implementer after review.
