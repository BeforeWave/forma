---
name: "backend-plan-first-finalize-plan"
description: "Materialize an already-settled plan into plan.md and tasks.md without reopening planning decisions."
---

# Backend Plan-First Finalize Plan

Materialize an already-settled plan into plan.md and tasks.md without reopening planning decisions.

## Interaction Semantics

- Use this skill to materialize an already-settled plan into the repository planning files.
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
- If repository exploration would still need to choose a concrete file path or target file, create-versus-edit behavior, single-versus-multi-file output, touched interface, validation mode, source precedence, or whether a specialized grounding producer should replace generic `ground-plan`, the gate has not passed yet.
- Before the gate passes, do not read planning references, do not explore the repository, do not run `scripts/issue-workflow.sh init <issue-id>`, and do not draft `plan.md` or `tasks.md`.

## Workflow

- If `./plans/issue-<id>/plan.md` or `./plans/issue-<id>/tasks.md` is missing, run `scripts/issue-workflow.sh init <issue-id>` from this installed skill package.
- Resolve bundled workflow scripts and references relative to the current triggered skill package; never switch to same-named resources in sibling skill directories, even if their contents match.
- Fill in `plan.md` for the issue, including explicit `Plan Strategy` for new plans; legacy plans without it default to `step-execution`.
- Finalize `tasks.md` for the issue, encoding each new task type in `Accept:` while preserving the structured task schema.
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

## Requirements

- Treat `finalize-plan` as a plan-finalization skill, not a brainstorming skill.
- When invoking `scripts/issue-workflow.sh` or loading bundled planning references, resolve them relative to the current triggered skill package only; do not switch to same-named resources in sibling skill directories, even if the contents match.
- If the current planning handoff includes a GitHub issue URL but the current session does not already contain confirmed issue body and key comments, run `python3 script/github_issue_context.py <issue-url-or-user-text>` from this skill package before the decision-complete gate.
- The GitHub issue helper supports issue URLs like `https://github.com/<owner>/<repo>/issues/<number>`, loads issue body and chronological comments through `gh issue view <url> --json number,title,body,state,labels,assignees,author,createdAt,updatedAt,url,comments`, and rejects PR, repo, commit, or arbitrary links.
- If multiple GitHub issue URLs appear, ask the user to identify the primary issue unless they explicitly confirm all issues belong to the same requirement context; only then rerun the helper with `--allow-multiple`.
- Treat GitHub issue comments as part of the planning handoff. Later comments may supersede issue body or earlier comments; if they conflict, block finalization and ask which version is authoritative.
- If `gh` is missing, unauthenticated, or lacks access, recommend the repository's macOS GitHub CLI setup guidance; if the user does not want to configure `gh` now, continue only after they confirm the issue body and key comments are pasted into the current session.
- Load and follow `references/finalization-decision-gate.md` for the finalization decision gate.
- Load and follow `references/plan-materialization.md` for plan materialization.
- Load and follow `references/task-structure.md` for task structure.
- Keep generated guidance generic and avoid organization-specific paths, credentials, or workflow commands.
- Treat user-provided special constraints as local to the generated bundle unless promoted into a tracked profile.
- Prefer existing repository conventions and native validation commands.
- Keep changes scoped to the accepted task and preserve unrelated user work.
- Keep changes scoped to the backend behavior required by the current issue.
- Prefer fixing the root cause over masking symptoms.
- Preserve backward compatibility unless the plan explicitly allows breaking changes.
- Avoid leaking sensitive data through logs, errors, or debug output.
- Run the project's Go formatter on edited Go files.
- Prefer module-local Go tests when available.
- This sample demonstrates tracked profile composition without organization-specific workflow details.
- Include task-local validation for behavior-changing backend work.
- Require an approved contract or source handoff before finalizing API- or stream-changing backend work.
- Use profile validation command when it applies: `python -m pytest tests/`
- Use profile validation command when it applies: `go test ./...`

## Output

- Follow `references/output-format.md`.
