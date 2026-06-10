# Issue Plan

## Goal

- Add a Forma self-iteration reconciliation stage that can evaluate post-delivery or post-feedback alignment against the current workflow stage, stage-local constraints, issue evidence, generated artifacts, and user feedback.
- The public stage key is `reconcile`; the internal stage kind is `hone`; the Forma self-profile skill is `forma-reconcile`.
- Preserve the generic default no-profile workflow output. `hone` must be optional and enabled first only through Forma's self profile.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- Iteration Area: cross-layer

## Scope

- In scope: repository governance guardrails in `AGENTS.md`, optional `hone` methodology stage source, profile schema/compiler support, bundled creator support, verifier recognition, Forma self-profile enablement, tests, and temporary generation/verification proof.
- In scope: `forma-reconcile` rules for target resolution, stage-local constraint evaluation, recent trigger evidence, route classification, and `delivery-revision` handling after all tasks are complete.
- Out of scope: README or docs changes, public default workflow expansion, committed `dist/` regeneration, generic examples, restoring `profile draft`, and making `agents-md generate`.

## Approach

- First record the repository-wide tracked-file path guard in `AGENTS.md` so this issue does not add private absolute paths to tracked files.
- Extend the stage model with optional internal kind `hone`, default disabled, and map Forma's self profile to public skill `forma-reconcile`.
- Add `source/methodology/stages/hone.md` plus a bundled `reconcile-rules.md` reference. The stage must stay read-only: it classifies feedback and produces an actionable next route, but does not implement, complete tasks, or edit plans.
- Define `Reconcile Target Resolution`: use explicit user target first, then recent Forma skill trigger context, then `.forma-workflow` review cache, then `tasks.md`/`runs/task-*.md`/diff evidence. If these conflict or are missing, return blocked rather than guessing.
- Define `Stage Evaluation Frame`: compare the feedback against the current stage's `SKILL.md`, bundled references, profile `default` constraints, profile current-stage constraints, issue plan/tasks/notes/runs, validation evidence, and current diff or commit evidence.
- Add route outcomes for aligned, acceptable deviation, task rework, delivery revision, plan rework, source rework, and blocked. Task implementation rework must update `plans/issue-<id>/implement-notes.md`; plan-level feedback must not be recorded as implementation notes.
- For all-tasks-complete implementation feedback, route to `delivery-revision`, not to `forma-showhand`, because the workflow runner has no unchecked task for `showhand` to process.

## Artifact/Evidence Boundary

- Source-of-truth refs: this issue plan and tasks, current conversation decisions, `AGENTS.md`, `source/methodology/`, `source/skill-creator/`, `src/forma/`, `profiles/forma-self/`, verifier rules, and tests.
- Artifact paths: temporary generated bundles/plugins may be written only under `/tmp`, `/private/tmp`, or `$TMPDIR`; they are validation evidence only and must not be committed.
- Committed artifacts: no committed `dist/` regeneration in this issue unless a later explicit task changes scope. Generic no-profile release output must remain without `forma-reconcile`.
- Evidence paths: workflow run evidence belongs under `plans/issue-hone-reconcile-stage/runs/`; implementation decisions belong in `plans/issue-hone-reconcile-stage/implement-notes.md` when they affect later tasks or review.
- Validation gates: each task must run its focused tests plus `git diff --check`; final validation must run the shared Python tests and `forma verify source/skill-creator/`.
- Path policy: tracked files must not contain non-temporary absolute filesystem paths. Use relative paths or placeholders, except necessary temporary evidence under `/tmp`, `/private/tmp`, or `$TMPDIR`.

## Constraints

- Keep changes minimal and scoped to this issue.
- Do not modify README, README.zh-CN, docs, public examples, or committed `dist/` output.
- Do not enable `hone` in default no-profile generation.
- Do not route all-completed feedback back to `showhand next`.
- Do not treat recent skill trigger context as authoritative when it conflicts with issue evidence.

## Acceptance Criteria

- `forma-reconcile` is generated from Forma's self profile and contains stage-aware reconciliation behavior.
- Default no-profile bundle/plugin output still emits only the existing five public stages.
- Verifier accepts valid optional `hone` artifacts and rejects inconsistent stage/manifest mappings.
- The bundled creator path and developer CLI path both support the optional stage behavior.
- Reconcile rules explicitly use current-stage constraints and recent trigger evidence to classify feedback, including all-completed `delivery-revision`.
- This issue has no README/docs churn and no committed generated release-surface churn.

## Validation

Check: diff-check
Command: git diff --check

Check: creator-profile-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py

Check: verifier-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
git diff --check
```

## Risks / Notes

- The optional stage must be carefully defaulted. Adding `hone` to shared stage constants without disabling it by default would change generic no-profile output and violate the release-surface boundary.
- The standalone bundled creator duplicates stage logic, so source and bundled creator changes must stay in sync.
- Recent skill trigger context is useful only as a target-resolution hint; the route must still be backed by issue artifacts or explicitly marked blocked.
