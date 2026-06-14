# Implement Notes

## Task 1: inventory-language-boundaries

Outcome:
- Created the current language-boundary inventory for execution. The cleanup is not a blanket word ban; it separates public concepts, schema/API names, source-structure language, execution-facing pollution, historical records, and deferred generated artifacts.

Decision Notes:
- Selected a boundary-based inventory instead of a term-only inventory. Options considered were a narrow `Layer 1/2/3` cleanup, a broad literal grep cleanup, and a source-boundary cleanup. The selected source-boundary cleanup matches the user correction: public/product concepts may exist, but internal maintenance names must not become profile routes, CLI/agent protocol, runtime guidance, or current test expectations.

Plan Gaps Found:
- None beyond the task plan.

Classifications:
- public/product explanation: keep or clarify reader-facing concepts that users operate directly, including `profile`, `workflow output`, `skill bundle`, `plugin`, `target`, `task contract`, `temporary injection`, and stage trigger names such as `plan`, `ground`, `lock`, `execute`, and `showhand`.
- public/product explanation: `docs/concepts.md` and `docs/concepts.zh-CN.md` can explain the product model, but headings such as "Three Layers" / "三层模型" should be renamed or reframed because they collide with old numbered implementation architecture.
- execution-surface pollution: remove old numbered architecture terms from `.forma` profile routes, default prompts, decision-gate fields, self-iteration references, generated self-profile guidance, and current tests. Confirmed residues include `Layer 1`, `Layer 2`, `Layer 3`, `Layer impact`, `Layer Boundaries`, and `Layer 3 profile`.
- execution-surface pollution: replace Forma self-iteration `cross-layer` route semantics with `cross-surface`, meaning coordinated work across multiple Forma work surfaces. Do not define it as old numbered architecture composition.
- execution-surface pollution: replace old product noun `suite` when it means generated workflow output or skill bundle. Confirmed residues include `generated suite`, `temporary generated suites`, and `target suite shape`.
- execution-surface pollution: avoid exposing raw manifest/provenance terms such as `same-origin` / `base_origin` as the primary agent-facing command concept. Keep machine fields in schema/code, but explain agent-facing behavior as Forma provenance matching the current creator baseline or equivalent concrete wording.
- execution-surface pollution: keep `bootstrap` only where it denotes a concrete install or reinstall state. Rewrite broad phrases such as "bootstrap discovery" when plain install-state confirmation, script missing, script incomplete, or reusable reinstall flow is clearer.
- neutral-but-contaminated: `cross-layer` remains valid in generic software examples when it means frontend/backend or multi-component integration validation. It should not be treated as a Forma self-iteration route after this cleanup.
- neutral-but-contaminated: internal stage keys `shape`, `gauge`, `seal`, `pour`, `flow`, `hone`, and `mend` are valid schema/source keys. They should appear in schema, source maps, and profile authoring docs, but reader-facing docs and CLI/agent guidance should prefer public stage/trigger language unless teaching schema.
- neutral-but-contaminated: `conditional_overlays` is a real schema field. Keep it in schema/API docs, profile authoring guidance, source code, and tests. In user-facing routing prose, prefer "route-specific rules" or "selected scenario rules" unless the schema field itself is being taught.
- historical/deferred residue: do not edit historical `plans/**`, run evidence, or older task contracts to rewrite terminology history.
- historical/deferred residue: do not refresh deferred `dist/skills/*/forma-creator` artifacts in this issue. They may continue to contain old terms until a dedicated creator artifact refresh issue.
- historical/deferred residue: active `dist/skill-bundles/*` and `dist/plugins/*` were not identified as current blockers for the known residue patterns, and this issue should not refresh them unless a later explicit task changes the release-surface policy.

Deviations From Plan:
- None.

Follow-ups:
- Later tasks must preserve existing unrelated doctor worktree changes in `docs/usage.md`, `docs/usage.zh-CN.md`, `src/forma/cli.py`, `src/forma/explain.py`, `src/forma/repo_doctor.py`, and `tests/test_cli.py`.

## Task 2: clean-self-profile-source

Outcome:
- Cleaned `.forma` self-profile source and self-profile references so generated self-iteration guidance uses affected-surface and path-level language instead of old numbered architecture terms.

Decision Notes:
- Replaced the polluted Forma self-iteration route `cross-layer` with `cross-surface`. Options considered were keeping `cross-layer` with a new definition, dropping the route, or renaming it. Renaming was selected because the route still represents real coordinated work across multiple Forma work surfaces, but the old name now carries the wrong numbered-architecture meaning.
- Replaced `generated suite` / `temporary generated suites` in self-profile references with workflow-output wording. This keeps the current product term aligned with `build bundle`, `workflow output`, and `skill bundle` language.
- Rewrote self-profile validation and boundary references around concrete surfaces: `source/skill-creator/`, bundled verifier package, profile composer, target adapters, docs/examples, tests, generated output, and release artifacts.

Plan Gaps Found:
- None.

Classifications:
- execution-surface pollution: `.forma` route ids, prompts, decision gates, validation matrix headings, and self-profile references are execution surfaces and must not use old architecture labels.
- neutral-but-contaminated: `cross-surface` now owns Forma self-iteration coordination. Generic software examples may still use ordinary cross-layer integration wording until the docs/examples task classifies them.

Deviations From Plan:
- Updated the direct `.forma` expectations in `tests/test_workflow_build.py` during this task so the required focused test could pass with the cleaned profile source.

Follow-ups:
- Later test cleanup still needs to rename broader dogfood test terminology and add the final terminology gate.
