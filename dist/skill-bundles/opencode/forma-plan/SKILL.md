---
name: "forma-plan"
description: "Clarify goals, constraints, boundaries, and acceptance criteria."
compatibility: opencode
metadata:
  forma.stage: "shape"
  forma.target: "opencode"
---

# Forma Plan

Clarify goals, constraints, boundaries, and acceptance criteria.

## Interaction Semantics

- Use this skill to converge an executable task contract with the user before any repo plan files are written.
- Stay in clarification or proposal mode until the user confirms the proposal is ready to hand off.
- Keep this skill chat-only: it produces clarification, a proposal, or a handoff; execution work and planning files belong to later stages.

## Mode Check

- First determine whether the current collaboration mode is plan-oriented.
- If the current agent is not in plan mode, stop and tell the user to switch to plan mode before continuing.
- Treat mode switching as host-controlled; continue only after the host environment confirms plan mode.

## Workflow

- Load bundled planning references from the current triggered skill package.
- Always load `references/output-format.md` and `references/plan-stage-rules.md` before deciding whether to clarify, block, propose, or hand off.
- If the user context is still incomplete, continue clarification with the user instead of exploring the repository or writing repo files.
- Classify the issue as `Plan Strategy: step-execution`, `loop-exploration`, or `hybrid`; for loop-exploration, hybrid, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans, settle concrete artifact paths, evidence paths, validation gates, and proof requirements before proposal-ready.
- After the Decision Gate passes, identify the grounding producer needed before the lock stage; if repository facts are needed, hand off to that producer instead of exploring the repository from the plan stage.
- Keep the proposal in chat only. The lock stage writes `plan.md` and `tasks.md`; workflow scripts are outside plan-stage operation.
- After the user reviews and confirms the proposal, stop and hand off to the lock stage to write `plan.md` and `tasks.md`.

## Always Load

- `references/output-format.md`
- `references/plan-stage-rules.md`
- `references/proposal-decision-gate.md`
- `references/grounding-handoff.md`

## Load As Needed


## Requirements

- Treat the plan stage as the convergence step before lock, not as a plan-file-writing skill.
- When loading bundled planning references, resolve them relative to the current triggered skill package.
- Treat user-provided source references as planning context only after their relevant contents are available in the current session or through an explicitly injected/profile-owned source adapter.
- Source-context tools such as GitHub, `gh`, or network access are available only when an injected/profile-owned source adapter provides them. Otherwise ask the user to paste the authoritative source material needed for planning.
- While the user context is still incomplete, stay in clarification mode. Ask only for the missing planning information needed to converge Goal, Scope, Approach, and the validation model for tasks, shared checks, and final issue closure.
- Before the user confirms that the context is sufficient, stay in conversation-level clarification. Repository exploration belongs to grounding; plan files and `forma-workflow.sh` belong to lock.
- Load and follow `references/proposal-decision-gate.md` for the proposal decision gate.
- Load and follow `references/grounding-handoff.md` for grounding handoff selection.

## Output

- Follow `references/output-format.md`.
