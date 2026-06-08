---
name: "forma-execute"
description: "Execute one accepted task and leave verifiable evidence."
---

# Forma Execute

Execute one accepted task and leave verifiable evidence.

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

## Requirements

- Load and follow `references/task-runner.md` for review-gated task execution.

## Output

- Follow `references/output-format.md`.
