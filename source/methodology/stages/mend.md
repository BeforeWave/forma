# Stage Source: mend

This file is the canonical source for the generated stage body. The
renderer composes these sections with target metadata, stage-local
resources, and resolved constraints.

## Description

Record same-issue corrective feedback as a locked rework contract without implementing the requested changes.

## Interaction Semantics

- Use this skill when completed or reviewed work needs same-issue corrective follow-up after direct human feedback or after `forma-reconcile` output.
- Materialize the rework contract only when the feedback can be tied to the active issue, current plan boundary, and ordinary task execution model.
- Do not implement code changes, do not complete tasks, do not write run evidence, and do not use a special rework task syntax.
- Keep detailed feedback source, grouping, same-issue rationale, and confirmation state in `plans/issue-<id>/rework.md`; keep `tasks.md` as flat standard task blocks only.

## Workflow

- Resolve the rework target from explicit human feedback first, then from `forma-reconcile` output when present, then from the active issue plan, tasks, runs, review cache, current diff, or commit evidence.
- Load and follow `references/rework-rules.md` before deciding whether the feedback is `task-rework`, `delivery-revision`, `plan-rework`, `source-rework`, or `blocked`.
- For same-issue implementation correction, write or update `plans/issue-<id>/rework.md` with feedback source, classification, same-issue rationale, confirmation state, and appended task ids.
- Append rework tasks to the end of `plans/issue-<id>/tasks.md` as ordinary structured task blocks using `rework-*` task ids and the existing `Accept:` / `Validate:` / `Depends:` / `Constraint:` fields.
- Do not add `## Rework Tasks`, `Source:`, `Feedback:`, grouping labels, or other non-task prose to `tasks.md`.
- Run `scripts/forma-workflow.sh check <issue-id>` after updating `rework.md` and appending tasks and before staging or asking for commit permission; if the check fails, fix the rework task contract and rerun the check before continuing.
- Stage only `plans/issue-<id>/rework.md` and `plans/issue-<id>/tasks.md`, show the staged diff, and commit the rework contract only after explicit user confirmation.
- After the confirmed rework contract is committed and `plan.md` / `tasks.md` are clean, hand execution to `forma-execute` for one task or `forma-showhand` for the remaining appended tasks.

## Adds

- Direct human feedback is sufficient input; `forma-reconcile` can supply the same intake fields but is not required.
- Use the existing task template for appended rework tasks; do not introduce a separate rework task template.
- Treat plan-level feedback as planning work, not implementation rework, and route it back to planning or lock instead of appending tasks.
- Prefer `blocked` over guessing when target issue, feedback source, same-issue rationale, required validation, or user confirmation is missing.

## Output

- Use the exact heading `## rework-contract` when a rework contract is ready for user confirmation.
- Include `Issue:`, `Source:`, `Classification:`, `Same-Issue Rationale:`, `Rework Ledger:`, `Tasks Appended:`, `Contract Check:`, `Staged Diff:`, and `Required Confirmation:`.
- Use the exact heading `## blocked` with `Missing:` and `Questions:` when the rework contract cannot be materialized safely.
