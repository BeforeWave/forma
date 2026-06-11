---
name: "backend-plan-first-plan"
description: "Use only in Plan mode to clarify Goal/Scope/Approach/Validation, Plan Strategy, selected grounding producer, and any applicable Artifact/Evidence Boundary for backend work without assuming a specific language stack before lock. Chat-only: do not inspect repo; do not write plan.md/tasks.md; return clarifying/blocked when decisions remain open."
---

# Backend Plan-First Plan

Use only in plan-oriented collaboration to clarify Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer, and any applicable Artifact/Evidence Boundary for backend work without assuming a specific language stack before lock.

## Interaction Semantics

- Use this skill to converge an executable task contract with the user before any repo plan files are written.
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
- Always load `references/output-format.md` and `references/plan-stage-rules.md` before deciding whether to clarify, block, propose, or hand off.
- If the user context is still incomplete, continue clarification with the user instead of exploring the repository or writing repo files.
- Classify the issue as `Plan Strategy: step-execution`, `loop-exploration`, or `hybrid`; for loop-exploration, hybrid, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans, settle concrete artifact paths, evidence paths, validation gates, and proof requirements before proposal-ready.
- After the Decision Gate passes, identify the grounding producer needed before the lock stage; if repository facts are needed, hand off to that producer instead of exploring the repository from the plan stage.
- Keep the proposal in chat only. Do not write `plan.md`, do not write `tasks.md`, and do not execute workflow scripts.
- After the user reviews and confirms the proposal, stop and hand off to the lock stage to write `plan.md` and `tasks.md`.

## Always Load

- `references/output-format.md`
- `references/plan-stage-rules.md`
- `references/proposal-decision-gate.md`
- `references/grounding-handoff.md`

## Load As Needed

- `references/backend-rules.md`
- `references/backend-review-checks.md`
- `references/script-resource-adapter.md`

## Requirements

- Treat the plan stage as the convergence step before lock, not as a plan-file-writing skill.
- First determine whether the current collaboration mode is plan-oriented. If the current agent is not in plan mode, stop and tell the user to switch to plan mode before continuing deeper plan shaping.
- Do not claim that you switched modes unless the host environment explicitly confirms it.
- When loading bundled planning references, resolve them relative to the current triggered skill package only; do not borrow same-named resources from sibling skill directories.
- Always load `references/output-format.md` and `references/plan-stage-rules.md` before deciding whether to clarify, block, propose, or hand off.
- Treat user-provided source references as planning context only after their relevant contents are available in the current session or through an explicitly injected/profile-owned source adapter.
- Do not assume GitHub, `gh`, network access, or any other source-context tool is a base plan-first capability. If a generated bundle includes an injected/profile-owned source adapter, follow that adapter's stage-specific reference and script instructions; otherwise ask the user to paste the authoritative source material needed for planning.
- While the user context is still incomplete, stay in clarification mode. Ask only for the missing planning information needed to converge Goal, Scope, Approach, and the validation model for tasks, shared checks, and final issue closure.
- Before the user confirms that the context is sufficient, do not explore the repository, do not write repo files, do not execute bundled scripts other than explicitly injected/profile-owned source adapters, and do not draft `plan.md` or `tasks.md`.
- Do not execute `forma-workflow.sh` from this skill.
- Load and follow `references/proposal-decision-gate.md` for the proposal decision gate.
- Load and follow `references/grounding-handoff.md` for grounding handoff selection.
- Keep generated guidance generic and avoid organization-specific paths, credentials, or workflow commands.
- Keep default constraints minimal; route heavy workflow rules to stage-specific constraints or conditional overlays.
- Prefer existing repository conventions and native validation commands.
- Keep changes scoped to the accepted task and preserve unrelated user work.
- Keep changes scoped to the backend behavior required by the current issue.
- Prefer fixing the root cause over masking symptoms.
- Preserve backward compatibility unless the plan explicitly allows breaking changes.
- Avoid leaking sensitive data through logs, errors, or debug output.
- Run the project's Go formatter on edited Go files.
- Prefer module-local Go tests when available.
- This sample demonstrates tracked profile composition without organization-specific workflow details.
- Classify whether repeated workflow behavior belongs in a tracked profile or only in the current temporary injection.
- Settle whether the request changes public API behavior, service behavior, stream payloads, persistence, or data flow.
- Distinguish API or stream contract-visible changes from internal logic, storage, queue, or computation changes before proposal-ready.
- When GitHub issue URLs are source-of-truth refs, load and follow `references/script-resource-adapter.md`, then run `python3 scripts/github_issue_context.py <issue-url-or-user-text>` before deciding planning context is incomplete.
- Settle workflow decision-gate dimension before proposal-ready: API or stream impact
- Settle workflow decision-gate dimension before proposal-ready: Data migration or persistence impact
- Apply workflow validation gate when it is relevant to the current task: `python -m pytest tests/`
- Apply workflow validation gate when it is relevant to the current task: `go test ./...`

## Output

- Follow `references/output-format.md`.
