---
name: "forma-ground"
description: "Inspect code, docs, issues, and evidence before deciding."
compatibility: opencode
metadata:
  forma.stage: "gauge"
  forma.target: "opencode"
---

# Forma Ground

Inspect code, docs, issues, and evidence before deciding.

## Interaction Semantics

- Use this skill as a read-only grounding producer between plan intent and final plan files.
- Inspect only the repository context needed to produce known facts, options, gaps, and a handoff for finalization.
- Do not write `plan.md`, do not write `tasks.md`, and do not start implementation.

## Workflow

- Use this skill after the plan stage has settled intent and before the lock stage writes `plan.md` or `tasks.md`.
- Inspect repository context read-only and produce `Source Material`, `Confirmed Facts`, `Inferences`, `Options Considered`, `Validation Surfaces`, `Blocking Gaps`, and a `Recommended Lock Handoff`.
- Keep facts, inferences, and recommendations separate. Every confirmed fact must name the exact source path or ref that supports it; every inference or recommendation is non-authoritative until the user accepts it.
- Leave unresolved choices in `Blocking Gaps`; the lock stage may copy only confirmed facts and user-approved recommendations.

## Load As Needed


## Requirements

- Use this skill only after the requirement intent is settled enough to know what repository facts need grounding.
- Keep the repository work read-only and do not create, edit, or stage files.
- Output relevant paths, viable options, unresolved gaps, validation surfaces, and a concise handoff that the lock stage can cite.
- Each `Confirmed Facts` item must cite the source path or ref it came from and must not include inferred intent, preference, plan decisions, or implementation recommendations.
- Put repository observations that require interpretation under `Inferences` and label them non-authoritative.
- Put possible implementation choices under `Options Considered`; put only the selected recommendation in `Recommended Lock Handoff`; put unresolved decisions in `Blocking Gaps`.
- Include `Source Material` with only the refs actually used, such as the current conversation, a GitHub issue URL, a reviewed solution package, or a prior grounding brief.
- Use the generic ground stage only when no specialized grounding producer owns the domain. For activity solution work, direct activity requirement-to-solution replaces generic grounding; for Go refactor planning, direct Go refactor planning replaces generic grounding.
- Do not treat a plan draft as the authoritative requirement source. Cite the original source material and any reviewed grounding handoff separately.

## Output

- Return the grounding handoff with Source Material, Confirmed Facts, Inferences, Options Considered, Recommended Lock Handoff, Validation Surfaces, and Blocking Gaps.
