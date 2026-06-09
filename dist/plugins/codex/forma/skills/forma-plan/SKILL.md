---
name: "forma-plan"
description: "Converge a Forma self-iteration plan, including layer impact, profile ownership, generated-output policy, and validation boundaries."
---

# Forma Plan

Converge a Forma self-iteration plan, including layer impact, profile ownership, generated-output policy, and validation boundaries.

## Interaction Semantics

- Use this skill to converge an executable task contract with the user before any repo plan files are written.
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
- Classify the issue as `Plan Strategy: step-execution`, `loop-exploration`, or `hybrid`; for loop-exploration, hybrid, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans, settle concrete artifact paths, evidence paths, validation gates, and proof requirements before proposal-ready.
- After the Decision Gate passes, identify the grounding producer needed before `finalize-plan`; if repository facts are needed, hand off to that producer instead of exploring the repository from `plan-issue`.
- Keep the proposal in chat only. Do not write `plan.md`, do not write `tasks.md`, and do not execute workflow scripts.
- After the user reviews and confirms the proposal, stop and hand off to `finalize-plan` to write `plan.md` and `tasks.md`.

## Always Load

- `references/output-format.md`
- `references/plan-issue-rules.md`
- `references/proposal-decision-gate.md`
- `references/grounding-handoff.md`

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

- Treat `plan-issue` as the convergence step before `finalize-plan`, not as a plan-file-writing skill.
- First determine whether the current collaboration mode is plan-oriented. If the current agent is not in plan mode, stop and tell the user to switch to plan mode before continuing deeper plan shaping.
- Do not claim that you switched modes unless the host environment explicitly confirms it.
- When loading bundled planning references, resolve them relative to the current triggered skill package only; do not borrow same-named resources from sibling skill directories.
- Always load `references/output-format.md` and `references/plan-issue-rules.md` before deciding whether to clarify, block, propose, or hand off.
- Treat user-provided source references as planning context only after their relevant contents are available in the current session or through an explicitly injected/profile-owned source adapter.
- Do not assume GitHub, `gh`, network access, or any other source-context tool is a base plan-first capability. If a generated bundle includes an injected/profile-owned source adapter, follow that adapter's stage-specific reference and script instructions; otherwise ask the user to paste the authoritative source material needed for planning.
- While the user context is still incomplete, stay in clarification mode. Ask only for the missing planning information needed to converge Goal, Scope, Approach, and the validation model for tasks, shared checks, and final issue closure.
- Before the user confirms that the context is sufficient, do not explore the repository, do not write repo files, do not execute bundled scripts other than explicitly injected/profile-owned source adapters, and do not draft `plan.md` or `tasks.md`.
- Do not execute `forma-workflow.sh` from this skill.
- Load and follow `references/proposal-decision-gate.md` for the proposal decision gate.
- Load and follow `references/grounding-handoff.md` for grounding handoff selection.
- Treat this profile stack as Forma-owned project source, not a sanitized public example.
- Keep downstream organization-specific workflow commands, private paths, credentials, and business rules out of Forma examples.
- Preserve unrelated user work in the dirty worktree and keep commits scoped to the current issue.
- Keep changes scoped to the active issue plan and tasks.
- Read README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, and active plans/issue-<id>/ files when converging Forma governance, scope, validation, or boundary decisions.
- For Layer 1 temporary injection work, classify natural-language constraints into minimal default, stage-specific execution, or conditional overlay targets before writing examples or tasks.
- Prefer durable profile changes for repeated behavior and one-off constraints only for temporary generated suites.
- Keep Layer 1, Layer 2, and Layer 3 responsibilities explicit in plans and implementation notes.
- Do not pre-lock future Layer 2 or Layer 3 implementation decisions outside the current issue scope.
- Decide whether the iteration touches Layer 1 creator behavior, Layer 2 verifier rules, Layer 3 profile composition, methodology resources, examples, generated baselines, docs, or tests.
- Decide whether committed generated outputs must be regenerated and reviewed as drift baselines.
- Decide whether the work is profile-only, docs-only, source behavior, generated-output replacement, or cross-layer.
- Settle profile decision-gate dimension before proposal-ready: Layer impact
- Settle profile decision-gate dimension before proposal-ready: Profile ownership
- Settle profile decision-gate dimension before proposal-ready: Generated baseline policy
- Settle profile decision-gate dimension before proposal-ready: Documentation update requirement
- Apply profile validation gate when it is relevant to the current task: `uv run --extra dev python -m pytest -p no:cacheprovider tests/`
- Apply profile validation gate when it is relevant to the current task: `uv run --extra dev forma verify source/skill-creator/`
- Apply profile validation gate when it is relevant to the current task: `git diff --check`
- Settle `Iteration Area` as part of the Decision Gate before proposal-ready when conditional overlays are present.
- If `Iteration Area` is `docs-only`, apply `docs` overlay constraint: Identify affected docs and whether README.zh-CN.md must stay aligned with README.md.
- If `Iteration Area` is `governance`, apply `governance` overlay constraint: Identify which governance surface changes: README.md, README.zh-CN.md, STRUCTURE.md, AGENTS.md, profiles/forma-self, or plan-first workflow policy.
- If `Iteration Area` is `methodology-verifier`, apply `methodology` overlay constraint: State which canonical methodology stage, fragment, or fixed resource changes and how it affects generated skills.
- If `Iteration Area` is `methodology-verifier`, apply `verifier` overlay constraint: Define the rule being added, relaxed, or tightened and the target suite shape it protects.
- If `Iteration Area` is `creator-profile`, apply `creator` overlay constraint: Identify whether the change affects profile loading, composition, target emission, manifest provenance, output replacement, or creator builder behavior.
- If `Iteration Area` is `creator-profile`, apply `profiles` overlay constraint: Decide whether a profile is Forma-owned under profiles/, sanitized example content under examples/profiles/, or downstream-owned outside this repository.
- If `Iteration Area` is `generated-baseline`, apply `generated` overlay constraint: State which committed generated output paths are drift baselines and why they must change.
- If `Iteration Area` is `cross-layer`, apply `methodology` overlay constraint: State which canonical methodology stage, fragment, or fixed resource changes and how it affects generated skills.
- If `Iteration Area` is `cross-layer`, apply `verifier` overlay constraint: Define the rule being added, relaxed, or tightened and the target suite shape it protects.
- If `Iteration Area` is `cross-layer`, apply `creator` overlay constraint: Identify whether the change affects profile loading, composition, target emission, manifest provenance, output replacement, or creator builder behavior.
- If `Iteration Area` is `cross-layer`, apply `profiles` overlay constraint: Decide whether a profile is Forma-owned under profiles/, sanitized example content under examples/profiles/, or downstream-owned outside this repository.
- If `Iteration Area` is `cross-layer`, apply `generated` overlay constraint: State which committed generated output paths are drift baselines and why they must change.
- If `Iteration Area` is `cross-layer`, apply `docs` overlay constraint: Identify affected docs and whether README.zh-CN.md must stay aligned with README.md.

## Output

- Follow `references/output-format.md`.
