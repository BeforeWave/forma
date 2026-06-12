# Issue Plan

## Goal

- Add a Forma self-profile-only rework stage that materializes same-issue corrective feedback into a locked rework contract.
- The internal stage kind is `mend`; the direct skill is `forma-rework`; the Codex plugin-local skill is `rework` with qualified trigger `forma:rework`.
- Preserve default public output. No-profile skill bundles and plugins must remain five-stage and must not expose `forma-rework` or `rework`.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- Iteration Area: cross-layer

## Scope

- In scope: optional `mend` stage model support, rework methodology source, Layer 2 verifier recognition, Layer 3 profile/composer/adapter/manifest support, Forma self-profile enablement, tests, and temporary self-profile generation/verification proof.
- In scope: a rework contract workflow that can consume direct human feedback or `forma-reconcile` output, write `plans/issue-<id>/rework.md`, append flat standard `rework-*` tasks to `tasks.md`, and hand off execution to `forma-execute` or `forma-showhand` after the rework contract is locked.
- In scope: committed release-surface synchronization only when drift checks show default creator artifacts need regeneration; default skill bundles/plugins must stay without rework.
- Out of scope: public README/docs/quick-start promotion of rework, downstream profile examples, changing default no-profile generation to six stages, and teaching `execute` or `showhand` a special rework task syntax.

## Approach

- Follow the optional `hone` precedent: extend known stage kinds with default-disabled `mend`, add stage-local methodology resources, and emit the stage only when a profile explicitly enables it.
- Add `source/methodology/stages/mend.md` and `source/methodology/resources/mend/references/rework-rules.md` as the canonical rework behavior source.
- Define `Rework Intake`: resolve explicit human feedback first, then `forma-reconcile` output when present; classify as `task-rework`, `delivery-revision`, `plan-rework`, `source-rework`, or `blocked`.
- Define `Rework Materialization`: for same-issue implementation correction, write or update `plans/issue-<id>/rework.md`, append flat standard `rework-001-*` task blocks to the end of `tasks.md`, stage only `rework.md` and `tasks.md`, show the diff, and require explicit user approval before committing the rework contract.
- Keep `tasks.md` runner-compatible. Do not add `## Rework Tasks`, `Source:`, `Feedback:`, or other non-task lines to `tasks.md`; put detailed grouping and source provenance in `rework.md`.
- Keep execution unchanged: after the rework contract is committed and `plan.md` / `tasks.md` are clean, `forma-execute` and `forma-showhand` execute the appended standard tasks through `review-ready` / `complete`.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user conversation decisions first, then the `forma:plan` proposal, then the `forma:ground` handoff, then existing optional `hone` plan records.
- Source paths: `source/methodology/`, `source/skill-creator/scripts/forma_verifier/`, `src/forma/creator/`, `src/forma/adapters/`, `profiles/forma-self/`, and focused tests.
- Runtime record path: `plans/issue-<id>/rework.md` is a committed issue-local ledger for rework source, classification, same-issue rationale, user confirmation, and appended task ids.
- Task path: rework execution tasks are appended to the end of `plans/issue-<id>/tasks.md` as ordinary structured task blocks with `rework-*` ids.
- Evidence paths: workflow completion evidence belongs under `plans/issue-rework-optional-stage/runs/`; meaningful execution decisions belong in `plans/issue-rework-optional-stage/implement-notes.md`.
- Transient generated output: self-profile bundle/plugin validation output must go under `/tmp`, `/private/tmp`, or `$TMPDIR` and must not be committed.
- Committed generated output: `dist/skill-bundles/*` and `dist/plugins/*` must remain default five-stage output. `dist/skills/*/forma-creator` may change only if release-surface drift requires syncing packaged optional methodology or verifier assets.
- State policy: do not write non-temporary absolute filesystem paths into tracked files; use relative paths or placeholders except necessary temporary evidence paths.

## Constraints

- Keep `mend` default disabled and profile opt-in.
- Do not expose rework in default no-profile bundle/plugin output.
- Do not add a new task syntax or new `tasks.md` section heading.
- Do not let `rework` implement code changes, complete tasks, or write `runs/` evidence.
- Do not record plan-level feedback as implementation notes; route it back to planning or lock as a plan amendment.

## Acceptance Criteria

- The developer CLI can load profiles that configure optional `mend`, and default profiles still emit only the existing five public stages.
- The self-profile can emit `forma-rework`; a Codex plugin generated from that profile localizes it to `rework` and records `forma:rework` in the manifest.
- `source/methodology/stages/mend.md` and `rework-rules.md` define direct-feedback intake, reconcile-output intake, same-issue classification, rework ledger format, flat task appending, explicit user-confirmed contract locking, and execute/showhand handoff.
- The verifier recognizes valid `mend` artifacts and rejects incomplete rework methodology that omits `rework.md`, flat `tasks.md` append behavior, explicit user confirmation, or execution handoff.
- Default no-profile generated bundle/plugin output does not include `forma-rework` or plugin-local `rework`.
- Temporary self-profile generation and verification prove the opt-in path without committing self-profile output to `dist/`.

## Validation

Check: creator-profile-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py

Check: verifier-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py

Check: source-creator-verify
Command: uv run --extra dev forma verify source/skill-creator/

Check: diff-check
Command: git diff --check

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma drift --release-surface
git diff --check
```

## Risks / Notes

- The highest-risk failure is accidentally adding `mend` to the default enabled stage set or standalone creator default generation. That would make rework public by default and violate the issue boundary.
- The runner currently rejects Markdown headings and prose inside `tasks.md`; rework source and grouping must stay in `rework.md`, with only standard task blocks in `tasks.md`.
- The standalone creator path intentionally remains five-stage for temporary injection defaults; profile-based generation owns optional self-profile capabilities.
