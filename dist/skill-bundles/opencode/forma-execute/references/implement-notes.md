# Implement Notes

Use this reference when a plan-first execute-stage or automated execution task discovers execution details that are not already captured by the task plan.

`implement-notes.md` is an execution decision journal, not an operation log. Record decisions that help the next task or reviewer understand why work was handled a certain way. Do not list every command or file touch.

For the execute stage, update the notes before presenting the task for review when the current task produces meaningful execution decisions or follow-ups.

For automated execution, update the notes during the automated task loop when a decision, gap, classification, deviation, or follow-up should carry forward to later tasks or final review.

When automated execution makes an ordinary execution decision without waiting for the user, record the viable options, the selected best option, and the rationale in `Decision Notes:` before continuing. Do not use this to invent missing requirements, bypass permission approval, or skip required workflow gates.

Do not record a process-gate exception as an execution decision. If the current task would skip or bypass workflow runner, approval, validation, safety, plan-lock, or plan-correction gates, stop and return to the required gate instead of putting that exception in `Decision Notes:`.

Use `scripts/forma-workflow.sh notes-template <issue-id>` to print a current-task section skeleton when starting or updating the notes file. If `implement-notes.md` is changed, `review-ready` checks that it has a `# Implement Notes` title, a section for the current task, and an `Outcome:` field.

Recommended issue-local path:

```text
plans/issue-<id>/implement-notes.md
```

Add or update a task section when any of these occur:

- a non-trivial implementation decision was made beyond the task text
- the plan missed a detail that affected execution
- blockers, skipped items, or retry-later items were classified
- execution intentionally deviated from the plan
- work was intentionally deferred as a follow-up because it was outside the current task

Keep notes sanitized. Do not include secrets, raw request or response payloads, local fixture values, private identifiers, or downstream project-specific details copied from another repository.

## Format

```md
# Implement Notes

## Task <number>: <task-id>

Outcome:
- <task result, metric change, or artifact effect>

Decision Notes:
- <key execution decision and reason, including options considered for autonomous execution choices, or "None beyond the task plan">

Plan Gaps Found:
- <plan gap that affected execution, or "None">

Classifications:
- <blocked/skipped/retry-later categories and why, or "None">

Deviations From Plan:
- <what changed and why it was necessary, or "None">

Follow-ups:
- <out-of-scope issues intentionally not fixed now, or "None">
```
