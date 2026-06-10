# Reconcile Rules

Use these rules when evaluating whether a delivered workflow result still
matches the active Forma stage contract and the user's feedback.

## Target Resolution

- Prefer an explicit user target, such as a named task, stage, file, commit, or generated artifact.
- If the user does not name a target, use the most recent Forma skill trigger from the current conversation as a hint:
  - `forma-plan` maps to `shape`.
  - `forma-ground` maps to `gauge`.
  - `forma-lock` maps to `seal`.
  - `forma-execute` maps to `pour`.
  - `forma-showhand` maps to `flow`, then the latest task/run evidence decides the concrete work item.
  - `forma-reconcile` maps to the stage being reconciled, not to itself.
- If `.forma-workflow/issue-<id>/review-state.env` exists, use its task number and task text as review-cache evidence.
- If all tasks are complete, use `tasks.md`, `runs/task-*.md`, current diff, and commit history to identify the delivered surface. Do not route to `showhand next` when no unchecked task exists.
- When trigger context and issue evidence conflict, report the conflict and return `blocked` unless the user feedback clearly resolves it.

## Stage Evaluation Frame

Evaluate feedback against only the sources that are actually available:

- the current stage `SKILL.md`
- bundled references loaded by that stage
- profile `default` constraints
- profile constraints for the current stage
- `plans/issue-<id>/plan.md`
- `plans/issue-<id>/tasks.md`
- `plans/issue-<id>/implement-notes.md`
- `plans/issue-<id>/runs/task-*.md`
- validation logs, current diff, or final commit diff
- current user feedback

Do not treat the plan alone as the source of truth when stage constraints,
profile rules, generated artifact boundaries, or validation evidence provide a
more specific contract.

## Conclusions

- `aligned`: delivery matches the stage frame and no follow-up remains.
- `acceptable-deviation`: a deviation exists but does not change the goal, stage boundary, validation model, artifact boundary, or required evidence.
- `task-rework`: the current or next unchecked task must be changed and rerun through review-ready.
- `delivery-revision`: all tasks are complete, but the same issue needs scoped implementation correction. The next execution must update `plans/issue-<id>/implement-notes.md` with a `## Delivery Revision: <topic>` section.
- `plan-rework`: the feedback changes Goal, Scope, Approach, Validation, task structure, or issue-level acceptance. Return to the planning workflow and do not record it as implementation notes.
- `source-rework`: an upstream source, grounding handoff, generated artifact source, profile source, or installed workflow surface needs correction before execution continues.
- `blocked`: the conclusion would be speculative because target, stage, evidence, validation, or feedback is missing or contradictory.

## Route Requirements

- For `task-rework`, name the execution skill or automated workflow to resume, the task id, the feedback to apply, the required validation, and the review-ready requirement.
- For `delivery-revision`, name the completed task or delivered surface, require an `implement-notes.md` delivery revision section, rerun relevant validation, and handle commit/history cleanup according to the issue workflow.
- For `plan-rework`, name the planning stage to resume and the exact planning dimension that changed.
- For `source-rework`, name the owning source producer or generated artifact surface that must be corrected.
- For `blocked`, list only the missing or conflicting evidence and ask at most three concrete questions.
