---
name: "forma-showhand"
description: "Execute a finalized Forma self-iteration plan automatically when all layer and validation gates pass."
---

# Forma Showhand

Execute a finalized Forma self-iteration plan automatically when all layer and validation gates pass.

## Interaction Semantics

- Use this skill as an automated execution workflow for an already-finalized plan, not as a planning or plan-finalization skill.
- Proceed task by task sequentially. For each task, automatically implement, validate, and record proof through the workflow runner.
- Before each task's implementation starts, preflight likely tools, runtime needs, workspace permissions, and validation commands; request expected permission grants up front.
- When ordinary execution choices need a decision, record the viable options and selected best choice, then proceed without waiting for user approval.
- If unchecked tasks remain after a successful completion, immediately continue with the next task.
- Stop only on validation failure, workflow failure, safety blocker, unavailable prerequisite, escalation denial, or user interruption.

## Workflow

- Read `./plans/issue-<id>/plan.md` and `./plans/issue-<id>/tasks.md`; if either file is missing or still a template, stop and hand off to `finalize-plan` instead of creating or editing plan files.
- Do not run `scripts/forma-workflow.sh init <issue-id>`, do not write `plan.md`, do not write `tasks.md`, and do not commit plan files from `showhand`.
- Loop through all remaining unchecked tasks sequentially. For each task:
  1. Read `scripts/forma-workflow.sh next <issue-id>` to get the source of truth for the current task.
  2. Before implementation, preflight the likely tools, runtimes, connectors, network/filesystem/process permissions, validation commands, and whether the current workspace can grant them; request expected permission grants before starting task execution.
  3. Execute only the current task contract: accepted files/surfaces, validation commands, gates, and proof requirements. Update `plans/issue-<id>/implement-notes.md` when decisions, plan gaps, classifications, deviations, or intentional follow-ups matter.
  4. For ordinary execution choices that would otherwise require user decision, record the options, selected best choice, and rationale in `implement-notes.md`, then execute directly without waiting.
  5. Run `scripts/forma-workflow.sh review-ready <issue-id>`.
  6. Once `review-ready` is successful, automatically run `scripts/forma-workflow.sh complete <issue-id>` without asking the user for review.
  7. If unchecked tasks remain after `complete` succeeds, immediately continue with the next task. Repeat the preflight before starting that task. Stop only on validation failure, workflow failure, safety blocker, unavailable prerequisite, escalation denial, or user interruption.

Read these files first:

- `./plans/issue-<id>/plan.md`
- `./plans/issue-<id>/tasks.md`

## Load As Needed

- `references/execution-rules.md`
- `references/implement-notes.md`
- `references/automated-execution.md`
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

- Load and follow `references/automated-execution.md` for automated execution.
- Treat this profile stack as Forma-owned project source, not a sanitized public example.
- Keep downstream organization-specific workflow commands, private paths, credentials, and business rules out of Forma examples.
- Do not write the invoking developer's home-directory path into tracked source, docs, profiles, plans, tests, examples, or generated release artifacts.
- Preserve unrelated user work in the dirty worktree and keep commits scoped to the current issue.
- Keep changes scoped to the active issue plan and tasks.
- Read the active plans/issue-<id>/plan.md, tasks.md, current task from scripts/forma-workflow.sh next <issue-id>, relevant source files, and only the references necessary for the current task.
- Record meaningful execution decisions in plans/issue-<id>/implement-notes.md when they affect later tasks or review.
- Use showhand only when source-of-truth docs, profile ownership, generated baseline policy, and validation commands are all explicit.
- Stop for plan correction when a change crosses Layer 1, Layer 2, Layer 3, docs, and generated outputs without a task boundary.
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/`
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev forma verify source/skill-creator/`
- Apply workflow validation gate when it is relevant to the current task: `git diff --check`
- Read finalized `plan.md` and use recorded `Iteration Area` before applying conditional overlays; if `Iteration Area` is missing, stop-for-plan-correction.
- If `Iteration Area` is `docs-only`, apply `docs` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before automated documentation edits.
- If `Iteration Area` is `governance`, apply `governance` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, and active plan files before automated governance or self-management policy changes.
- If `Iteration Area` is `creator-profile`, apply `profiles` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before automated Forma-owned profile changes.
- If `Iteration Area` is `creator-profile`, apply `profiles` overlay constraint: After automated profiles/forma-self changes, regenerate the Forma Codex plugin and reinstall it through Codex before closure.
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before automated generated baseline replacement.
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/`
- If `Iteration Area` is `cross-layer`, apply `profiles` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before automated Forma-owned profile changes.
- If `Iteration Area` is `cross-layer`, apply `profiles` overlay constraint: After automated profiles/forma-self changes, regenerate the Forma Codex plugin and reinstall it through Codex before closure.
- If `Iteration Area` is `cross-layer`, apply `generated` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before automated generated baseline replacement.
- If `Iteration Area` is `cross-layer`, apply `generated` overlay validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/`
- If `Iteration Area` is `cross-layer`, apply `docs` overlay constraint: Read README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md before automated documentation edits.

## Output

- Follow `references/output-format.md`.
