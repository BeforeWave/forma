# Repository Structure

This document maps the current Forma source tree and the role of each area.

## Top level

| Path | Role | Status |
|---|---|---|
| `README.md` | English project entrypoint and documentation index | present |
| `README.zh-CN.md` | Chinese project entrypoint and documentation index | present |
| `AGENTS.md` | Agent-facing repo entrypoint | present |
| `CLAUDE.md` | Claude Code-facing pointer back to `AGENTS.md` | present |
| `STRUCTURE.md` | This file — top-level structure map | present |
| `LICENSE` | Apache-2.0 license text | present |
| `pyproject.toml` | Python package metadata and `forma` console entry point | present |
| `setup.py` | Build hook copying canonical runtime assets into wheel package data | present |
| `MANIFEST.in` | sdist inclusion rules for canonical runtime assets | present |
| `uv.lock` | uv dependency lockfile for local development | present |
| `npm/` | Thin npm launcher package; the Python package remains the canonical implementation | present |
| `plans/issue-<id>/` | Per-issue planning and execution state | present per issue |
| `source/` | Canonical methodology, agent-guide, and creator source | present |
| `src/forma/` | Developer Python package and CLI | present |
| `profiles/` | Project-owned tracked profiles for Forma itself | present |
| `examples/` | Composable profile examples; generated example outputs are built locally when needed | present |
| `docs/` | Human-facing split documentation linked from the README files | present |
| `dist/` | Committed release artifacts for profile-backed skill bundles, OpenCode skill output, Codex / Claude Code plugins, and deferred creator skills | present |
| `tests/` | Verifier, creator, fixture, and dogfood tests | present |

## Source tree

| Path | Role |
|---|---|
| `source/methodology/` | Canonical plan-first methodology source used to generate stage-specific workflow skills |
| `source/methodology/stages/` | Stage body sources composed into generated `shape` / `gauge` / `seal` / `pour` / `flow` `SKILL.md` files |
| `source/methodology/fragments/` | Source-only reusable methodology fragments expanded inline before generated `SKILL.md` output |
| `source/methodology/resources/` | Stage-local fixed resources copied into generated workflow bundles, including output formats, workflow rules, templates, helpers, and runner scripts |
| `source/methodology/resources/shared/` | Single source for identical fixed resources copied into multiple generated skills |
| `source/agent-guide/` | Agent-facing explain guidance used by the CLI, separate from creator-bundled temporary injection rules |
| `source/agent-guide/references/profile-authoring-principles.md` | Canonical profile authoring and constraint-placement guidance used by `forma explain profile` |
| `source/skill-creator/` | Self-contained `forma-creator` source |
| `source/skill-creator/interfaces/codex/openai.yaml` | Codex UI metadata used when building the Codex creator |
| `source/skill-creator/references/` | Bundled references for creator authoring and verifier guidance |
| `source/skill-creator/references/temporary-injection-generation.md` | Standard for classifying natural-language constraints into temporary injection JSON |
| `source/skill-creator/scripts/verify.py` | Agent-side verification entrypoint; no pip install required |
| `source/skill-creator/scripts/forma_verifier/` | Bundled verifier package copied with creator source |

The bundled verifier lives inside the creator source so an installed creator
skill can verify generated workflow bundles without depending on a separately
installed developer package. The same `forma_verifier` package is also
discovered by `pyproject.toml` for the developer CLI and tests.

`source/skill-creator/` does not keep a second copy of
`source/methodology/`. `forma build creator` injects that methodology tree into
the built creator bundle at `resources/plan-first/methodology/`.

Wheel builds copy `source/agent-guide/`, `source/methodology/`, and
`source/skill-creator/` into `forma.assets` package data. Installed CLI
commands use those packaged assets first and fall back to source-checkout paths
only during editable development.

Generated workflow bundles keep references inside each skill directory. Shared
source resources are copied into each skill that needs them using consistent
destination names such as `references/output-format.md` and
stage-specific `references/planning-rules.md` or
`references/execution-rules.md`.

`source/methodology/stages/*.md` may use `{{ include: fragments/... }}` for
source readability. The composer expands those fragments inline; they are not
generated skill resources.

## Python package

| Path | Role |
|---|---|
| `src/forma/cli.py` | Click CLI exposing `verify`, `build bundle`, `build plugin`, `install`, `build creator`, and `explain` |
| `src/forma/assets/` | Package-data anchor for runtime assets copied into wheels |
| `src/forma/runtime_assets.py` | `importlib.resources` runtime asset resolver with source-checkout fallback |
| `src/forma/explain.py` | Read-only `forma explain ...` guidance renderer assembled from canonical reference files |
| `src/forma/install.py` | Verified local artifact installer for single skills, skill bundles, and Claude Code plugin roots; rejects Codex plugin artifacts with Codex marketplace guidance |
| `src/forma/plugins.py` | Codex and Claude Code plugin artifact builder |
| `src/forma/creator/manifest.py` | Methodology lookup and provenance manifest helpers |
| `src/forma/creator/profiles.py` | Strict composable profile schema, include resolver, and merge rules |
| `src/forma/creator/composer.py` | Methodology + resolved profile composition into Plan-First skill contents |
| `src/forma/adapters/skill.py` | Target-specific `forma-creator` builder with fixed output contracts |
| `src/forma/creator/emitter.py` | Output writer for generated task-level workflow bundles |

## PyPI packages

| Path | Role |
|---|---|
| `pyproject.toml` | Development package metadata and canonical `forma-cli` distribution metadata |
| `packaging/pypi/packages.toml` | Configured PyPI distribution names built from the same Forma source tree |
| `packaging/pypi/README.beforewave-forma.md` | PyPI README for the `beforewave-forma` compatibility package |
| `scripts/build-pypi-package.py` | Builds one configured PyPI distribution from a temporary copy of the source tree |
| `scripts/publish-pypi.sh` | Validates, builds, smokes, twine-checks, and publishes configured PyPI packages |

## npm launcher

| Path | Role |
|---|---|
| `npm/launcher/bin/forma-npm.js` | Shared npm launcher command that points npm users to the Python CLI |
| `packaging/npm/packages.toml` | Configured npm package name built from the shared launcher source |
| `packaging/npm/README.beforewave-forma.md` | npm README for the scoped `@beforewave/forma` launcher package |
| `scripts/build-npm-package.py` | Builds one configured npm package source from the shared launcher |
| `scripts/publish-npm.sh` | Builds, packs, smokes, dry-runs, and publishes configured npm packages |

The npm packages are distribution entrypoints and discovery placeholders. They
do not install Python dependencies automatically, do not expose the `forma`
binary, and are not Node.js implementations of Forma.

## Documentation

| Path | Role |
|---|---|
| `docs/quick-start.md` | English first-run path, install locations, tracked-profile generation, and `forma-creator` generation walkthrough |
| `docs/quick-start.zh-CN.md` | Chinese quick start |
| `docs/concepts.md` | English compiler model, layer boundaries, core terminology, fit, and documentation routing |
| `docs/concepts.zh-CN.md` | Chinese concepts guide |
| `docs/workflow-contract.md` | English explanation of stages, gates, evidence policy, execution boundaries, validation proof, and continuation rules |
| `docs/workflow-contract.zh-CN.md` | Chinese workflow contract guide |
| `docs/skill-bundle.md` | English generated artifact layout, skill directory anatomy, manifest, install targets, and bundle quality guide |
| `docs/skill-bundle.zh-CN.md` | Chinese skill bundle guide |
| `docs/profile-schema.md` | English durable profile source format, examples, constraint placement, resources, validation commands, and common mistakes |
| `docs/profile-schema.zh-CN.md` | Chinese profile schema guide |
| `docs/forma-creator.md` | English agent-side creator path, temporary injection lifecycle, classification, promotion, and verification boundaries |
| `docs/forma-creator.zh-CN.md` | Chinese forma-creator guide |
| `docs/verifier.md` | English verifier checks, non-goals, common failures, manifest/drift relationship, CI usage, and bundled verifier boundary |
| `docs/verifier.zh-CN.md` | Chinese verifier guide |
| `docs/targets.md` | English Codex, Claude Code, and OpenCode target values, install locations, target-specific metadata, and trust guidance |
| `docs/targets.zh-CN.md` | Chinese targets guide |
| `docs/examples.md` | English illustrative end-to-end workflow walkthrough using committed sample sources |
| `docs/examples.zh-CN.md` | Chinese examples guide |
| `docs/usage.md` | English command reference, repository checks, source layout, and installed CLI behavior notes |
| `docs/usage.zh-CN.md` | Chinese usage guide |

## Release artifacts

| Path | Role |
|---|---|
| `dist/skills/codex/forma-creator` | Codex-targeted creator skill; deferred until creator iteration resumes |
| `dist/skills/claude-code/forma-creator` | Claude Code-targeted creator skill; deferred until creator iteration resumes |
| `dist/skills/opencode/forma-creator` | OpenCode-targeted creator skill; deferred until creator iteration resumes |
| `dist/skill-bundles/codex/` | Default Codex Plan-First skill bundle with `forma-plan` through `forma-showhand` |
| `dist/skill-bundles/claude-code/` | Default Claude Code Plan-First skill bundle with `forma-plan` through `forma-showhand` |
| `dist/skill-bundles/opencode/` | Default OpenCode-native Plan-First skill bundle with `forma-plan` through `forma-showhand` |
| `dist/plugins/codex/forma` | Codex plugin artifact exposing the default Plan-First skills |
| `dist/plugins/claude-code/forma` | Claude Code plugin artifact exposing plugin-local default Plan-First skills |

## Profiles

| Path | Role |
|---|---|
| `.forma/` | Project-owned profile stack for generating skills that manage Forma's own development iterations |
| `.forma/profile.yaml` | Top-level self-iteration profile with `Iteration Area` conditional routing |
| `.forma/base.yaml` | Lightweight always-on self-profile constraints; governance docs are stage- or overlay-scoped, not default execution requirements |
| `.forma/iteration-overlays.yaml` | Conditional docs/governance/methodology/verifier/creator/profile/generated/cross-surface execution overlays |
| `.forma/references/` | Forma-specific source-boundary, validation, and profile policy references copied into generated self-iteration bundles |

Project-owned profiles may contain Forma-specific workflow policy. They are
separate from public examples under `examples/profiles/`.
For self-iteration, `shape`, `gauge`, and `seal` may read root governance docs
because they define boundaries and tasks. Routine `pour` / `flow` execution
defaults stay narrow and only load root governance docs through docs-only,
governance, profile, generated-baseline, or cross-surface `Iteration Area`
overlays.

Sample profiles follow the same constraint classification principle: default
constraints stay minimal, planning and execution rules are stage-specific, and
heavy scenario-specific behavior belongs in conditional overlays.

## Examples

| Path | Role |
|---|---|
| `examples/profiles/sample-backend/` | Profile stack showing base/dev/backend/language composition |
| `examples/profiles/sample-software/` | Profile stack showing generic software plan-first behavior, Chinese workflow wording, Impact Profile / Impact Boundary controls, and safe showhand gates |
| `examples/profiles/sample-backend/scripts/` | Profile-declared helper scripts used only by profiles that select them as resources |
| `examples/profiles/sample-backend/references/` | Profile-declared reference resources copied into generated skills when selected |

Real downstream profiles with organization-specific workflow commands, private
paths, credentials, or business rules belong in the downstream repository that
owns those constraints.
Examples are profile source only. Users who want to inspect generated output
should run `forma build bundle` or `forma build plugin` themselves and choose
the output directory.

## Tests

| Path | Role |
|---|---|
| `tests/test_verifier.py` | Structural and methodology-rule coverage for the bundled verifier |
| `tests/test_layer_1_dogfood.py` | Verifies `source/skill-creator/` as a self-contained creator source |
| `tests/test_creator_builder.py` | Codex, Claude Code, and OpenCode creator builder coverage |
| `tests/test_workflow_build.py` | Workflow build integration, profile resolver hardening, generated-output drift, and verifier dogfood |
| `tests/test_docs_links.py` | Lightweight relative Markdown document link check for README, STRUCTURE, and `docs/` |
| `tests/fixtures/valid-bundle/` | Minimal valid plan-first bundle fixture |
| `tests/fixtures/invalid-bundle/` | Minimal invalid bundle fixture with targeted rule failures |

## Planning state per issue

| Path | Role |
|---|---|
| `plans/issue-<id>/plan.md` | Goal, Scope, Approach, Validation, Plan Strategy, Constraints, Acceptance Criteria |
| `plans/issue-<id>/tasks.md` | Structured task checklist (`Accept:` / `Validate:` / optional `Use-Check:` / `Depends:` / `Constraint:`) |
| `plans/issue-<id>/runs/` | Per-task execution evidence |
| `plans/issue-<id>/implement-notes.md` | Execution decision journal (optional, added when decisions matter to later tasks or review) |
