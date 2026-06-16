# Execution Rules

Use these rules for plan-first task execution skills.

The workflow runner is the authority for task selection, review staging,
evidence, completion, and task commits. Resolve bundled `scripts/*` and
`references/*` relative to the current triggered skill package, then use that
package's `scripts/forma-workflow.sh` for all runner operations.

- Read `plan.md` first, then `tasks.md`.
- Use `scripts/forma-workflow.sh next <issue-id>` to get the current task text.
- Treat the `next` output as the source of truth for the current task.
- If `next` fails, stop on that workflow error instead of reconstructing task state manually.
- `scripts/forma-workflow.sh` auto-detects legacy and structured task files. Legacy checklist lines still work for backward compatibility, but new tasks must use the structured task contract.
- Use `tasks.md` only for surrounding context.
- Keep `plan.md`, task order, task completion marks, run evidence, and task commits under workflow-runner control.
- During execution, the only additional current-issue file allowed under `./plans/issue-<id>/` is `implement-notes.md`; all other plan-directory edits remain workflow-controlled.
- Apply minimal changes and keep unrelated refactors out of the current task.
- Showhand may override the user-approval rules below only when the triggered showhand skill explicitly authorizes automatic completion.
- For non-showhand execution skills, work one workflow task at a time; do not move on to the next task before the current task is review-ready and, after user approval, completed.
- The agent may decompose execution internally into steps such as inspect, implement, test, and validate. Keep that decomposition inside the current planned task unless `plan.md` / `tasks.md` explicitly define multiple plan tasks.
- Infer missing `Plan Strategy` as `step-execution` and missing `Task Type` as `step`; legacy plans can execute without being rewritten first.
- Treat the current task's `Accept:` as the delivery target and `Validate:` / `Use-Check:` as validation gates and proof obligations, not as replacement goals.
- Keep diagnostics, output schema expansion, adjacent cleanup, and nearby refactors out of the task unless required by the current `Accept:` or needed to prevent unsafe formal/destructive writes or decision-critical mistakes.
- For `Task Type=loop-batch`, prioritize metric/artifact movement and report that outcome before validation details; never allow empty selection or failed filtering to fall back to an unintended full run.
- For `Task Type=gate`, require a decision-critical boundary in the task text, such as protecting later selection, closure, artifact acceptance, promotion, or destructive write decisions; otherwise record the issue as follow-up instead of implementing generic cleanup.
- For `Task Type=promote`, require explicit allowed write surfaces and prerequisite evidence in the task before writing source-of-truth, long-lived assets, production-like config, or other hard-to-revert surfaces.
- Record meaningful execution decisions, plan gaps, classifications, deviations, and intentional follow-ups in `plans/issue-<id>/implement-notes.md`; this notes file is an execution decision journal, not a command log.
- Use `scripts/forma-workflow.sh notes-template <issue-id>` when you need a current-task `implement-notes.md` section skeleton; if `implement-notes.md` is changed, `review-ready` checks its title, current task section, and `Outcome:` field.
- For non-showhand execution skills, first implement the current task, run `scripts/forma-workflow.sh review-ready <issue-id>`, and present the review-ready result for user review.
- For structured tasks, `review-ready` requires the current task's `Validate:` lines, any referenced `Use-Check:` shared checks, and when applicable `## Final Validation`; documentation-only work still needs the explicit `# no-programmatic-validation: <reason>` marker.
- Validation commands run in a non-login, non-interactive Bash process that inherits the invoking process environment, ignores user profile and rc files, and clears `BASH_ENV` / `ENV` so shell startup hooks cannot inject validation behavior.
- For behavior-changing tasks, put the proving tests in the current task's `Validate:` lines, shared `Use-Check:` references, or `## Final Validation` instead of treating validation as a single issue-wide gate on every task.
- `scripts/forma-workflow.sh review-ready <issue-id>` stages the reviewed task snapshot in the Git index; if review feedback changes the task, rerun `review-ready` to refresh that snapshot before completion.
- For non-showhand execution skills, wait for explicit user approval before running `scripts/forma-workflow.sh complete <issue-id>`.
- After user approval, run `scripts/forma-workflow.sh complete <issue-id>`.
- `scripts/forma-workflow.sh review-ready <issue-id>` must validate dependencies before review readiness; if a task depends on unfinished task ids, it must stay open.
- `scripts/forma-workflow.sh complete <issue-id>` must see the same staged snapshot that `review-ready` prepared and must fail if there are unstaged post-review edits.
- If `review-ready` or `complete` fails, fix the failure and rerun the workflow command. Manual staging, task completion marks, run evidence, or task commits are not valid recovery paths.
- For non-showhand execution skills, after `scripts/forma-workflow.sh complete <issue-id>` succeeds, immediately run `scripts/forma-workflow.sh next <issue-id>`.
- If `next` returns another unchecked task, treat it as the current task and start executing it in the same invocation instead of waiting for a new user request.
- If `next` reports no unchecked tasks remain, stop and report the completed issue state.
- Generate evidence, mark the task complete, and create the task commit only through `scripts/forma-workflow.sh complete <issue-id>`.
- Completion is determined by repository state and review-ready validation results, not by self-report.
- `scripts/forma-workflow.sh review-ready <issue-id>` may write transient review cache state under `.forma/state/workflow/`; do not read or migrate legacy `.forma-workflow/` cache.
- `scripts/forma-workflow.sh complete <issue-id>` records task evidence under `./plans/issue-<id>/runs/`.
- If validation fails, the task remains unchecked and no commit is created.
