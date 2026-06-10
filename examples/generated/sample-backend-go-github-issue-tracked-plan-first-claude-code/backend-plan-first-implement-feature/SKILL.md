---
name: "backend-plan-first-implement-feature"
description: "Execute one planned Go task through tests and review handoff."
---

# Backend Plan-First Implement Feature

Execute one planned Go task through tests and review handoff.

## Interaction Semantics

- Use this skill as a review-gated task executor for one accepted task contract.
- For each task, implement only the current task's accepted files/surfaces, run its validation gates through review-ready, and wait for explicit user approval before completion.
- After an approved task is completed successfully, check for the next task immediately and continue if one remains.
- Stop only when review is needed, no unchecked task remains, validation fails, workflow fails, escalation is needed, or the user interrupts.

## Workflow

- Read `./plans/issue-<id>/plan.md`.
- Use `scripts/forma-workflow.sh next <issue-id>` from this installed skill package to get the current task.
- Resolve `scripts/forma-workflow.sh` relative to the current triggered skill package only; never switch to a same-named script in a sibling skill directory, even if the contents match.
- Implement only the current task by treating `Accept:` as the delivery target and `Validate:` / `Use-Check:` as validation gates and proof obligations; if it is the last remaining task, `review-ready` will also run `## Final Validation`.
- For `loop-batch`, report metric/artifact movement before validation; for `gate`, name the protected decision boundary; for `promote`, write only the surfaces explicitly allowed by the current task.
- Record meaningful execution decisions, plan gaps, classifications, deviations, and follow-ups in `plans/issue-<id>/implement-notes.md` using the bundled notes reference.
- Run `scripts/forma-workflow.sh review-ready <issue-id>` before presenting the current task result for user review.
- `scripts/forma-workflow.sh review-ready <issue-id>` stages the reviewed task snapshot; if review feedback changes the task, rerun `review-ready` before completion.
- Only after the user explicitly approves the current task for completion, run `scripts/forma-workflow.sh complete <issue-id>`.
- After `complete` succeeds, immediately run `scripts/forma-workflow.sh next <issue-id>`; if another unchecked task is returned, start executing it in the same invocation instead of waiting for the user to ask again.

Read these files first:

- `./plans/issue-<id>/plan.md`
- `./plans/issue-<id>/tasks.md`

## Load As Needed

- `references/execution-rules.md`
- `references/implement-notes.md`
- `references/task-runner.md`
- `references/backend-rules.md`
- `references/backend-review-checks.md`

## Requirements

- Load and follow `references/task-runner.md` for review-gated task execution.
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
- Treat user-provided special constraints as local to the generated bundle unless they were promoted into a tracked profile.
- Add or update tests when the task changes behavior.
- Stop and re-plan if implementation requires API or stream changes missing from the sealed plan.
- Call out contract, compatibility, data, or operational risk in the task summary when behavior changes.
- Add or update Go tests when changing Go behavior.
- Apply workflow validation gate when it is relevant to the current task: `python -m pytest tests/`
- Apply workflow validation gate when it is relevant to the current task: `go test ./...`

## Output

- Follow `references/output-format.md`.
