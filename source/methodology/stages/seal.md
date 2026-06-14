# Stage Source: seal

This file is the canonical source for the generated stage body. The
renderer composes these sections with target metadata, stage-local
resources, and resolved constraints.

## Description

Materialize an already-settled plan into plan.md and task-level execution contracts without reopening planning decisions.

## Interaction Semantics

- Use this skill to materialize an already-settled plan into repository planning files and task contracts.
- Do not reopen brainstorming or fill planning gaps during finalization.
- Keep the planning handoff narrow: write the current issue plan files and stop before execution begins.

## Entry Gate

{{ include: fragments/seal/entry-gate.md }}

## Workflow

- If `./plans/issue-<id>/plan.md` or `./plans/issue-<id>/tasks.md` is missing, run `scripts/forma-workflow.sh init <issue-id>` from this installed skill package.
- Resolve bundled workflow scripts and references relative to the current triggered skill package; never switch to same-named resources in sibling skill directories, even if their contents match.
- Fill in `plan.md` for the issue, including explicit `Plan Strategy` for new plans; legacy plans without it default to `step-execution`.
- Finalize `tasks.md` for the issue, encoding each task's accepted surface, validation gates, proof obligations, dependencies, and constraints while preserving the structured task schema.
- Run `scripts/forma-workflow.sh check <issue-id>` after finalizing `plan.md` and `tasks.md` and before staging or asking for commit permission; if the check fails, fix the plan/task contract and rerun the check before continuing.
- Stage only the finalized `plan.md` and `tasks.md`, show the staged diff to the user, then commit only that staged snapshot after explicit user permission.

## Adds

- Treat the lock stage as a plan-materialization skill, not a brainstorming skill.
- When invoking `scripts/forma-workflow.sh` or loading bundled planning references, resolve them relative to the current triggered skill package only; do not switch to same-named resources in sibling skill directories, even if the contents match.
- Treat source references in the planning handoff as confirmed only when their relevant contents are already present in the current session or were loaded through an explicitly injected/profile-owned source adapter.
- Do not assume GitHub, `gh`, network access, or any other source-context tool is a base finalization capability. If the handoff depends on an unavailable source reference and no explicit adapter is present, block finalization and ask the user to provide the authoritative material or update the plan.
{{ include: fragments/seal/decision-gate-adds.md }}
{{ include: fragments/seal/plan-materialization-adds.md }}
{{ include: fragments/seal/task-structure-adds.md }}

## Output

- Follow `references/output-format.md`.
- Include `Contract Check:` with the latest `scripts/forma-workflow.sh check <issue-id>` result before asking for commit permission.
