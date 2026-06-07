# Issue Plan

## Goal

- Rework Forma's public release and install surface around plan-first workflow bundles, Codex plugins, creator skills, and local installation so another agent can quickly install and try the workflow without reading Forma source.

## Plan Strategy

- Plan Strategy: step-execution

## Scope

- In scope:
  - Rename the public `suite` concept to `bundle` across Layer 3 creator APIs, generated manifests, verifier internals, tests, and docs.
  - Replace the current `forma create` command with `forma create-bundle`.
  - Add `forma create-plugin --target codex --output <dir> [--profile <file>]`; `--output` is required and there is no default `dist` destination.
  - Add `forma install --target codex|claude-code --scope user|project <path> [--replace]` for verified local single-skill, skill-bundle, and Codex-plugin installs.
  - Add a generic no-injection plan-first workflow profile that emits `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand`.
  - Strengthen the default `forma-plan` and `forma-lock` workflow contract so planning produces executor-ready task contracts instead of broad direction.
  - Generate and commit release artifacts under `dist/` for creator skills, Codex and Claude Code skill bundles, and the Codex plugin.
  - Update README, docs, AGENTS.md, and a new CLAUDE.md wrapper so both Codex and Claude Code agents understand how to install and use the release artifacts.
- Out of scope:
  - Backward compatibility for `forma create`, `suite` API names, old manifest fields, or old verifier names.
  - Claude Code plugin output; plugin generation is Codex-only in this issue.
  - Network download/install behavior in `forma install`; it installs local paths only.
  - Creator-skill auto-install behavior; generated artifacts remain installed by the user or by a separate agent action.
  - Changing the canonical internal stage keys `shape`, `gauge`, `seal`, `pour`, and `flow` except where profile output names map them to public skill ids.
  - Touching unrelated untracked assets such as `docs/assets/`.

## Approach

- Update Layer 3 naming and contracts in `src/forma/creator/`, `src/forma/adapters/`, CLI command wiring, tests, and any generated manifest provenance:
  - `create_suite` -> `build_bundle`
  - `compose_suite` -> `compose_bundle`
  - `emit_suite` -> `emit_bundle`
  - `ComposedSuite` -> `ComposedBundle`
  - manifest `format: forma-bundle-manifest-v1`
  - manifest `bundle_kind: plan-first-workflow`
- Update Layer 1 and Layer 2 creator/verifier source under `source/skill-creator/`:
  - verifier report/internal names use `plan-first-bundle`, `bundle_path`, and `bundle_kind`.
  - creator-generated artifacts use bundle manifest fields and no suite wording.
  - Codex-targeted `forma-creator` can generate both workflow bundles and Codex plugin output.
  - Claude Code-targeted `forma-creator` can generate workflow bundles but must not advertise plugin output.
- Implement CLI behavior:
  - `create-bundle` emits a target-specific skill bundle to the explicit output path.
  - `create-plugin --target codex` emits one plugin at `<output>/.codex-plugin/plugin.json` plus `<output>/skills/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`.
  - `create-plugin --target claude-code` fails clearly.
  - `install` verifies the local source first, writes to the concrete target/scope install location, and refuses to overwrite unless `--replace` is set.
  - Installation path rules:
    - Codex user skills: `$HOME/.codex/skills/<skill-id>`.
    - Codex project skills: `<cwd>/.codex/skills/<skill-id>`.
    - Codex user plugins: `$HOME/.codex/plugins/<plugin-id>`; the installed plugin root retains `.codex-plugin/plugin.json`.
    - Codex project plugins: `<cwd>/.codex/plugins/<plugin-id>`; the installed plugin root retains `.codex-plugin/plugin.json`.
    - Claude Code user skills: `$HOME/.claude/skills/<skill-id>`.
    - Claude Code project skills: `<cwd>/.claude/skills/<skill-id>`.
    - Claude Code plugin install attempts fail clearly.
    - Skill-bundle installs expand child skill directories into the selected skills directory.
- Add the default profile at `profiles/default/forma-plan-first.yaml` as product-owned source, not under sanitized examples.
- Strengthen the public workflow methodology and generated skill surfaces by editing canonical methodology sources, not only generated output:
  - In `source/methodology/resources/shape/references/plan-issue-rules.md`, add a `## Execution Contract Completeness` section.
  - That section must block `proposal-ready` whenever the executor would still need to decide any exact CLI command, API name, function name, skill id, plugin id, file name, directory name, manifest field, argument, default, unsupported value, error behavior, output path, output layout, install destination, scope, overwrite behavior, mutation boundary, target support matrix, artifact state, compatibility policy, validation proof, or important negative proof.
  - For CLI or API work, require the proposal to name the concrete command or API shape, input flags or parameters, default behavior, output location, unsupported cases, and at least one direct behavior check.
  - For generated artifacts, require the proposal to name each generated path and classify it as committed, transient, ignored, evidence-only, or source-of-truth; if output must not be produced as a side effect, name the forbidden path explicitly.
  - For multi-target work, require a target matrix where each target is classified as supported, unsupported with clear failure, or out of scope.
  - For installation or other filesystem mutation, require the proposal to name the source artifact shape, destination path, user/project scope behavior, overwrite policy, verification-before-write rule, and rollback or partial-write expectation when relevant.
  - For validation, require direct create/install/verify commands or file assertions for the primary success path and the most important negative path when direct behavior can be checked.
  - In `source/methodology/fragments/seal/entry-gate.md`, add fail-closed rules so finalization treats the handoff as unconverged if the execution contract is missing concrete names, paths, defaults, unsupported cases, artifact state, mutation boundary, compatibility policy, or validation proof.
  - In `source/methodology/fragments/seal/entry-gate.md`, treat broad phrases such as "support", "generate", "install", "update docs", "make it easy", "targeted version", and "release artifact" as unconverged unless expanded into exact behavior and paths.
  - In `source/methodology/resources/shared/references/planning-rules.md`, require `plan.md` to preserve the execution contract in Scope, Approach, Constraints, Acceptance Criteria, Validation, and task entries instead of leaving concrete paths, target support, or non-goals only in chat history.
  - In `source/methodology/resources/shared/references/planning-rules.md`, require behavior-changing tasks to state concrete success behavior in `Accept:` and to prove the primary success path, required failure path, or explicit non-goal in `Validate:`.
  - In `source/methodology/resources/shared/references/planning-rules.md`, state that a task is not execution-ready if its `Validate:` line could pass while the main promised behavior is absent.
- Remove the top-level `dist/` ignore rule and generate release outputs:
  - `dist/skills/codex/forma-creator`
  - `dist/skills/claude-code/forma-creator`
  - `dist/skill-bundles/codex/forma-plan`
  - `dist/skill-bundles/codex/forma-ground`
  - `dist/skill-bundles/codex/forma-lock`
  - `dist/skill-bundles/codex/forma-execute`
  - `dist/skill-bundles/codex/forma-showhand`
  - `dist/skill-bundles/claude-code/forma-plan`
  - `dist/skill-bundles/claude-code/forma-ground`
  - `dist/skill-bundles/claude-code/forma-lock`
  - `dist/skill-bundles/claude-code/forma-execute`
  - `dist/skill-bundles/claude-code/forma-showhand`
  - `dist/plugins/codex/forma`
- Update docs and discovery copy:
  - README.md and README.zh-CN.md include quick-try agent wording for Codex plugin, skill bundle, and creator skill paths.
  - Usage and target docs cover `create-bundle`, `create-plugin`, `install`, `build-creator`, and `verify`.
  - AGENTS.md describes the release surface, CLI boundaries, validation, and install semantics for both Codex and Claude Code.
  - CLAUDE.md is a thin Claude Code entrypoint that points back to AGENTS.md.
  - ASO/discoverability copy is tightened in plugin metadata, skill descriptions, `source/skill-creator/interfaces/codex/openai.yaml`, `pyproject.toml`, and docs headings.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user conversation and the `forma-gauge` grounding handoff take precedence; repository files only provide current implementation facts.
- Committed artifact paths:
  - `dist/skills/codex/forma-creator`
  - `dist/skills/claude-code/forma-creator`
  - `dist/skill-bundles/codex/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`
  - `dist/skill-bundles/claude-code/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`
  - `dist/plugins/codex/forma`
- Transient artifact paths:
  - temporary create/install validation outputs under `mktemp -d` paths.
  - additional ad hoc bundle or plugin outputs outside the committed `dist/` release paths are transient unless explicitly promoted by the issue plan.
- Evidence paths: task execution evidence is recorded by Forma workflow scripts under `plans/issue-bundle-plugin-install-surface/runs/`.
- State policy: preserve unrelated dirty/untracked work; the known untracked `docs/assets/` directory is outside this issue unless the user explicitly brings it into scope.
- Validation gates: each behavior change must have targeted pytest coverage or direct create/verify/install command evidence; final validation must run full tests, source creator verification, committed release artifact verification, and whitespace checks.
- Metadata/provenance: generated manifests must expose bundle terminology and target provenance without keeping old suite compatibility aliases.

## Constraints

- Keep Layer 1, Layer 2, and Layer 3 boundaries explicit.
- Do not duplicate canonical methodology from `source/methodology/` into generated source unless existing builder injection already owns that copy.
- Keep `source/skill-creator/scripts/forma_verifier/` stdlib-only.
- Do not make `create-plugin` write `dist/skill-bundles/{codex,claude-code}/*`; those bundle paths are produced only by explicit `create-bundle --output dist/skill-bundles/<target>` commands.
- Do not make `install` fetch remote URLs.
- Do not add compatibility aliases for the old `suite` naming or `forma create` command.

## Acceptance Criteria

- `forma create-bundle` is the supported workflow-bundle command and `forma create` is removed.
- `forma create-plugin --target codex --output <dir>` produces a valid Codex plugin with the five settled public skill ids and no unintended sibling bundle output.
- `forma install` installs verified local single skills, skill bundles, and Codex plugins to the fixed target/scope paths above, with overwrite protection and tested project-scope placement.
- The default no-injection profile can emit `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand` without requiring downstream team constraints.
- `forma-plan` and `forma-lock` generated from the default workflow make plans sharp by forcing concrete surfaces, target matrices, artifact policy, non-goals, and validation before execution can begin.
- `forma-creator` generated for Codex supports workflow-bundle and plugin generation; `forma-creator` generated for Claude Code supports workflow-bundle generation only.
- `dist/` is committable and contains the settled creator, Codex skill-bundle, Claude Code skill-bundle, and Codex plugin release artifacts.
- README, docs, AGENTS.md, and CLAUDE.md explain quick install/try paths for Codex plugin, skill bundle, and creator skill artifacts in agent-friendly language.
- Tests and verifier checks cover the renamed bundle contracts, CLI behavior, generated release artifacts, and docs/link consistency.

## Validation

Check: layer3-creator
Command: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py
Note: use for profile loading, bundle composition/emission, CLI create/build behavior, and creator builder changes.

Check: layer1-layer2
Command: uv run --extra dev pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py
Note: use for creator skill source, verifier rules, and target-layout behavior.

Check: source-creator-verify
Command: uv run --extra dev forma verify source/skill-creator/
Note: use whenever Layer 1 creator source or verifier semantics change.

Check: docs-links
Command: uv run --extra dev pytest -p no:cacheprovider tests/test_docs_links.py
Note: use for README/docs/AGENTS/CLAUDE link and wording changes.

## Final Validation

```sh
uv run --extra dev pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify dist/skills/codex/forma-creator
uv run --extra dev forma verify dist/skills/claude-code/forma-creator
uv run --extra dev forma verify dist/skill-bundles/codex
uv run --extra dev forma verify dist/skill-bundles/claude-code
uv run --extra dev forma verify dist/plugins/codex/forma
git diff --check
```

## Risks / Notes

- The issue intentionally breaks old `suite` and `forma create` names because the user confirmed there are no users yet.
- The committed release artifact set is Codex plugin plus Codex/Claude Code skill bundles plus Codex/Claude Code creator skills; Claude Code plugin output stays out of scope.
