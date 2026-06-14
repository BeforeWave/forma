# Issue Plan

## Goal

- Clean up Forma's architecture-language boundary so public/product concepts, internal implementation terms, profile routes, runtime guidance, CLI/agent guidance, docs, examples, and current tests are not mixed together in a way that turns implementation maintenance names into user or agent operating protocol.
- The cleanup must cover the known old numbered-layer terminology and the broader non-layer inventory: old `suite` wording, internal stage-key leakage outside schema/authoring contexts, schema-field language such as `conditional_overlays` where plain route language is enough, manifest/provenance names such as `same-origin` / `base_origin` in agent-facing text, and bootstrap wording where it reads like an internal process label instead of concrete install-state handling.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- Iteration Area: cross-surface
- This issue intentionally introduces and uses `cross-surface` as the neutral execution/planning route for coordinated changes across Forma work surfaces. It must not redefine the route through old numbered architecture terms.

## Scope

- In scope:
  - Inventory and classify current language-boundary residues in `.forma/`, `source/`, `src/forma/`, `docs/`, `examples/`, `STRUCTURE.md`, and current tests.
  - Clean Forma self-profile execution source under `.forma/`, including route names, stage prompts, self-management references, validation matrix text, profile policy text, and generated self-iteration guidance.
  - Clean source/runtime guidance under `source/agent-guide/`, `source/skill-creator/`, `source/methodology/` only where current wording exposes internal maintenance names as user or agent protocol.
  - Clean developer/runtime source comments, docstrings, and generated guidance strings under `src/forma/` where they surface old public/internal terminology boundaries.
  - Clean reader-facing docs and examples where old or internal terms are presented as product concepts rather than explained schema or implementation details.
  - Update current tests that assert old wording, route ids, generated guidance, or test names as expected behavior.
  - Add or update a terminology gate that distinguishes allowed schema/API terms from disallowed execution-facing residues.
- Out of scope:
  - Do not resume or implement the `forma doctor` replan in this issue.
  - Do not change creator, verifier, generator, installer, drift, adoption, or doctor behavior except as needed for text/constants/tests that express the language boundary.
  - Do not refresh or commit `dist/skills/*/forma-creator` deferred creator artifacts.
  - Do not refresh `dist/skill-bundles/*` or `dist/plugins/*` unless a later explicit task changes the release-surface policy.
  - Do not edit historical `plans/**`, `runs/**`, or older task evidence to rewrite history.
  - Do not revert or mix in the existing unrelated doctor worktree changes in `docs/usage.md`, `docs/usage.zh-CN.md`, `src/forma/cli.py`, `src/forma/explain.py`, `src/forma/repo_doctor.py`, or `tests/test_cli.py`; if this issue must touch one of those files, preserve the existing doctor edits and keep the diff attributable.

## Approach

- Treat the source of truth for this cleanup as the current conversation plus the read-only grounding inventory gathered before this lock:
  - Old numbered-layer terms are confirmed in `.forma/project.yaml`, `.forma/profile.yaml`, `.forma/base.yaml`, `.forma/iteration-overlays.yaml`, `.forma/references/forma-iteration-boundaries.md`, `.forma/references/forma-validation-matrix.md`, `STRUCTURE.md`, `source/skill-creator/**`, `src/forma/**`, and `tests/test_workflow_build.py` / `tests/test_layer_1_dogfood.py`.
  - `cross-layer` is neutral in some software example contexts but polluted as a Forma execution route; Forma self-iteration should use `cross-surface` or equivalent surface language instead.
  - Non-layer residues include `suite` as old product wording, internal stage keys used as reader-facing explanations outside schema/authoring docs, `conditional_overlays` appearing where route-specific rules would be clearer, `same-origin` / `base_origin` exposed in agent-facing command guidance, and broad `bootstrap` phrasing that may need concrete install-state wording.
- First produce a current inventory inside the implementation work, grouped as:
  - public architecture/product explanation that can remain with clearer reader language;
  - execution-surface pollution to remove from profile routes, runtime guidance, CLI/agent guidance, and current tests;
  - historical records or deferred artifacts to leave untouched;
  - neutral concepts whose current wording is contaminated and must be renamed or redefined.
- Then make scoped source edits:
  - Update `.forma` self-profile source and references first, replacing the polluted execution route with `cross-surface` and rewriting self-profile guidance around concrete surfaces such as `.forma`, methodology source, creator source, verifier package, profile/schema/adapters, docs/examples, tests, generated output policy, and release artifacts.
  - Update `STRUCTURE.md`, docs, examples, and source/runtime guidance so public docs explain product concepts in reader language while implementation details stay in structure/contributor contexts.
  - Update source docstrings/comments and generated guidance strings in `src/forma/` / `source/skill-creator/` only where wording is part of guidance, help, generated artifact text, or current expectations.
  - Update tests to assert the new wording, renamed route, renamed dogfood concepts, and terminology gate.
- Keep code behavior stable: this issue is a language-boundary cleanup with tests and self-profile generation verification, not a feature behavior rewrite.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user conversation and the read-only grounding inventory in this thread take precedence over old installed lock-skill wording and historical plans.
- Committed artifacts: source/docs/tests under the in-scope paths and `plans/issue-architecture-language-boundary-cleanup/{plan.md,tasks.md}` only.
- Transient artifacts: any generated self-profile output must be written only under `/tmp`, `/private/tmp`, or `$TMPDIR` and verified there.
- Deferred artifacts: `dist/skills/*/forma-creator` may still contain old terminology after this issue and must be recorded as deferred known residue, not treated as failure.
- Historical records: `plans/**` and previous run records may contain old terminology and must be excluded from the cleanup gate except for this active plan/task contract.
- Dirty-worktree policy: preserve the existing doctor-related modified files; do not revert them. If task execution touches an already-modified doctor file, inspect and edit around the existing changes.
- Terminology gate policy: the final gate must search in current active source/docs/tests surfaces and exclude historical plans/runs plus deferred creator artifacts, or explicitly report them as allowed deferred residues.

## Constraints

- Keep changes minimal and scoped to language-boundary cleanup.
- Preserve product concepts that are truly public and useful; do not ban every use of `layer`, `stage`, `profile`, `temporary injection`, `workflow output`, `skill bundle`, `plugin`, or `target`.
- Do not mechanically replace words without classifying whether the term is public product language, schema/API language, source-structure language, or execution-facing pollution.
- Do not turn Agent Guide / CLI guidance into implementation architecture docs; agent-facing guidance should say which CLI command to run, how to use the output, and what the output does not prove.
- Do not hide machine-readable schema terms from schema/API documentation, tests, or source code where those are the actual field names.
- Do not add new persistent assets unless they directly support the cleanup gate or repeated validation.

## Acceptance Criteria

- `.forma` no longer emits self-iteration prompts, generated stage guidance, route names, validation references, or decision-gate fields that require agents to reason in old numbered architecture terms or polluted `cross-layer` semantics.
- Current source/runtime guidance no longer tells users or agents to reason through old implementation architecture labels, old product nouns, or raw manifest provenance names when a path-level, command-level, schema-level, or product-level phrase is clearer.
- Reader-facing docs and examples separate public product concepts from implementation structure; internal stage keys and schema field names appear only where the reader is learning schema, authoring profiles, or inspecting structure.
- Current tests no longer assert old terminology or route names as desired behavior, and any renamed test files/functions use path-level or behavior-level names.
- The issue records deferred residue for historical `plans/**` and `dist/skills/*/forma-creator` instead of editing or refreshing them.
- Self-profile output generated from `.forma/profile.yaml` verifies successfully in a transient path.
- Focused tests and final gates pass, including a terminology gate that protects the cleaned surfaces.

## Validation

Check: workflow-build-focused
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_build.py
Note: proves `.forma` profile composition, generated self-iteration guidance, route text, and related expectations.

Check: docs-links
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Note: use after docs, README-linked docs, examples, or STRUCTURE references change.

Check: creator-source-verify
Command: uv run --extra dev forma verify source/skill-creator/
Note: use after `source/skill-creator/` guidance, bundled verifier text, or creator-facing references change.

Check: self-profile-verify
Command: uv run --extra dev forma build bundle --target codex --profile .forma/profile.yaml --output /tmp/forma-architecture-language-boundary-self-profile && uv run --extra dev forma verify /tmp/forma-architecture-language-boundary-self-profile
Note: transient self-profile output only; do not write this output into `dist/`.

Check: diff-check
Command: git diff --check
Note: whitespace and patch hygiene across the active diff.

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_build.py tests/test_docs_links.py
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma build bundle --target codex --profile .forma/profile.yaml --output /tmp/forma-architecture-language-boundary-self-profile && uv run --extra dev forma verify /tmp/forma-architecture-language-boundary-self-profile
python3 -c "import pathlib,re,sys; roots=[pathlib.Path(p) for p in ['.forma','source','src','docs','examples','tests','README.md','README.zh-CN.md','STRUCTURE.md','AGENTS.md']]; patterns=[r'Layer [123]',r'Layer impact',r'Layer Boundaries',r'Layer 3 profile',r'Layer 1 temporary',r'\\bcross-layer\\b',r'generated suite',r'temporary generated suites']; offenders=[]; [offenders.append(f'{path}:{i}:{line.strip()}') for root in roots for path in ([root] if root.is_file() else root.rglob('*')) if path.is_file() and '.git' not in path.parts and path.suffix not in {'.pyc'} for i,line in enumerate(path.read_text(encoding='utf-8',errors='ignore').splitlines(),1) if any(re.search(p,line) for p in patterns)]; print('\\n'.join(offenders)); sys.exit(1 if offenders else 0)"
git diff --check
```

## Risks / Notes

- The installed `$forma:lock` skill and historical generated creator artifacts currently contain old wording; this plan treats the installed skill as evidence of what source must fix, not as a file to edit directly.
- `dist/skills/*/forma-creator` is deferred by policy and may continue to show old terminology until an explicit creator artifact refresh issue.
- `cross-layer` in generic software examples may be valid engineering language when it means frontend/backend or multi-component integration. Execution should classify it before changing it.
