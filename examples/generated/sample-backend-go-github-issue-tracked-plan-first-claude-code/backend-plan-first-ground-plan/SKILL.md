---
name: "backend-plan-first-ground-plan"
description: "Inspect backend repository facts read-only and produce a grounding handoff."
---

# Backend Plan-First Ground Plan

Inspect backend repository facts read-only and produce a grounding handoff.

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
- Inspect source layout, test entrypoints, and dependency files without writing.
- Use profile validation command when it applies: `python -m pytest tests/`
- Use profile validation command when it applies: `go test ./...`

## Output

- Return the grounding handoff with Source Material, Confirmed Facts, Options Considered, Recommended Handoff, Validation Surfaces, and Blocking Gaps.
