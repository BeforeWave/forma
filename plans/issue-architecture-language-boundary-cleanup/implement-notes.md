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

## Task 5: update-current-tests-and-gate

Outcome:
- Updated current tests to assert cleaned guidance wording, renamed the creator dogfood test file and symbols, and verified the final terminology gate across active source/docs/tests surfaces.

Decision Notes:
- Renamed `tests/test_layer_1_dogfood.py` to `tests/test_creator_source_dogfood.py` and replaced file-local `LAYER_1` / `test_layer_1_*` symbols with creator-source terminology.
- Updated CLI tests from bootstrap/same-origin assertions to reusable install path and Forma-provenance assertions.
- Cleaned remaining non-layer guidance residues found while updating tests: source strings now say install-path discovery or Forma provenance instead of broad bootstrap discovery or same-origin wording.
- Kept `base_origin`, `base_origin_status`, and `bootstrap-incomplete` where they are real schema/API/state fields. The cleanup removes inappropriate operating language, not machine-readable compatibility fields.

Plan Gaps Found:
- The task 3 hard regex did not catch every non-layer residue. During test cleanup, additional current source strings in build/adoption/drift/provenance wording were found and cleaned under the same boundary rule.

Classifications:
- execution-surface pollution: current test expectations must not lock old architecture names or polluted operating language back into the CLI/help/runtime output.
- neutral-but-contaminated: schema/status names remain allowed where they are concrete contract fields or compatibility states.
- historical/deferred residue: the final gate scans active roots and explicitly does not scan historical `plans/**` or deferred `dist/skills/*/forma-creator`.

Validations:
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_build.py tests/test_docs_links.py tests/test_cli.py tests/test_creator_source_dogfood.py`
- `python3 -c "import pathlib,re,sys; roots=[pathlib.Path(p) for p in ['.forma','source','src','docs','examples','tests','README.md','README.zh-CN.md','STRUCTURE.md','AGENTS.md']]; patterns=[r'Layer [123]',r'Layer impact',r'Layer Boundaries',r'Layer 3 profile',r'Layer 1 temporary',r'\\bcross-layer\\b',r'generated suite',r'temporary generated suites']; offenders=[]; [offenders.append(f'{path}:{i}:{line.strip()}') for root in roots for path in ([root] if root.is_file() else root.rglob('*')) if path.is_file() and '.git' not in path.parts and path.suffix not in {'.pyc'} for i,line in enumerate(path.read_text(encoding='utf-8',errors='ignore').splitlines(),1) if any(re.search(p,line) for p in patterns)]; print('\\n'.join(offenders)); sys.exit(1 if offenders else 0)"`
- `git diff --check`

Deviations From Plan:
- Added focused `tests/test_cli.py` and `tests/test_creator_source_dogfood.py` validation because this task changed CLI expectations and renamed the dogfood test file.

## Task 4: clean-docs-examples-structure

Outcome:
- Cleaned reader-facing docs, examples, and `STRUCTURE.md` so they explain product/schema/source concepts with public or path-level wording instead of old numbered architecture names or polluted cross-layer route language.

Decision Notes:
- Kept `conditional_overlays` in profile schema and creator docs because it is a real schema field being taught there. Replaced only the example route wording from `cross-layer` to coordinated multi-surface or integration language.
- Reframed `STRUCTURE.md` around concrete source areas: methodology, agent-guide, creator source, bundled verifier, profiles, release artifacts, and tests.
- Rewrote usage docs so install-path setup and diagnostics no longer use broad bootstrap phrasing.
- Left historical `plans/**` and deferred `dist/skills/*/forma-creator` out of scope as required.

Plan Gaps Found:
- None.

Classifications:
- public/product explanation: docs may teach `conditional_overlays`, profiles, workflow output, plugins, and install paths when those are actual user-facing concepts or schema fields.
- execution-surface pollution: docs and structure maps should not ask readers or agents to reason in old numbered architecture names.
- neutral-but-contaminated: full-stack examples can still describe integration across frontend and backend surfaces, but should not use `cross-layer` as a Forma route or profile taxonomy.

Validations:
- `rg -n "Layer [123]|Layer impact|Layer Boundaries|Layer 3 profile|Layer 1 temporary|\\bcross-layer\\b|generated suite|temporary generated suites" README.md README.zh-CN.md docs examples STRUCTURE.md AGENTS.md` returned no matches.
- `rg -n "same-origin|bootstrap discovery|bootstrap state|bootstrapped|bootstrap decision|bootstrap success|approves bootstrap" README.md README.zh-CN.md docs examples STRUCTURE.md AGENTS.md` returned no matches.
- `git diff --check`
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py`

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

## Task 3: clean-runtime-guidance

Outcome:
- Cleaned current source and runtime guidance strings under `source/` and `src/forma/` so creator, agent-guide, CLI, and runtime explanations no longer expose old numbered architecture labels or polluted cross-layer routing language.

Decision Notes:
- Replaced old `Layer 3 profile` wording with `tracked profile` or `reviewed profile` depending on whether the guidance is talking about durable source tracking or human-approved promotion.
- Replaced creator/runtime `cross-layer` route wording with coordinated multi-surface wording. This preserves the concept that some rules affect multiple work surfaces without tying it to old numbered architecture labels.
- Replaced broad agent-facing bootstrap/same-origin wording with reusable install path and Forma provenance wording. Machine fields such as `base_origin` remain unchanged because they are schema/code fields, not user-facing operating language.

Plan Gaps Found:
- None.

Classifications:
- execution-surface pollution: source guidance, creator SKILL text, agent guide profile-authoring guidance, CLI help/docstrings, and runtime guidance are current execution surfaces and must not instruct agents with old numbered architecture names.
- neutral-but-contaminated: `conditional_overlays` remains valid schema/profile terminology where the schema is being taught. The polluted part was the route label and example language bound to `cross-layer`.
- public/product explanation: Forma provenance is acceptable public command guidance when phrased as what the agent can verify or compare, not as a raw internal field name.

Validations:
- `rg -n "Layer [123]|Layer impact|Layer Boundaries|Layer 3 profile|Layer 1 temporary|\\bcross-layer\\b|generated suite|temporary generated suites" source src` returned no matches.
- `rg -n "same-origin|bootstrap discovery|bootstrap state|bootstrapped|bootstrap decision|bootstrap success|approves bootstrap" src/forma/explain.py src/forma/cli.py src/forma/plugin_guidance.py source` returned no matches.
- `git diff --check`
- `uv run --extra dev forma verify source/skill-creator/`

Deviations From Plan:
- None.
