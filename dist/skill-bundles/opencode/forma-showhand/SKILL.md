---
name: "forma-showhand"
description: "Continue remaining tasks, but stop when evidence is insufficient."
compatibility: opencode
metadata:
  forma.stage: "flow"
  forma.target: "opencode"
---

# Forma Showhand

Continue remaining tasks, but stop when evidence is insufficient.

## Interaction Semantics

- Use this skill as an automated execution workflow for an already-locked plan, not as a planning or plan-finalization skill.
- Proceed task by task sequentially. For each task, automatically implement, validate, and record proof through the workflow runner.
- Before each task's implementation starts, preflight likely tools, runtime needs, workspace permissions, and validation commands; request expected permission grants up front.
- When ordinary execution choices need a decision, record the viable options and selected best choice, then proceed without waiting for user approval.
- If unchecked tasks remain after a successful completion, immediately continue with the next task.
- Stop only on validation failure, workflow failure, safety blocker, unavailable prerequisite, escalation denial, or user interruption.

## Workflow

- Read `./plans/issue-<id>/plan.md` and `./plans/issue-<id>/tasks.md`; if either file is missing or still a template, stop and hand off to the lock stage instead of creating or editing plan files.
- Do not run `scripts/forma-workflow.sh init <issue-id>`, do not write `plan.md`, do not write `tasks.md`, and do not commit plan files from `showhand`.
- The workflow runner is mandatory for task selection, review staging, task completion, evidence recording, and task commits. If `next`, `review-ready`, or `complete` fails, stop and report the runner failure; do not recover by parsing `tasks.md` manually, editing checkboxes, creating run evidence, or committing outside the runner.
- Loop through all remaining unchecked tasks sequentially. For each task:
  1. Run `scripts/forma-workflow.sh next <issue-id>` to get the source of truth for the current task. If `next` reports that `plan.md` or `tasks.md` is missing, templated, untracked, modified, staged, or otherwise not locked, stop and hand off to the lock stage for user-confirmed plan commit.
  2. Before implementation, preflight the likely tools, runtimes, connectors, network/filesystem/process permissions, validation commands, and whether the current workspace can grant them; request expected permission grants before starting task execution.
  3. Execute only the current task contract: accepted files/surfaces, validation commands, gates, and proof requirements. Before review, decide whether `plans/issue-<id>/implement-notes.md` is required and update it when decisions, plan gaps, classifications, deviations, or intentional follow-ups matter.
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

## Requirements

- Load and follow `references/automated-execution.md` for automated execution.

## Output

- Follow `references/output-format.md`.
