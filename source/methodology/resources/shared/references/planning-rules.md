# Planning Rules

Use these rules as the canonical detailed finalization gate for plan-first lock
skills. Stage entry text is only the quick precheck; if another lock-stage
instruction seems looser, this reference wins.

- Resolve bundled `scripts/*` and `references/*` relative to the current triggered skill package.
- Use the lock stage only after the current conversation has already converged on an executable plan.
- Before initializing the workspace or writing the final plan, confirm from the current user-agent conversation and already-present confirmed grounding handoffs or source-adapter outputs that Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer or confirmed grounding handoff, and any applicable Artifact/Evidence Boundary are decision-complete.
- The lock stage fails closed until all execution-shaping questions are settled. If an unanswered question could change the deliverable, module scope, implementation shape, or acceptance criteria, use the compact `blocked` format from `references/output-format.md` and name only the unconverged dimensions.
- Treat documentation-only, analysis-only, and `# no-programmatic-validation: <reason>` plans as explicit user-conversation decisions; infer them only when the conversation settles that no code behavior, code-owned definitions, or runtime logic needs to change.
- Treat Goal as unconverged unless the current conversation explicitly settles the concrete deliverable to produce, not just the high-level topic.
- Treat Scope as unconverged unless the current conversation explicitly settles both the in-scope work and the key out-of-scope boundaries.
- Treat Approach as unconverged unless the current conversation explicitly settles the intended deliverable shape, the concrete surfaces to touch, and whether the work adds new assets or edits existing ones. The lock stage should assume the destination itself is a planning decision: broad directions such as "under the auth module", "write a markdown doc", or "add a file in that area" are not enough if the agent would still need to choose the actual file path, file count, or touched files.
- Treat Validation as unconverged unless the current conversation explicitly settles the task-local validation contract, any reusable task-safe shared checks, and the issue-level final validation or explicit review-only standard.
- Treat Final Validation as unconverged if any proposed command line depends on shell state from a previous line. Each final validation line must be self-contained; fold setup, command execution, and cleanup into one line when a smoke check needs multiple shell operations.
- Treat Plan Strategy as unconverged for new plans unless the conversation explicitly selects `step-execution`, `loop-exploration`, or `hybrid`; existing plans without this field default to `step-execution`.
- For `loop-exploration` or `hybrid`, settle baseline metric, target metric or convergence threshold, batch selection, batch size, artifact path/type, stop/skip/retry rules, no-full-rerun guard, write boundary, and final validation before finalization.
- Treat grounding as unconverged unless the current conversation includes a selected grounding producer still to be run, or a confirmed grounding handoff whose known facts are sufficient for the final plan.
- Treat the Artifact/Evidence Boundary as unconverged for `loop-exploration`, `hybrid`, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans unless artifact paths, evidence paths, committed/gitignored/transient output policy, source-of-truth status, state or environment assumptions, proof gates, metadata/provenance, write boundaries, and final validation are explicit in the current conversation.
- When multiple requirement, design, contract, solution, grounding, or conversation inputs are present, treat `Source-of-truth refs` as unconverged unless the current conversation states precedence for the sources actually present.
- Required proof stays at the strength and timing settled before lock. Weaker surrogates, post-commit/manual proof, and invented report paths require an already-settled boundary; otherwise block finalization.
- The gate fails if repository exploration would still need to choose any planning detail on the user's behalf, including a concrete file path or target file, create-versus-edit behavior, single-versus-multi-file output, touched interfaces, validation mode, source precedence, or whether a specialized grounding producer should replace the generic ground stage.
- After the gate passes, initialize the workspace with `scripts/forma-workflow.sh init <issue-id>` before creating or editing `./plans/issue-<id>/plan.md` and `./plans/issue-<id>/tasks.md`.
- Work inside `./plans/issue-<id>/plan.md` and `./plans/issue-<id>/tasks.md`.
- Let `scripts/forma-workflow.sh init <issue-id>` create `./plans/issue-<id>/` and its template files.
- After the gate passes, write only confirmed facts from the plan stage, approved grounding handoffs, source material, and the current user confirmation. Repository exploration from the lock stage is for confirming already-settled facts, not inventing missing scope, approach, validation, or source precedence.
- Fill in `plan.md` before writing or changing `tasks.md`.
- Rewrite `tasks.md` into the final task checklist for the issue, replacing template guidance and example text.
- Run `scripts/forma-workflow.sh check <issue-id>` after finalizing `plan.md` and `tasks.md` and before staging or asking for commit permission. A passing check is required before staging or committing the locked plan.
- Stage only the current issue's finalized `plan.md` and `tasks.md`, then show the staged diff to the user before leaving planning.
- Commit only that staged plan/task snapshot after explicit user permission.
- The planning commit must contain only the current issue's planning files, not implementation changes.
- Keep `plan.md` concise and decision-complete.
- `plan.md` must preserve the execution contract in Scope, Approach, Constraints, Acceptance Criteria, Validation, and task entries instead of leaving concrete paths, target support, artifact state, compatibility policy, mutation boundaries, or non-goals only in chat history.
- For generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans, `plan.md` must preserve the settled Artifact/Evidence Boundary either as its own section or as explicit Scope, Approach, Constraints, Acceptance Criteria, Validation, and task entries.
- For behavior-changing work, capture test expectations in acceptance criteria and validation instead of creating separate "implement" and "then test" tasks unless test work is itself the standalone deliverable.
- For behavior-changing work, each task `Accept:` line must state the concrete success behavior, and each `Validate:` line must prove a primary success path, required failure path, or explicit non-goal.
- A task is not execution-ready if its `Validate:` line could pass while the main promised behavior is absent.
- In `plan.md`, use `## Validation` for shared task-safe checks written as `Check:` / `Command:` blocks.
- In `plan.md`, use `## Final Validation` for fenced `sh` commands that only run when the last task is completed.
- Each `## Final Validation` command line must be self-contained because the workflow runner executes every line as an independent command. Combine multi-step smoke checks into one command line with explicit setup and cleanup.
- Use portable shell variable names such as `exit_status` in copyable cleanup commands.
- Write each new task entry as `- [ ] [<task-id>] ...` or `- [x] [<task-id>] ...`.
- For new tasks, encode task type in the existing schema, preferably at the start of `Accept:` as `Task Type=<type>; ...`; existing tasks without a task type default to `step`.
- Put exactly one `Accept:` line directly below each task.
- Put one or more `Validate:` lines directly below each task.
- Use optional `Use-Check:` lines only for shared check ids defined in `## Validation`.
- Use optional `Depends:` lines for prerequisite task ids; omit them when there are no dependencies, or use a single `Depends: none`. `Depends:` must use bare task ids, not bracketed forms.
- Use `Constraint:` only for execution guardrails such as touched-surface limits, non-goals, or review conditions; for `loop-batch`, include batch limits, selection rules, retry/skip rules, no-full-rerun guards, and write boundaries here.
- Use `Task Type=gate` for decision-critical proof, promotion, compatibility, or evidence gates that must pass before review-ready closure.
- Split tasks only when there is a meaningful execution boundary.
- If the issue is simple, use a single task instead of artificial decomposition.
- Keep each task independently completable and easy to audit.
- Make each task's `Validate:` and `Use-Check:` lines sufficient for task completion without forcing unrelated later tasks to be done.
- When planning the last remaining task, prefer the narrowest task-local proof in that task's `Validate:` lines and reserve `## Final Validation` for issue-level closure checks whenever possible.
