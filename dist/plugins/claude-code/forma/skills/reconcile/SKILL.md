---
name: reconcile
description: "Reconcile Forma delivery feedback against stage contracts, issue evidence, and workflow boundaries."
---

# Forma Reconcile

Reconcile Forma delivery feedback against stage contracts, issue evidence, and workflow boundaries.

## Interaction Semantics

- Use this skill as a read-only reconciliation stage after user feedback, review-ready, task completion, or whole-issue completion suggests the delivery may not match the intended workflow.
- Evaluate the current target against the relevant stage-local constraints, bundled references, issue evidence, validation evidence, and current feedback.
- Do not implement changes, do not complete tasks, do not edit `plan.md` or `tasks.md`, and do not write run evidence.
- For every non-`aligned` result, provide a concrete next route that another agent can act on without reinterpreting the feedback.

## Workflow

- Resolve the reconciliation target from explicit user feedback first, then recent Forma skill trigger context, then `.forma-workflow` review cache, then `plans/issue-<id>/tasks.md`, `plans/issue-<id>/runs/task-*.md`, and current diff or commit evidence.
- Build a stage evaluation frame from the current stage `SKILL.md`, bundled references, profile `default` constraints, profile current-stage constraints, issue plan/tasks/notes/runs, validation evidence, and current feedback.
- Classify the result as `aligned`, `acceptable-deviation`, `task-rework`, `delivery-revision`, `plan-rework`, `source-rework`, or `blocked`.
- Route task implementation rework back to the execution workflow with required `implement-notes.md` updates and another review-ready pass.
- Route all-tasks-complete implementation feedback to `delivery-revision`; do not route it to `showhand next` when no unchecked task remains.
- Route plan-level feedback back to the planning workflow without recording it as implementation notes.

## Load As Needed

- `references/reconcile-rules.md`
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

- Load and follow `references/reconcile-rules.md` before classifying feedback.
- Treat recent skill trigger context as a target-resolution hint, not as authoritative evidence when it conflicts with issue artifacts.
- Prefer `blocked` over guessing when the current stage, issue evidence, validation proof, or feedback target cannot be resolved.
- Keep the repository work read-only while reconciling; output the next route instead of applying it.
- Treat this profile stack as Forma-owned project source, not a sanitized public example.
- Keep downstream organization-specific workflow commands, private paths, credentials, and business rules out of Forma examples.
- Do not write the invoking developer's home-directory path into tracked source, docs, profiles, plans, tests, examples, or generated release artifacts.
- Preserve unrelated user work in the dirty worktree and keep commits scoped to the current issue.
- Keep changes scoped to the active issue plan and tasks.
- Resolve the reconciliation target from explicit feedback first, then recent Forma skill trigger context, review cache, task run evidence, and current diff or commit evidence.
- Evaluate feedback against the current stage constraints and bundled references before deciding whether it is implementation rework, delivery revision, plan rework, source rework, aligned, acceptable deviation, or blocked.
- For task implementation rework, require `plans/issue-<id>/implement-notes.md` to record how feedback changed implementation, validation, generated artifacts, or commit/history.
- For plan-level feedback, return to planning without recording the finding as implementation notes.
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/`
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev forma verify source/skill-creator/`
- Apply workflow validation gate when it is relevant to the current task: `git diff --check`
- Carry recorded `Iteration Area` in the grounding handoff when it is available.

## Output

- Use the exact heading `## reconcile-result` when enough evidence exists.
- Include `Target:`, `Stage Frame:`, `Conclusion:`, `Evidence:`, `Deviation:`, `User Feedback Handling:`, and `Recommended Next Step:`.
- Use the exact heading `## blocked` with `Missing:` and `Questions:` when evidence is insufficient.
