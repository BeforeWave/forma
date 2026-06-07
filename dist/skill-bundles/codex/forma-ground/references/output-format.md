# Standard Output Format

Keep user-facing output compact. Prefer 6 to 10 lines and use only sections that add new information.

## Status Types

- `success`: the current planning or execution step finished and the user only needs the result.
- `blocked`: the skill cannot continue until missing planning or execution inputs are clarified.
- `clarifying`: the skill is still collecting missing planning context with the user before a reviewable proposal can be finalized.
- `proposal-ready`: the skill has enough information to present a reviewable plan proposal in chat, but final plan files have not been written yet.
- `handoff`: the current skill should stop and recommend a better workflow or skill.
- `needs-escalation`: the current step needs approval, permissions, or another external prerequisite.

## Default Rules

- Lead with the result, not process narration.
- Omit empty sections.
- Do not repeat the same point across sections.
- Do not restate settled context, repo rules, or workflow explanations.
- Do not include `Risks` unless there is a concrete unresolved risk.
- Do not include `Next Step` unless the user must take an action now.
- Do not include `Review Status` unless waiting for user approval is the key state.
- Do not include `Evidence Path` unless evidence was actually created.
- Do not claim that `plan.md` or `tasks.md` were written unless they were actually written.

## `success` for Planning

Required:

- Summary
- Files Changed
- Validation Commands

Optional:

- Plan Scope
- Plan Commit Status
- Risks

## `success` for Execution

Required:

- Summary
- Files Changed
- Validation Results

Optional:

- Review Status
- Next Step
- Evidence Path
- Risks

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
- Proposed Plan
- Next Step

Optional:

- Open Questions
- Risks

## `handoff`

Use this compact shape:

- One sentence stating that the current skill should stop.
- `Switch to:` followed by the recommended skill or workflow and a short reason.

## `needs-escalation`

Use this compact shape:

- One sentence stating what approval or prerequisite is missing.
- `Needed:` followed by the specific approval, permission, or external input.
