---
name: "forma-lock"
description: "Lock the execution plan and task contract."
compatibility: opencode
metadata:
  forma.stage: "seal"
  forma.target: "opencode"
---

# Forma Lock

Lock the execution plan and task contract.

## Interaction Semantics

- Use this skill to materialize an already-settled plan into repository planning files and task contracts.
- Do not reopen brainstorming or fill planning gaps during finalization.
- Keep the planning handoff narrow: write the current issue plan files and stop before execution begins.

## Entry Gate

- Use only the current user-agent conversation and already-present confirmed grounding handoffs or source-adapter outputs to decide whether finalization can begin.
- Before loading planning references, exploring the repository, running `scripts/forma-workflow.sh init <issue-id>`, or writing `plan.md` / `tasks.md`, confirm at summary level that Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer or confirmed grounding handoff, and any applicable Artifact/Evidence Boundary are decision-complete.
- Fail closed. If any unanswered question could still change the deliverable, module scope, implementation shape, artifact/evidence boundary, or acceptance criteria, stop and tell the user what still needs to be clarified.
- After this entry gate passes, `references/planning-rules.md` is the canonical detailed finalization gate. If any detailed planning rule fails, stop in the same blocked format instead of filling gaps through repository exploration.
- Before the gate passes, do not read planning references, do not explore the repository, do not run `scripts/forma-workflow.sh init <issue-id>`, and do not draft `plan.md` or `tasks.md`.

## Workflow

- If `./plans/issue-<id>/plan.md` or `./plans/issue-<id>/tasks.md` is missing, run `scripts/forma-workflow.sh init <issue-id>` from this installed skill package.
- Resolve bundled workflow scripts and references relative to the current triggered skill package; never switch to same-named resources in sibling skill directories, even if their contents match.
- Fill in `plan.md` for the issue, including explicit `Plan Strategy` for new plans; legacy plans without it default to `step-execution`.
- Finalize `tasks.md` for the issue, encoding each task's accepted surface, validation gates, proof obligations, dependencies, and constraints while preserving the structured task schema.
- Run `scripts/forma-workflow.sh check <issue-id>` after finalizing `plan.md` and `tasks.md` and before staging or asking for commit permission; if the check fails, fix the plan/task contract and rerun the check before continuing.
- Stage only the finalized `plan.md` and `tasks.md`, show the staged diff to the user, then commit only that staged snapshot after explicit user permission.

## Read After Gate

- `references/planning-rules.md`
- `references/plan-template.md`
- `references/tasks-template.md`
- `references/finalization-decision-gate.md`
- `references/plan-materialization.md`
- `references/task-structure.md`

## Requirements

- Treat the lock stage as a plan-materialization skill, not a brainstorming skill.
- When invoking `scripts/forma-workflow.sh` or loading bundled planning references, resolve them relative to the current triggered skill package only; do not switch to same-named resources in sibling skill directories, even if the contents match.
- Treat source references in the planning handoff as confirmed only when their relevant contents are already present in the current session or were loaded through an explicitly injected/profile-owned source adapter.
- Do not assume GitHub, `gh`, network access, or any other source-context tool is a base finalization capability. If the handoff depends on an unavailable source reference and no explicit adapter is present, block finalization and ask the user to provide the authoritative material or update the plan.
- Load and follow `references/finalization-decision-gate.md` for the finalization decision gate.
- Load and follow `references/plan-materialization.md` for plan materialization.
- Load and follow `references/task-structure.md` for task structure.

## Output

- Follow `references/output-format.md`.
- Include `Contract Check:` with the latest `scripts/forma-workflow.sh check <issue-id>` result before asking for commit permission.
