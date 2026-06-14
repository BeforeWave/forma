# Rework Rules

Use these rules to turn corrective feedback into a same-issue rework contract
without implementing the changes.

## Intake Sources

- Prefer explicit human feedback from the current conversation.
- When available, use `forma-reconcile` output as structured intake for target, stage frame, conclusion, evidence, deviation, and recommended next step.
- Do not require `forma-reconcile` before rework. Direct human feedback can independently drive rework when the issue, delivered surface, and requested correction are clear.
- If direct feedback conflicts with `forma-reconcile` output or issue evidence, report `blocked` unless the user resolves the conflict.

## Classifications

- `task-rework`: an unchecked or review-ready task must be corrected before completion.
- `delivery-revision`: all planned tasks are complete, but the same issue needs scoped implementation correction.
- `plan-rework`: the feedback changes Goal, Scope, Approach, Validation, task structure, or issue-level acceptance.
- `source-rework`: an upstream source, grounding handoff, profile source, generated artifact source, or installed workflow surface needs correction before tasks can be rewritten.
- `blocked`: target, evidence, same-issue rationale, validation, or confirmation is missing or contradictory.

Only `task-rework` and `delivery-revision` may append rework tasks. Route
`plan-rework` back to planning or lock, and route `source-rework` to the owning
source producer before writing execution tasks.

## Same-Issue Gate

Before writing `rework.md` or appending tasks, confirm all of these:

- the active issue id is known
- the feedback targets work inside the active issue's Goal and Scope
- the correction can be executed as ordinary task work without changing the plan-level contract
- the requested validation can be expressed through standard `Validate:` and `Use-Check:` fields
- the user has confirmed this is same-issue rework or the current conversation makes that explicit

If any point fails, return `blocked`, `plan-rework`, or `source-rework` instead
of appending tasks.

## Rework Ledger

Store feedback source, grouping, and rationale in `plans/issue-<id>/rework.md`,
not in `tasks.md`.

Use this ledger shape:

```md
# Rework Ledger

## Rework 001: <short topic>

Source:
- <direct-human-feedback | forma-reconcile | direct-human-feedback + forma-reconcile>

Feedback:
- <sanitized feedback summary>

Classification:
- <task-rework | delivery-revision>

Same-Issue Rationale:
- <why this remains inside the active issue plan and task contract>

User Confirmation:
- <pending | confirmed: <short confirmation source>>

Appended Tasks:
- rework-001-<slug>
```

Append new ledger entries instead of overwriting earlier entries. Keep raw
private data, secrets, downstream-only details, and non-temporary absolute paths
out of the ledger.

## Task Appending

Append rework tasks to the end of `plans/issue-<id>/tasks.md` using the existing
task structure:

```text
- [ ] [rework-001-<slug>] <short task title>
Accept: Task Type=step; <same-issue corrective outcome>
Validate: <focused validation command>
Use-Check: <shared check name when applicable>
Depends: <completed or prerequisite task id>
Constraint: <write boundary or non-goal>
```

Rules:

- use `rework-<number>-<slug>` ids and continue numbering from existing rework entries
- do not add a `## Rework Tasks` heading
- do not add `Source:`, `Feedback:`, grouping labels, or explanatory prose to `tasks.md`
- do not invent a rework-specific task template
- include enough `Accept:` and `Validate:` detail that `forma-execute` or `forma-showhand` can run the tasks without reinterpreting the original feedback

## Confirmation And Commit

After updating `rework.md` and `tasks.md`:

- run `scripts/forma-workflow.sh check <issue-id>` before staging or asking for commit permission
- if the check fails, fix the rework task contract and rerun the check; do not stage or commit the rework contract while the check is failing
- stage only `plans/issue-<id>/rework.md` and `plans/issue-<id>/tasks.md`
- show the staged diff
- require explicit user confirmation before committing the rework contract
- do not write `plans/issue-<id>/runs/`
- do not mark tasks complete
- do not implement source changes

## Execution Handoff

After the rework contract is committed and `plan.md` / `tasks.md` are clean,
execution uses the existing skills:

- use `forma-execute` for one appended rework task
- use `forma-showhand` for all remaining appended rework tasks

`execute` and `showhand` do not need special rework syntax. They consume the
appended task blocks as ordinary tasks and record proof through the normal
`review-ready` / `complete` workflow.
