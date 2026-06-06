# Stage Source: shape

This file is the canonical source for the generated stage body. The
renderer composes these sections with target metadata, stage-local
resources, and resolved constraints.

## Description

Use only in plan-oriented collaboration to clarify Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer, and any applicable Artifact/Evidence Boundary before plan finalization.

## Interaction Semantics

- Use this skill to converge an executable plan with the user before any repo plan files are written.
- Stay in clarification or proposal mode until the user confirms the proposal is ready to hand off.
- Do not start execution work or materialize planning files from this skill.

## Mode Check

- First determine whether the current collaboration mode is plan-oriented.
- If the current agent is not in plan mode, stop and tell the user to switch to plan mode before continuing.
- Do not pretend that you switched modes unless the host environment explicitly confirms it.

## Workflow

- First determine whether the current collaboration mode is plan-oriented.
- If the agent is not in plan mode, stop and tell the user to switch to plan mode before any deeper plan shaping.
- Load bundled planning references only from the current triggered skill package; never switch to same-named resources in sibling skill directories.
- Always load `references/output-format.md` and `references/plan-issue-rules.md` before deciding whether to clarify, block, propose, or hand off.
- If the user context is still incomplete, continue clarification with the user instead of exploring the repository or writing repo files.
- Classify the issue as `Plan Strategy: step-execution`, `loop-exploration`, or `hybrid`; for loop-exploration, hybrid, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans, settle the Artifact/Evidence Boundary before proposal-ready.
- After the Decision Gate passes, identify the grounding producer needed before `finalize-plan`; if repository facts are needed, hand off to that producer instead of exploring the repository from `plan-issue`.
- Keep the proposal in chat only. Do not write `plan.md`, do not write `tasks.md`, and do not execute workflow scripts.
- After the user reviews and confirms the proposal, stop and hand off to `finalize-plan` to write `plan.md` and `tasks.md`.

## Adds

- Treat `plan-issue` as the convergence step before `finalize-plan`, not as a plan-file-writing skill.
- First determine whether the current collaboration mode is plan-oriented. If the current agent is not in plan mode, stop and tell the user to switch to plan mode before continuing deeper plan shaping.
- Do not claim that you switched modes unless the host environment explicitly confirms it.
- When loading bundled planning references, resolve them relative to the current triggered skill package only; do not borrow same-named resources from sibling skill directories.
- Always load `references/output-format.md` and `references/plan-issue-rules.md` before deciding whether to clarify, block, propose, or hand off.
- Treat user-provided source references as planning context only after their relevant contents are available in the current session or through an explicitly injected/profile-owned source adapter.
- Do not assume GitHub, `gh`, network access, or any other source-context tool is a base plan-first capability. If a generated suite includes an injected/profile-owned source adapter, follow that adapter's stage-specific reference and script instructions; otherwise ask the user to paste the authoritative source material needed for planning.
- While the user context is still incomplete, stay in clarification mode. Ask only for the missing planning information needed to converge Goal, Scope, Approach, and the validation model for tasks, shared checks, and final issue closure.
- Before the user confirms that the context is sufficient, do not explore the repository, do not write repo files, do not execute bundled scripts other than explicitly injected/profile-owned source adapters, and do not draft `plan.md` or `tasks.md`.
- Do not execute `forma-workflow.sh` from this skill.
{{ include: fragments/shape/decision-gate-adds.md }}
{{ include: fragments/shape/handoff-adds.md }}

## Output

- Follow `references/output-format.md`.
