---
name: "forma-ground"
description: "Inspect repository facts read-only and produce a grounding handoff before plan files are written."
---

# Gauge

Inspect repository facts read-only and produce a grounding handoff before plan files are written.

## Interaction Semantics

- Use this skill as a read-only grounding producer between plan intent and final plan files.
- Inspect only the repository context needed to produce known facts, options, gaps, and a handoff for finalization.
- Do not write `plan.md`, do not write `tasks.md`, and do not start implementation.

## Workflow

- Use this skill after `plan-issue` has settled intent and before `finalize-plan` writes `plan.md` or `tasks.md`.
- Inspect repository context read-only and produce known facts, options, relevant paths, validation surfaces, unresolved gaps, and a finalization handoff.
- Keep facts, inferences, and recommendations separate so `finalize-plan` can copy only confirmed facts.
- Do not write `plan.md`, do not write `tasks.md`, and do not start implementation.

## Load As Needed


## Requirements

- Use this skill only after the requirement intent is settled enough to know what repository facts need grounding.
- Keep the repository work read-only and do not create, edit, or stage files.
- Output known facts, relevant paths, viable options, unresolved gaps, validation surfaces, and a concise handoff that `finalize-plan` can cite.
- Separate confirmed facts from inference and recommendation; `finalize-plan` may copy only confirmed facts and user-approved recommendations.
- Include `Source Material` with only the refs actually used, such as the current conversation, a GitHub issue URL, a reviewed solution package, or a prior grounding brief.
- Use generic `ground-plan` only when no specialized grounding producer owns the domain. For activity solution work, direct activity requirement-to-solution replaces generic `ground-plan`; for Go refactor planning, direct Go refactor planning replaces generic `ground-plan`.
- Do not treat a plan draft as the authoritative requirement source. Cite the original source material and any reviewed grounding handoff separately.
- Do not write `plan.md`, do not write `tasks.md`, and do not start implementation.

## Output

- Return the grounding handoff with Source Material, Confirmed Facts, Options Considered, Recommended Handoff, Validation Surfaces, and Blocking Gaps.
