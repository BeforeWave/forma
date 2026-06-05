---
name: "backend-plan-first-plan-issue"
description: "Use only in plan-oriented collaboration to clarify Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer, and any applicable Artifact/Evidence Boundary for backend work without assuming a specific language stack before finalize-plan."
---

# Backend Plan-First Plan Issue

Use only in plan-oriented collaboration to clarify Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer, and any applicable Artifact/Evidence Boundary for backend work without assuming a specific language stack before finalize-plan.

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

## Always Load

- `references/output-format.md`
- `references/plan-issue-rules.md`
- `references/proposal-decision-gate.md`
- `references/grounding-handoff.md`

## Load As Needed

- `references/backend-rules.md`
- `references/backend-review-checks.md`

## Requirements

- Treat `plan-issue` as the convergence step before `finalize-plan`, not as a plan-file-writing skill.
- First determine whether the current collaboration mode is plan-oriented. If the current agent is not in plan mode, stop and tell the user to switch to plan mode before continuing deeper plan shaping.
- Do not claim that you switched modes unless the host environment explicitly confirms it.
- When loading bundled planning references, resolve them relative to the current triggered skill package only; do not borrow same-named resources from sibling skill directories.
- Always load `references/output-format.md` and `references/plan-issue-rules.md` before deciding whether to clarify, block, propose, or hand off.
- If the user provides a GitHub issue URL, run `python3 script/github_issue_context.py <issue-url-or-user-text>` from this skill package before deciding the context is incomplete; this helper loads planning context without repository exploration.
- The GitHub issue helper supports issue URLs like `https://github.com/<owner>/<repo>/issues/<number>`, loads issue body and chronological comments through `gh issue view <url> --json number,title,body,state,labels,assignees,author,createdAt,updatedAt,url,comments`, and rejects PR, repo, commit, or arbitrary links.
- If multiple GitHub issue URLs appear, ask the user to identify the primary issue unless they explicitly confirm all issues belong to the same requirement context; only then rerun the helper with `--allow-multiple`.
- Treat GitHub issue comments as part of the planning context. Later comments may supersede issue body or earlier comments; if they conflict, ask which version is authoritative instead of guessing.
- If `gh` is missing, unauthenticated, or lacks access, recommend the repository's macOS GitHub CLI setup guidance; if the user does not want to configure `gh` now, continue only after they confirm the issue body and key comments are pasted into the current session.
- While the user context is still incomplete, stay in clarification mode. Ask only for the missing planning information needed to converge Goal, Scope, Approach, and the validation model for tasks, shared checks, and final issue closure.
- Before the user confirms that the context is sufficient, do not explore the repository, do not write repo files, do not execute bundled scripts other than `script/github_issue_context.py`, and do not draft `plan.md` or `tasks.md`.
- Do not execute `issue-workflow.sh` from this skill. The GitHub issue context helper is the only bundled script that `plan-issue` may run.
- Load and follow `references/proposal-decision-gate.md` for the proposal decision gate.
- Load and follow `references/grounding-handoff.md` for grounding handoff selection.
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
- Settle whether the request changes public API behavior, service behavior, stream payloads, persistence, or data flow.
- Distinguish API or stream contract-visible changes from internal logic, storage, queue, or computation changes before proposal-ready.
- Settle profile decision-gate dimension before proposal-ready: API or stream impact
- Settle profile decision-gate dimension before proposal-ready: Data migration or persistence impact
- Use profile validation command when it applies: `python -m pytest tests/`
- Use profile validation command when it applies: `go test ./...`

## Output

- Follow `references/output-format.md`.
