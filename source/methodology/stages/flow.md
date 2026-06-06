# Stage Source: flow

This file is the canonical source for the generated stage body. The
renderer composes these sections with target metadata, stage-local
resources, and resolved constraints.

## Description

Execute all remaining tasks from an already-finalized issue plan automatically with preflight, validation, evidence, and safety gates.

## Interaction Semantics

- Use this skill as an automated execution workflow for an already-finalized plan, not as a planning or plan-finalization skill.
- Proceed task by task sequentially. For each task, automatically implement, validate, and commit the evidence.
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
  3. Execute the task, implementing the required features and updating `plans/issue-<id>/implement-notes.md` when decisions, plan gaps, classifications, deviations, or intentional follow-ups matter.
  4. For ordinary execution choices that would otherwise require user decision, record the options, selected best choice, and rationale in `implement-notes.md`, then execute directly without waiting.
  5. Run `scripts/forma-workflow.sh review-ready <issue-id>`.
  6. Once `review-ready` is successful, automatically run `scripts/forma-workflow.sh complete <issue-id>` without asking the user for review.
  7. If unchecked tasks remain after `complete` succeeds, immediately continue with the next task. Repeat the preflight before starting that task. Stop only on validation failure, workflow failure, safety blocker, unavailable prerequisite, escalation denial, or user interruption.

## Adds

{{ include: fragments/flow/automated-execution-adds.md }}

## Output

- Follow `references/output-format.md`.
