# Stage Source: seal

This file is the canonical source for the generated stage body. The
renderer composes these sections with target metadata, stage-local
resources, and resolved constraints.

## Description

Materialize an already-settled plan into plan.md and tasks.md without reopening planning decisions.

## Interaction Semantics

- Use this skill to materialize an already-settled plan into the repository planning files.
- Do not reopen brainstorming or fill planning gaps during finalization.
- Keep the planning handoff narrow: write the current issue plan files and stop before execution begins.

## Entry Gate

{{ include: fragments/seal/entry-gate.md }}

## Workflow

- If `./plans/issue-<id>/plan.md` or `./plans/issue-<id>/tasks.md` is missing, run `scripts/issue-workflow.sh init <issue-id>` from this installed skill package.
- Resolve bundled workflow scripts and references relative to the current triggered skill package; never switch to same-named resources in sibling skill directories, even if their contents match.
- Fill in `plan.md` for the issue, including explicit `Plan Strategy` for new plans; legacy plans without it default to `step-execution`.
- Finalize `tasks.md` for the issue, encoding each new task type in `Accept:` while preserving the structured task schema.
- Commit only `./plans/issue-<id>/plan.md` and `./plans/issue-<id>/tasks.md` before leaving the planning phase.

## Adds

- Treat `finalize-plan` as a plan-finalization skill, not a brainstorming skill.
- When invoking `scripts/issue-workflow.sh` or loading bundled planning references, resolve them relative to the current triggered skill package only; do not switch to same-named resources in sibling skill directories, even if the contents match.
- If the current planning handoff includes a GitHub issue URL but the current session does not already contain confirmed issue body and key comments, run `python3 script/github_issue_context.py <issue-url-or-user-text>` from this skill package before the decision-complete gate.
- The GitHub issue helper supports issue URLs like `https://github.com/<owner>/<repo>/issues/<number>`, loads issue body and chronological comments through `gh issue view <url> --json number,title,body,state,labels,assignees,author,createdAt,updatedAt,url,comments`, and rejects PR, repo, commit, or arbitrary links.
- If multiple GitHub issue URLs appear, ask the user to identify the primary issue unless they explicitly confirm all issues belong to the same requirement context; only then rerun the helper with `--allow-multiple`.
- Treat GitHub issue comments as part of the planning handoff. Later comments may supersede issue body or earlier comments; if they conflict, block finalization and ask which version is authoritative.
- If `gh` is missing, unauthenticated, or lacks access, recommend the repository's macOS GitHub CLI setup guidance; if the user does not want to configure `gh` now, continue only after they confirm the issue body and key comments are pasted into the current session.
{{ include: fragments/seal/decision-gate-adds.md }}
{{ include: fragments/seal/plan-materialization-adds.md }}
{{ include: fragments/seal/task-structure-adds.md }}

## Output

- Follow `references/output-format.md`.
