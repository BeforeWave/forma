# Plan-Issue Output Format

Keep user-facing output compact. Prefer 6 to 10 lines and use only sections that add new information.

## Status Types

The plan stage may output only these statuses:

- `blocked`: the skill cannot continue until missing mode, planning, or execution-boundary inputs are clarified.
- `clarifying`: the skill is still collecting missing Goal, Scope, Approach, Validation, Plan Strategy, or applicable Artifact/Evidence Boundary context before a reviewable proposal can be finalized.
- `proposal-ready`: all blocking decisions are resolved and the skill has enough information to present a reviewable plan proposal in chat, but final plan files have not been written.
- `handoff`: the current skill should stop and recommend the lock stage or another workflow.

The plan stage does not use `success`. Its work is chat-only, so it reports
`blocked`, `clarifying`, `proposal-ready`, or `handoff` instead of completed
files, validation runs, evidence paths, or planning success.

## Default Rules

- Lead with the result, not process narration.
- Omit empty sections.
- Put each point in one section only.
- Keep settled context, repo rules, and workflow explanations out of routine output.
- Include `Risks` only for concrete unresolved risks.
- Include `Next Step` only when the user must act now.
- Mention `plan.md` or `tasks.md` only to say that the lock stage will write them later.
- Keep `proposal-ready` free of questions that could block execution.

## `blocked`

Use this compact shape:

- One sentence stating that the skill cannot continue yet.
- `Missing:` followed by only the unsettled items.
- Up to 3 short clarifying questions.
Keep settled decisions and workflow explanations out of `blocked`; state each
blocker once.

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

Keep `proposal-ready` chat-only: no changed-file report, no completed
validation report, no execution-changing open questions, and no missing
execution-boundary details for artifact paths, evidence paths, output policy,
state or environment assumptions, proof gates, metadata/provenance, or write
boundaries.

## `handoff`

Use this compact shape:

- One sentence stating that the current skill should stop.
- `Switch to:` followed by the recommended skill or workflow and a short reason.
