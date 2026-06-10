---
name: "backend-plan-first-finalize-plan"
description: "Materialize an already-settled plan into plan.md and task-level execution contracts without reopening planning decisions."
---

# Backend Plan-First Finalize Plan

Materialize an already-settled plan into plan.md and task-level execution contracts without reopening planning decisions.

## Interaction Semantics

- Use this skill to materialize an already-settled plan into repository planning files and task contracts.
- Do not reopen brainstorming or fill planning gaps during finalization.
- Keep the planning handoff narrow: write the current issue plan files and stop before execution begins.

## Entry Gate

- Use only the current user-agent conversation to decide whether planning can begin.
- Confirm from the current user-agent conversation alone that Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer or confirmed grounding handoff, and any applicable Artifact/Evidence Boundary are decision-complete before loading references or taking any planning action.
- Fail closed. If any unanswered question could still change the deliverable, module scope, implementation shape, artifact/evidence boundary, or acceptance criteria, stop and tell the user what still needs to be clarified.
- Do not infer that the task is documentation-only, analysis-only, or eligible for `# no-programmatic-validation: <reason>` unless the current conversation explicitly settles that no code behavior, code-owned definitions, or runtime logic needs to change.
- Treat Goal as unconverged unless the current conversation explicitly settles the concrete deliverable to produce.
- Treat Scope as unconverged unless the current conversation explicitly settles both what is included and what is excluded.
- Treat Approach as unconverged unless the current conversation explicitly settles the intended deliverable shape, the concrete surfaces to touch, and whether the work adds new assets or edits existing ones.
- Treat Validation as unconverged unless the current conversation explicitly settles the task-local validation contract, any reusable task-safe shared checks, and the issue-level final validation or explicit review-only acceptance standard.
- Treat the execution contract as unconverged if the handoff is missing concrete names, paths, defaults, unsupported cases, artifact state, mutation boundary, compatibility policy, or validation proof.
- Treat any broad phrase such as "support", "generate", "install", "update docs", "make it easy", "targeted version", or "release artifact" as unconverged unless it is expanded into exact behavior and paths.
- If finalization would need to choose a command name, API name, function name, skill id, plugin id, file name, directory name, manifest field, argument, default, unsupported value, error behavior, output path, output layout, install destination, scope, overwrite behavior, mutation boundary, target support matrix, artifact state, compatibility policy, validation proof, or negative proof, the gate has not passed.
- If repository exploration would still need to choose a concrete file path or target file, create-versus-edit behavior, single-versus-multi-file output, touched interface, validation mode, source precedence, or whether a specialized grounding producer should replace generic `ground-plan`, the gate has not passed yet.
- Before the gate passes, do not read planning references, do not explore the repository, do not run `scripts/forma-workflow.sh init <issue-id>`, and do not draft `plan.md` or `tasks.md`.

## Workflow

- If `./plans/issue-<id>/plan.md` or `./plans/issue-<id>/tasks.md` is missing, run `scripts/forma-workflow.sh init <issue-id>` from this installed skill package.
- Resolve bundled workflow scripts and references relative to the current triggered skill package; never switch to same-named resources in sibling skill directories, even if their contents match.
- Fill in `plan.md` for the issue, including explicit `Plan Strategy` for new plans; legacy plans without it default to `step-execution`.
- Finalize `tasks.md` for the issue, encoding each task's accepted surface, validation gates, proof obligations, dependencies, and constraints while preserving the structured task schema.
- Commit only `./plans/issue-<id>/plan.md` and `./plans/issue-<id>/tasks.md` before leaving the planning phase.

## Read After Gate

- `references/planning-rules.md`
- `references/plan-template.md`
- `references/tasks-template.md`
- `references/finalization-decision-gate.md`
- `references/plan-materialization.md`
- `references/task-structure.md`
- `references/backend-rules.md`
- `references/backend-review-checks.md`
- `references/script-resource-adapter.md`

## Requirements

- Treat `finalize-plan` as a plan-finalization skill, not a brainstorming skill.
- When invoking `scripts/forma-workflow.sh` or loading bundled planning references, resolve them relative to the current triggered skill package only; do not switch to same-named resources in sibling skill directories, even if the contents match.
- Treat source references in the planning handoff as confirmed only when their relevant contents are already present in the current session or were loaded through an explicitly injected/profile-owned source adapter.
- Do not assume GitHub, `gh`, network access, or any other source-context tool is a base finalization capability. If the handoff depends on an unavailable source reference and no explicit adapter is present, block finalization and ask the user to provide the authoritative material or update the plan.
- Load and follow `references/finalization-decision-gate.md` for the finalization decision gate.
- Load and follow `references/plan-materialization.md` for plan materialization.
- Load and follow `references/task-structure.md` for task structure.
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
- Record durable profile decisions in plan tasks instead of relying on one-off generation notes.
- Include task-local validation for behavior-changing backend work.
- Require an approved contract or source handoff before finalizing API- or stream-changing backend work.
- When the planning handoff depends on GitHub issue refs, load and follow `references/script-resource-adapter.md`, then run `python3 scripts/github_issue_context.py <issue-url-or-user-text>` before finalization if issue body and key comments are not already confirmed.
- Apply workflow validation gate when it is relevant to the current task: `python -m pytest tests/`
- Apply workflow validation gate when it is relevant to the current task: `go test ./...`

## Output

- Follow `references/output-format.md`.
