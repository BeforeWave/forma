# Reconcile Rules

Use these rules when evaluating whether a delivered workflow result still
matches the active Forma stage contract and the user's feedback.

## Target Resolution

- Prefer an explicit user target, such as a named task, stage, file, commit, or generated artifact.
- If the user does not name a target, use the most recent Forma skill trigger from the current conversation as a hint:
  - A plugin-local or qualified trigger whose final component is `plan` maps to `shape`.
  - A plugin-local or qualified trigger whose final component is `ground` maps to `gauge`.
  - A plugin-local or qualified trigger whose final component is `lock` maps to `seal`.
  - A plugin-local or qualified trigger whose final component is `execute` maps to `pour`.
  - A plugin-local or qualified trigger whose final component is `showhand` maps to `flow`, then the latest task/run evidence decides the concrete work item.
  - Direct skill triggers use the `forma-*` pattern and map by the same stage suffix.
  - A trigger whose final component is `reconcile` maps to the stage being reconciled, not to itself.
- If `.forma/state/workflow/issue-<id>/review-state.env` exists, use its task number and task text as review-cache evidence.
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

## Quality Gate

Do not use reconciliation as a low-bar completion check. Passing tests,
finishing tasks, or satisfying the literal task contract is necessary but not
sufficient for `aligned`.

Compare the delivery against `plan.md` Scope, Approach, Constraints,
Acceptance Criteria, Validation, task `Accept:` / `Validate:` lines, stage and
profile constraints, generated artifact boundaries, and required evidence. Do
not return `aligned` from task checkboxes, passing tests, or a literal
`Accept:` line alone.

Treat low-standard completion as not aligned when the implementation proves a
weaker surrogate, uses mock or browser-only evidence where real runtime or
sidecar proof was required, changes the wrong source layer, patches only one
visible case while the plan required durable source behavior, or leaves the
reviewer to infer that a stricter plan requirement was satisfied.

Return `aligned` only when both points hold:

- Contract fit: the delivery satisfies the relevant stage frame, issue
  contract, validation model, artifact boundary, and evidence requirements.
- Best practical outcome: within the confirmed scope, the delivery uses the
  right source layer, keeps long-term maintenance cost reasonable, reduces
  future agent misunderstanding, matches the user's product mental model, keeps
  product boundaries clear, and fixes recurring behavior at the durable source
  rather than only patching one visible case.

If a delivery is adequate enough to continue but is clearly not the best
practical outcome, do not return `aligned`. Route it to:

- `acceptable-deviation` when the tradeoff is explicit, bounded, and does not
  change the goal, stage boundary, validation model, artifact boundary, or
  required evidence.
- `delivery-revision` when the completed same-issue delivery needs scoped
  implementation correction.
- `source-rework` when the durable source, generated artifact source, profile
  source, or installed workflow surface must change before the result should be
  accepted.
- `plan-rework` when the better outcome would require changing Goal, Scope,
  Approach, Validation, task structure, or issue-level acceptance.

## Conclusions

- `aligned`: delivery matches the stage frame, satisfies the active contract, and is the best practical outcome within the current scope; no follow-up remains.
- `acceptable-deviation`: a deviation exists but does not change the goal, stage boundary, validation model, artifact boundary, or required evidence.
- `task-rework`: the current or next unchecked task must be changed and rerun through review-ready.
- `delivery-revision`: all tasks are complete, but the same issue needs scoped implementation correction. Route it to the rework stage to append ordinary rework tasks; the later execution must record `delivery-revision` inside the standard current-task `implement-notes.md` section, not a custom top-level section.
- `plan-rework`: the feedback changes Goal, Scope, Approach, Validation, task structure, or issue-level acceptance. Return to the planning workflow and do not record it as implementation notes.
- `source-rework`: an upstream source, grounding handoff, generated artifact source, profile source, or installed workflow surface needs correction before execution continues.
- `blocked`: the conclusion would be speculative because target, stage, evidence, validation, or feedback is missing or contradictory.

## Route Requirements

- For `task-rework`, name the execution skill or automated workflow to resume, the task id, the feedback to apply, the required validation, and the review-ready requirement.
- For `delivery-revision`, name the completed task or delivered surface, route to the rework stage for ordinary appended tasks, require the later execution task's standard `implement-notes.md` section to record `delivery-revision`, rerun relevant validation, and handle commit/history cleanup according to the issue workflow.
- For `plan-rework`, name the planning stage to resume and the exact planning dimension that changed.
- For `source-rework`, name the owning source producer or generated artifact surface that must be corrected.
- For `blocked`, list only the missing or conflicting evidence and ask at most three concrete questions.
