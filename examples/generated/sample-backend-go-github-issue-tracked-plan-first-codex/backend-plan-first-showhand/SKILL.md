---
name: "backend-plan-first-showhand"
description: "Execute remaining Go tasks automatically with Go validation gates."
---

# Backend Plan-First Showhand

Execute remaining Go tasks automatically with Go validation gates.

## Interaction Semantics

- Use this skill as an automated execution workflow for an already-finalized plan, not as a planning or plan-finalization skill.
- Proceed task by task sequentially. For each task, automatically implement, validate, and record proof through the workflow runner.
- Before each task's implementation starts, preflight likely tools, runtime needs, workspace permissions, and validation commands; request expected permission grants up front.
- When ordinary execution choices need a decision, record the viable options and selected best choice, then proceed without waiting for user approval.
- If unchecked tasks remain after a successful completion, immediately continue with the next task.
- Stop only on validation failure, workflow failure, safety blocker, unavailable prerequisite, escalation denial, or user interruption.

## Workflow

- Read `./plans/issue-<id>/plan.md` and `./plans/issue-<id>/tasks.md`; if either file is missing or still a template, stop and hand off to `finalize-plan` instead of creating or editing plan files.
- Do not run `scripts/forma-workflow.sh init <issue-id>`, do not write `plan.md`, do not write `tasks.md`, and do not commit plan files from `showhand`.
- Loop through all remaining unchecked tasks sequentially. For each task:
  1. Read `scripts/forma-workflow.sh next <issue-id>` to get the source of truth for the current task.
  2. Before implementation, preflight the likely tools, runtimes, connectors, network/filesystem/process permissions, validation commands, and whether the current workspace can grant them; request expected permission grants before starting task execution.
  3. Execute only the current task contract: accepted files/surfaces, validation commands, gates, and proof requirements. Update `plans/issue-<id>/implement-notes.md` when decisions, plan gaps, classifications, deviations, or intentional follow-ups matter.
  4. For ordinary execution choices that would otherwise require user decision, record the options, selected best choice, and rationale in `implement-notes.md`, then execute directly without waiting.
  5. Run `scripts/forma-workflow.sh review-ready <issue-id>`.
  6. Once `review-ready` is successful, automatically run `scripts/forma-workflow.sh complete <issue-id>` without asking the user for review.
  7. If unchecked tasks remain after `complete` succeeds, immediately continue with the next task. Repeat the preflight before starting that task. Stop only on validation failure, workflow failure, safety blocker, unavailable prerequisite, escalation denial, or user interruption.

Read these files first:

- `./plans/issue-<id>/plan.md`
- `./plans/issue-<id>/tasks.md`

## Load As Needed

- `references/execution-rules.md`
- `references/implement-notes.md`
- `references/automated-execution.md`
- `references/backend-rules.md`
- `references/backend-review-checks.md`

## Requirements

- Load and follow `references/automated-execution.md` for automated execution.
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
- Do not let automated execution bypass developer clarification, contract/source handoff, or plan correction when API or stream impact is unclear.
- Apply profile validation gate when it is relevant to the current task: `python -m pytest tests/`
- Apply profile validation gate when it is relevant to the current task: `go test ./...`

## Output

- Follow `references/output-format.md`.
