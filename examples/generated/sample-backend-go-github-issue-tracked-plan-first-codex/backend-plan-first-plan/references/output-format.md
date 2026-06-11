# Plan-Issue Output Format

Keep user-facing output compact. Prefer 6 to 10 lines and use only sections that add new information.

## Status Types

The plan stage may output only these statuses:

- `blocked`: the skill cannot continue until missing mode, planning, or execution-boundary inputs are clarified.
- `clarifying`: the skill is still collecting missing Goal, Scope, Approach, Validation, Plan Strategy, or applicable Artifact/Evidence Boundary context before a reviewable proposal can be finalized.
- `proposal-ready`: all blocking decisions are resolved and the skill has enough information to present a reviewable plan proposal in chat, but final plan files have not been written.
- `handoff`: the current skill should stop and recommend the lock stage or another workflow.

Do not use `success` for the plan stage. This skill does not write files, so it must not output `Files Changed`, `Validation Commands` as completed work, `Evidence Path`, or a planning success report.

## Default Rules

- Lead with the result, not process narration.
- Omit empty sections.
- Do not repeat the same point across sections.
- Do not restate settled context, repo rules, or workflow explanations.
- Do not include `Risks` unless there is a concrete unresolved risk.
- Do not include `Next Step` unless the user must take an action now.
- Do not claim that `plan.md` or `tasks.md` were written.
- Do not include blocking questions in `proposal-ready`.

## `blocked`

Use this compact shape:

- One sentence stating that the skill cannot continue yet.
- `Missing:` followed by only the unsettled items.
- Up to 3 short clarifying questions.

Do not:

- Re-list settled decisions.
- Explain the workflow at length.
- Repeat the same blocker in multiple phrasings.

## `clarifying`

Use this compact shape:

- One sentence stating that more planning context is still needed.
- `Missing:` followed by only the unsettled items.
- Up to 3 short clarifying questions.

## `proposal-ready`

Required:

- Summary
- Blocking Decisions Resolved
- Proposed Plan
- Artifact/Evidence Boundary, when the plan is `loop-exploration`, `hybrid`, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing work
- Validation Reality
- Next Step

Optional:

- Open Questions, limited to non-blocking notes that cannot change deliverable, scope, implementation shape, contracts, artifact location, validation, or review-only status.
- Risks

Do not:

- Include `Files Changed`; this skill writes no files.
- Include `Validation Commands` as already executed.
- Include Open Questions that could change execution.
- Omit required execution-boundary details for artifact paths, evidence paths, output policy, state or environment assumptions, proof gates, metadata/provenance, or write boundaries.

## `handoff`

Use this compact shape:

- One sentence stating that the current skill should stop.
- `Switch to:` followed by the recommended skill or workflow and a short reason.
