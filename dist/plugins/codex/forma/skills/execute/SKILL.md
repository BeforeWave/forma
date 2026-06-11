---
name: execute
description: "Execute one Forma self-iteration task through focused validation and review."
---

# Forma Execute

Execute one Forma self-iteration task through focused validation and review.

## Interaction Semantics

- Use this skill as a review-gated task executor for one accepted task contract.
- For each task, implement only the current task's accepted files/surfaces, run its validation gates through review-ready, and wait for explicit user approval before completion.
- After an approved task is completed successfully, check for the next task immediately and continue if one remains.
- Stop only when review is needed, no unchecked task remains, validation fails, workflow fails, escalation is needed, or the user interrupts.

## Workflow

- Read `./plans/issue-<id>/plan.md`.
- Use `scripts/forma-workflow.sh next <issue-id>` from this installed skill package to get the current task.
- Resolve `scripts/forma-workflow.sh` relative to the current triggered skill package only; never switch to a same-named script in a sibling skill directory, even if the contents match.
- Implement only the current task by treating `Accept:` as the delivery target and `Validate:` / `Use-Check:` as validation gates and proof obligations; if it is the last remaining task, `review-ready` will also run `## Final Validation`.
- For `loop-batch`, report metric/artifact movement before validation; for `gate`, name the protected decision boundary; for `promote`, write only the surfaces explicitly allowed by the current task.
- Record meaningful execution decisions, plan gaps, classifications, deviations, and follow-ups in `plans/issue-<id>/implement-notes.md` using the bundled notes reference.
- Run `scripts/forma-workflow.sh review-ready <issue-id>` before presenting the current task result for user review.
- `scripts/forma-workflow.sh review-ready <issue-id>` stages the reviewed task snapshot; if review feedback changes the task, rerun `review-ready` before completion.
- Only after the user explicitly approves the current task for completion, run `scripts/forma-workflow.sh complete <issue-id>`.
- After `complete` succeeds, immediately run `scripts/forma-workflow.sh next <issue-id>`; if another unchecked task is returned, start executing it in the same invocation instead of waiting for the user to ask again.

Read these files first:

- `./plans/issue-<id>/plan.md`
- `./plans/issue-<id>/tasks.md`

## Load As Needed

- `references/execution-rules.md`
- `references/implement-notes.md`
- `references/task-runner.md`
- `references/forma-iteration-boundaries.md`
- `references/forma-validation-matrix.md`
- `references/forma-profile-policy.md`

## Conditional References

Use the recorded `Iteration Area` before loading overlay references.

- If `Iteration Area` is `docs-only`, do not load overlay references.
- If `Iteration Area` is `governance`, do not load overlay references.
- If `Iteration Area` is `methodology-verifier`, do not load overlay references.
- If `Iteration Area` is `creator-profile`, do not load overlay references.
- If `Iteration Area` is `generated-baseline`, do not load overlay references.
- If `Iteration Area` is `cross-layer`, do not load overlay references.

## Requirements

- Load and follow `references/task-runner.md` for review-gated task execution.
- Treat this profile stack as Forma-owned project source, not a sanitized public example.
- Keep downstream organization-specific workflow commands, private paths, credentials, and business rules out of Forma examples.
- Do not write the invoking developer's home-directory path into tracked source, docs, profiles, plans, tests, examples, or generated release artifacts.
- Preserve unrelated user work in the dirty worktree and keep commits scoped to the current issue.
- Keep changes scoped to the active issue plan and tasks.
- Read the active plans/issue-<id>/plan.md, tasks.md, current task from scripts/forma-workflow.sh next <issue-id>, relevant source files, and only the references necessary for the current task.
- Record meaningful execution decisions in plans/issue-<id>/implement-notes.md when they affect later tasks or review.
- Run the narrowest relevant test first, then the shared validation gate before review-ready.
- For generated baseline replacements, stage deletions and additions together and verify the committed output path.
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/`
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev forma verify source/skill-creator/`
- Apply workflow validation gate when it is relevant to the current task: `git diff --check`
- Read finalized `plan.md` and use recorded `Iteration Area` before applying conditional overlays; if `Iteration Area` is missing, stop-for-plan-correction.
- If `Iteration Area` is `docs-only`, apply `docs` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, and dist/AGENTS.md when release-surface documentation is in scope before editing Forma documentation.
- If `Iteration Area` is `docs-only`, apply `docs` overlay constraint: Remove stale command examples, deprecated flags, and references to superseded profile locations.
- If `Iteration Area` is `docs-only`, apply `docs` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py`
- If `Iteration Area` is `docs-only`, apply `docs` overlay validation gate when it is relevant to the current task: `git diff --check README.md README.zh-CN.md STRUCTURE.md AGENTS.md dist/AGENTS.md docs`
- If `Iteration Area` is `governance`, apply `governance` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, dist/AGENTS.md when release artifacts are in scope, and active plan files before changing governance or self-management policy.
- If `Iteration Area` is `governance`, apply `governance` overlay validation gate when it is relevant to the current task: `git diff --check README.md README.zh-CN.md STRUCTURE.md AGENTS.md dist/AGENTS.md profiles/forma-self`
- If `Iteration Area` is `methodology-verifier`, apply `methodology` overlay constraint: Keep source/methodology as the canonical source and do not duplicate methodology truth inside source/skill-creator.
- If `Iteration Area` is `methodology-verifier`, apply `methodology` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_verifier.py tests/test_layer_1_dogfood.py`
- If `Iteration Area` is `methodology-verifier`, apply `methodology` overlay validation gate when it is relevant to the current task: `uv run --extra dev forma verify source/skill-creator/`
- If `Iteration Area` is `methodology-verifier`, apply `verifier` overlay constraint: Add paired positive and negative verifier coverage for rule changes.
- If `Iteration Area` is `methodology-verifier`, apply `verifier` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py`
- If `Iteration Area` is `creator-profile`, apply `creator` overlay constraint: Keep generated skill bodies deterministic except for generated_at unless a plan explicitly changes that contract.
- If `Iteration Area` is `creator-profile`, apply `creator` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py`
- If `Iteration Area` is `creator-profile`, apply `profiles` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before changing Forma-owned profiles or generated self-iteration behavior.
- If `Iteration Area` is `creator-profile`, apply `profiles` overlay constraint: Verify every affected top-level profile by running forma create-bundle or forma create-plugin into /tmp, /private/tmp, or $TMPDIR and then running forma verify for at least one target.
- If `Iteration Area` is `creator-profile`, apply `profiles` overlay constraint: After changing profiles/forma-self, generate self-profile output only into a transient path and verify it; install through Codex only when the issue explicitly requires refreshing the local self-iteration workflow.
- If `Iteration Area` is `creator-profile`, apply `profiles` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py`
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, and dist/AGENTS.md before replacing generated baselines or release artifacts that affect documented workflow behavior.
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay constraint: For dist release artifacts, regenerate default no-profile output unless a future issue explicitly changes the release contract; do not commit profiles/forma-self output into dist.
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay constraint: For committed example baselines, regenerate from the owning committed profile and stage removed old directories plus new generated directories together.
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay validation gate when it is relevant to the current task: `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/`
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay validation gate when it is relevant to the current task: `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/`
- If `Iteration Area` is `cross-layer`, apply `methodology` overlay constraint: Keep source/methodology as the canonical source and do not duplicate methodology truth inside source/skill-creator.
- If `Iteration Area` is `cross-layer`, apply `methodology` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_verifier.py tests/test_layer_1_dogfood.py`
- If `Iteration Area` is `cross-layer`, apply `methodology` overlay validation gate when it is relevant to the current task: `uv run --extra dev forma verify source/skill-creator/`
- If `Iteration Area` is `cross-layer`, apply `verifier` overlay constraint: Add paired positive and negative verifier coverage for rule changes.
- If `Iteration Area` is `cross-layer`, apply `verifier` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py`
- If `Iteration Area` is `cross-layer`, apply `creator` overlay constraint: Keep generated skill bodies deterministic except for generated_at unless a plan explicitly changes that contract.
- If `Iteration Area` is `cross-layer`, apply `creator` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py`
- If `Iteration Area` is `cross-layer`, apply `profiles` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before changing Forma-owned profiles or generated self-iteration behavior.
- If `Iteration Area` is `cross-layer`, apply `profiles` overlay constraint: Verify every affected top-level profile by running forma create-bundle or forma create-plugin into /tmp, /private/tmp, or $TMPDIR and then running forma verify for at least one target.
- If `Iteration Area` is `cross-layer`, apply `profiles` overlay constraint: After changing profiles/forma-self, generate self-profile output only into a transient path and verify it; install through Codex only when the issue explicitly requires refreshing the local self-iteration workflow.
- If `Iteration Area` is `cross-layer`, apply `profiles` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py`
- If `Iteration Area` is `cross-layer`, apply `generated` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, and dist/AGENTS.md before replacing generated baselines or release artifacts that affect documented workflow behavior.
- If `Iteration Area` is `cross-layer`, apply `generated` overlay constraint: For dist release artifacts, regenerate default no-profile output unless a future issue explicitly changes the release contract; do not commit profiles/forma-self output into dist.
- If `Iteration Area` is `cross-layer`, apply `generated` overlay constraint: For committed example baselines, regenerate from the owning committed profile and stage removed old directories plus new generated directories together.
- If `Iteration Area` is `cross-layer`, apply `generated` overlay validation gate when it is relevant to the current task: `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/`
- If `Iteration Area` is `cross-layer`, apply `generated` overlay validation gate when it is relevant to the current task: `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/`
- If `Iteration Area` is `cross-layer`, apply `docs` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, and dist/AGENTS.md when release-surface documentation is in scope before editing Forma documentation.
- If `Iteration Area` is `cross-layer`, apply `docs` overlay constraint: Remove stale command examples, deprecated flags, and references to superseded profile locations.
- If `Iteration Area` is `cross-layer`, apply `docs` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py`
- If `Iteration Area` is `cross-layer`, apply `docs` overlay validation gate when it is relevant to the current task: `git diff --check README.md README.zh-CN.md STRUCTURE.md AGENTS.md dist/AGENTS.md docs`

## Output

- Follow `references/output-format.md`.
