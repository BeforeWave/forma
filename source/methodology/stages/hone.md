# Stage Source: hone

This file is the canonical source for the generated stage body. The
renderer composes these sections with target metadata, stage-local
resources, and resolved constraints.

## Description

Reconcile delivered workflow results against the current stage contract, issue evidence, and user feedback, then route the next action without implementing changes.

## Interaction Semantics

- Use this skill as a read-only reconciliation stage after user feedback, review-ready, task completion, or whole-issue completion suggests the delivery may not match the intended workflow.
- Evaluate the current target against the relevant stage-local constraints, bundled references, issue evidence, validation evidence, current feedback, and best practical outcome within the task scope.
- Do not implement changes, do not complete tasks, do not edit `plan.md` or `tasks.md`, and do not write run evidence.
- For every non-`aligned` result, provide a concrete next route that another agent can act on without reinterpreting the feedback.

## Workflow

- Resolve the reconciliation target from explicit user feedback first, then recent Forma skill trigger context, then `.forma/state/workflow` review cache, then `plans/issue-<id>/tasks.md`, `plans/issue-<id>/runs/task-*.md`, and current diff or commit evidence.
- Build a stage evaluation frame from the current stage `SKILL.md`, bundled references, profile `default` constraints, profile current-stage constraints, issue plan/tasks/notes/runs, validation evidence, and current feedback.
- Classify the result as `aligned`, `acceptable-deviation`, `task-rework`, `delivery-revision`, `plan-rework`, `source-rework`, or `blocked`; use `aligned` only when the delivery both fits the contract and is the best practical outcome for the current scope.
- Route task implementation rework back to the execution workflow with required `implement-notes.md` updates and another review-ready pass.
- Route all-tasks-complete implementation feedback to `delivery-revision`; do not route it to `showhand next` when no unchecked task remains.
- Route plan-level feedback back to the planning workflow without recording it as implementation notes.

## Adds

- Load and follow `references/reconcile-rules.md` before classifying feedback.
- Treat recent skill trigger context as a target-resolution hint, not as authoritative evidence when it conflicts with issue artifacts.
- Prefer `blocked` over guessing when the current stage, issue evidence, validation proof, or feedback target cannot be resolved.
- Keep the repository work read-only while reconciling; output the next route instead of applying it.

## Output

- Use the exact heading `## reconcile-result` when enough evidence exists.
- Include `Target:`, `Stage Frame:`, `Conclusion:`, `Evidence:`, `Deviation:`, `User Feedback Handling:`, and `Recommended Next Step:`.
- Use the exact heading `## blocked` with `Missing:` and `Questions:` when evidence is insufficient.
