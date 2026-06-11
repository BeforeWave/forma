---
name: ground
description: "Read Forma repository facts and produce grounding for a self-iteration plan."
---

# Forma Ground

Read Forma repository facts and produce grounding for a self-iteration plan.

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

- `references/forma-iteration-boundaries.md`
- `references/forma-validation-matrix.md`
- `references/forma-profile-policy.md`

## Conditional References

Use the recorded `Iteration Area` before loading overlay references.

- If `Iteration Area` is `docs-only`, do not load overlay references.
- If `Iteration Area` is `governance`, do not load overlay references.
- If `Iteration Area` is `methodology-verifier`, do not load overlay references.
- If `Iteration Area` is `creator-profile`, do not load overlay references.
- If `Iteration Area` is `generated-baseline`, do not load overlay references.
- If `Iteration Area` is `cross-layer`, do not load overlay references.

## Requirements

- Use this skill only after the requirement intent is settled enough to know what repository facts need grounding.
- Keep the repository work read-only and do not create, edit, or stage files.
- Output known facts, relevant paths, viable options, unresolved gaps, validation surfaces, and a concise handoff that `finalize-plan` can cite.
- Separate confirmed facts from inference and recommendation; `finalize-plan` may copy only confirmed facts and user-approved recommendations.
- Include `Source Material` with only the refs actually used, such as the current conversation, a GitHub issue URL, a reviewed solution package, or a prior grounding brief.
- Use generic `ground-plan` only when no specialized grounding producer owns the domain. For activity solution work, direct activity requirement-to-solution replaces generic `ground-plan`; for Go refactor planning, direct Go refactor planning replaces generic `ground-plan`.
- Do not treat a plan draft as the authoritative requirement source. Cite the original source material and any reviewed grounding handoff separately.
- Do not write `plan.md`, do not write `tasks.md`, and do not start implementation.
- Treat this profile stack as Forma-owned project source, not a sanitized public example.
- Keep downstream organization-specific workflow commands, private paths, credentials, and business rules out of Forma examples.
- Do not write the invoking developer's home-directory path into tracked source, docs, profiles, plans, tests, examples, or generated release artifacts.
- Preserve unrelated user work in the dirty worktree and keep commits scoped to the current issue.
- Keep changes scoped to the active issue plan and tasks.
- Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, active plan/task files, pyproject.toml, relevant source directories, tests, and examples read-only before finalization.
- Keep Layer 1, Layer 2, and Layer 3 responsibilities explicit in plans and implementation notes.
- Do not pre-lock future Layer 2 or Layer 3 implementation decisions outside the current issue scope.
- Confirm whether profile changes belong under profiles/forma-self, examples/profiles, or a downstream repository.
- Confirm current generated baselines before recommending any delete/add replacement.
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/`
- Apply workflow validation gate when it is relevant to the current task: `uv run --extra dev forma verify source/skill-creator/`
- Apply workflow validation gate when it is relevant to the current task: `git diff --check`
- Carry recorded `Iteration Area` in the grounding handoff when it is available.

## Output

- Return the grounding handoff with Source Material, Confirmed Facts, Options Considered, Recommended Handoff, Validation Surfaces, and Blocking Gaps.
