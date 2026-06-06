# Issue Plan

## Goal

Ship Forma's three architectural layers as a coherent, demonstrable end-to-end loop:

- canonical methodology source under `source/methodology/` consumed by both Layer 1 and Layer 3;
- a self-contained Layer 1 meta skill source at `source/skill-creator/` that ships the Layer 2 verifier organizationally inside its `scripts/`;
- a small creator builder that emits Codex and Claude Code installable `forma-creator` bundles from that single meta source, with each generated creator carrying a fixed target contract for its later five-skill output;
- a Layer 3 target-aware programmatic bundle builder under `src/forma/creator/` exposed via `forma create --target codex|claude-code --profile <file>`;
- one worked sanitized composable profile example (`examples/profiles/sample-backend/`) plus committed target-specific Layer-3 outputs (`examples/generated/sample-backend-go-plan-first-codex/` and `examples/generated/sample-backend-go-plan-first-claude-code/`);
- a developer `forma` CLI with `verify`, `create`, and `build-creator` subcommands installed by `pip install -e .`;
- updated `README.md` and `STRUCTURE.md` reflecting the new state.

End state: a fresh clone can `pip install -e .`, run `forma create --target codex --profile examples/profiles/sample-backend/sample-backend-go.yaml --output /tmp/demo-suite-codex`, then `forma verify /tmp/demo-suite-codex`, and the result passes as a Codex-ready plan-first skill bundle. The same command with `--target claude-code` emits and verifies a Claude Code-ready plan-first skill bundle. `forma verify` also passes against `source/skill-creator/` (Layer 1 dogfood) and against both committed target outputs (`examples/generated/sample-backend-go-plan-first-codex/` and `examples/generated/sample-backend-go-plan-first-claude-code/`). `forma build-creator --source source/skill-creator --output /tmp/forma-creator-dist --target codex` emits `/tmp/forma-creator-dist/codex/forma-creator/`; the same command with `--target claude-code` emits `/tmp/forma-creator-dist/claude-code/forma-creator/`. Each emitted creator is single-target and includes `references/agent-target.md`.

Layer 3 output mode for v1: **Mode-S (Solo / vertical)** — target-specific, ready-to-install suite of five skill directories (`shape/`, `gauge/`, `seal/`, `pour/`, `flow/`) plus `.forma-manifest.json`. Codex target output MUST include Codex UI metadata (`agents/openai.yaml`) inside every generated skill. Claude Code target output MUST NOT emit Codex-only metadata. Suits solo developers and single-stack vertical teams who copy the output into the selected agent's skill root and use it immediately. **Mode-O (Org / multi-stack layered meta-skill team kit)** — structurally isomorphic to Forma's own source tree, suited to multi-stack organizations — is deferred to issue-3 (see Out of scope).

Layer operating model:

- **Layer 1 installed creator path**: `forma-creator` is installed into a single agent target (Codex or Claude Code). The agent may accept user-provided ad hoc special constraints during that interaction, inject those constraints into a plan-first five-skill bundle, run the bundled Layer 2 verifier, and only then install or hand off the generated bundle for installation into that same agent's skill root. These ad hoc constraints are embedded into the generated bundle but are not tracked by Forma after the interaction unless the user explicitly promotes them into a Layer 3 profile.
- **Layer 3 tracked profile path**: `forma create --target ... --profile ...` is the deterministic builder path. A profile can include other profiles, and the resolved profile stack is the source of truth. Changing a tracked profile changes the generated target bundle in a reviewable, repeatable way. Agents may help author or revise profile files, but profile changes must be human-reviewed and committed before they become durable source truth.

## Plan Strategy

- Plan Strategy: step-execution

## Scope

In scope:

- `pyproject.toml` at the repository root with two-package discovery (`src/forma` and `source/skill-creator/scripts/forma_verifier`), the `forma` console-script entry point, and the three deps `click`, `pyyaml`, `pytest`.
- `.gitignore` covering `__pycache__/`, `.pytest_cache/`, `*.egg-info/`, `build/`, `dist/`, `.venv/`.
- Canonical methodology source: `source/methodology/{shape,gauge,seal,pour,flow}.md` and `source/methodology/references/{decision-gate,plan-strategy,task-structure,output-format}.md`. The five skill kinds correspond to the plan-first workflow stages: `shape` (chat convergence), `gauge` (read-only repository grounding), `seal` (lock plan into `plan.md` + `tasks.md`), `pour` (execute one task with review gate), `flow` (autopilot all tasks).
- Layer 1 meta skill source (self-contained, stdlib-only after adaptation): `source/skill-creator/SKILL.md`, `source/skill-creator/interfaces/codex/openai.yaml`, `source/skill-creator/references/*.md` (hand-derived from methodology), `source/skill-creator/scripts/verify.py`, `source/skill-creator/scripts/forma_verifier/{__init__,rules,runner,report}.py`.
- Layer 3 creator package: `src/forma/{__init__,cli}.py`, `src/forma/creator/{__init__,manifest,profiles,composer,emitter}.py`, and `src/forma/adapters/skill.py`; `forma create` must require `--target codex|claude-code` and `--profile <file>`.
- Tests: `tests/test_verifier.py`, `tests/test_creator.py`, `tests/test_layer_1_dogfood.py`, `tests/test_creator_builder.py`, plus `tests/fixtures/valid-suite/` and `tests/fixtures/invalid-suite/`; creator tests must cover both target outputs and target-layout failures.
- Example sanitized composable profile stack: `examples/profiles/sample-backend/{base,dev,backend,languages/go,languages/py,sample-backend-go,sample-backend-py}.yaml`, using the v1 bundle-profile schema and containing no downstream organization-specific workflow commands, paths, credentials, or business rules.
- Committed Layer-3 generated outputs: `examples/generated/sample-backend-go-plan-first-codex/` and `examples/generated/sample-backend-go-plan-first-claude-code/` (each including `.forma-manifest.json`).
- Documentation updates: `README.md` (replace bootstrap status with install/verify/create/build walkthrough; note Layer 2 ships inside the Layer 1 meta source) and `STRUCTURE.md` (planned → present; add Layer-2-inside-Layer-1 plus builder organizational notes).

Out of scope:

- **Mode-O (layered meta-skill team kit) — deferred to issue-3**. Layer 3 v1 emits Mode-S only. Mode-O work will introduce: `--mode layered` flag (or equivalent profile field); an org-level profile schema (teams, stacks, language matrix); an emitter branch that produces a Forma-isomorphic source tree (`source/methodology/` + `source/skill-creator/` with `scripts/forma_verifier/` inside + `pyproject.toml`); a Mode-O example (`examples/profiles/sample-org-multi-stack/` + corresponding `examples/generated/`); a self-hosting check that running Mode-O against Forma's own methodology with the appropriate org profile regenerates a `source/skill-creator/` structurally identical to the hand-authored one.
- Runtime multi-target selection from an installed creator; each generated `forma-creator` is single-target.
- Target-neutral installable output from `forma create`; `--target` is required and every generated plan-first bundle must be target-specific.
- Additional agent targets beyond `codex` and `claude-code`.
- Additional methodology language overlays.
- LLM-judge / semantic verification in Layer 2 (v1 is structural + methodology-rule only).
- CI workflow files.
- Pre-commit hooks.
- `forma init` scaffolding for new profile stacks.
- Renaming the artifact filenames the generated suite's `seal` / `pour` skills write — confirmed: `plans/issue-<id>/plan.md`, `plans/issue-<id>/tasks.md`, `plans/issue-<id>/runs/`, `plans/issue-<id>/implement-notes.md` stay as-is. Forma-themed naming applies at the skill-kind layer only (shape/gauge/seal/pour/flow), not at the on-disk artifact-name layer.

## Approach

- Python 3.10+. `pyproject.toml` at the repository root with `tool.setuptools.packages.find` set to `where = ["src", "source/skill-creator/scripts"]` so both `forma` and `forma_verifier` install from a single `pip install -e .`. Deps: `click`, `pyyaml`, `pytest` (dev).
- Layer 2 is implemented inside Layer 1's meta source at `source/skill-creator/scripts/forma_verifier/` and uses stdlib only — so any adapted `forma-creator` bundle has enough code for an agent to verify the suites it generates, without any `pip install`. The same package is also picked up by `pip install -e .` for the developer `forma verify` CLI and the tests.
- Layer 1 entry: `source/skill-creator/SKILL.md` with strict Codex-compatible frontmatter (`name: forma-creator`, `description` only), progressive-disclosure load pointers into `references/`, and an instruction that the agent must invoke `scripts/verify.py <path>` on the suite it scaffolds before reporting success. Codex UI metadata lives at `source/skill-creator/interfaces/codex/openai.yaml`; `forma build-creator --target codex` maps it to `agents/openai.yaml` only in Codex creator output, and every `build-creator` target injects `references/agent-target.md` into the generated creator bundle. The installed creator's interactive contract allows one-off user constraints for the requested generated bundle, but requires the agent to keep those constraints local to that generated bundle, run Layer 2 verification before install/handoff, and avoid implying that those one-off constraints are tracked source.
- Layer 2 rules — structural: frontmatter validity + required keys, kebab-case `name` matching parent directory, required sections present, every referenced `references/*.md` resolves, no cross-skill borrowing. Methodology (apply when a suite is identified as plan-first): `shape` MUST cite the Decision Gate dimensions (Goal / Scope / Approach / Validation / Plan Strategy) and chat-only output; `gauge` MUST cite read-only repository inspection (no writes, no execution) and producing a grounding handoff for `seal`; `seal` MUST cite `plan.md` / `tasks.md` outputs and `issue-workflow init`; `pour` MUST cite `review-ready` / `complete` workflow steps; `flow` is structural-only in v1 (no extra methodology rule beyond the shared structural set). Target rules (apply when `.forma-manifest.json` records a target): `codex` suites MUST include `agents/openai.yaml` in every generated skill with `interface.display_name`, `interface.short_description`, `interface.default_prompt`, and `policy.allow_implicit_invocation`; `claude-code` suites MUST NOT include Codex-only `agents/openai.yaml` or `interfaces/codex` metadata. Rules are declarative dataclasses in `rules.py`; the runner walks the input path, classifies each `SKILL.md` by directory name or frontmatter metadata, applies relevant rules, and produces a structured report.
- Layer 3 creator: `forma create --target <codex|claude-code> --profile <file> --output <dir>`. Locates `source/methodology/` (via `importlib.resources` after install, or `--methodology <path>` for development). Reads the top-level profile file, recursively resolves its `includes`, detects cycles, rejects missing references, merges profiles in declaration order, and then composes per kind (`shape` / `gauge` / `seal` / `pour` / `flow`). The emitted target-specific Mode-S output is `<output>/<kind>/SKILL.md` + sibling `references/` per kind, plus target-required metadata, plus `<output>/.forma-manifest.json` recording target, top-level profile id/path, resolved profile order, methodology git short SHA, methodology tree digest, resolved profile file hashes, generator version, and real UTC generation timestamp. Generated skill bodies and target metadata are deterministic from target + methodology + resolved profile; `generated_at` is the only intentionally time-varying field unless `FORMA_GENERATED_AT` is set for reproducible review baselines. Mode-O (layered meta-skill team kit) is deferred to issue-3 — the v1 manifest schema and emitter API are designed so the Mode-O extension does not require breaking changes.
- Profile surface (v1 bundle profile, intentionally strict): allowed top-level keys are `profile`, `includes`, `bundle`, `org`, `skills`, `terminology`, `validation_commands`, `decision_gate_extras`, and `constraints`. `profile` contains a stable id and optional description. `includes` references other profile files by relative path or profile id and is resolved before local fields are applied. Merge rules are explicit: scalar review fields use last-wins; lists such as `decision_gate_extras` and `constraints` append in resolved order with deterministic de-duplication; mappings such as `terminology`, `validation_commands`, and `skills.<kind>` deep-merge with later profiles overriding the same key. `bundle` may define a review-facing name/description but MUST NOT override the CLI target or rename required stage directories. `skills.<shape|gauge|seal|pour|flow>.description` may refine trigger descriptions while preserving the stage's methodology contract. `constraints` are emitted into the relevant generated skill bodies as hard local requirements, e.g. backend boundaries, Go validation commands, or Python validation commands. Unknown top-level and unknown nested keys are rejected to prevent users from voiding the methodology or target contract. No arbitrary markdown/template injection is allowed in v1. Agents may assist with authoring or refactoring profile files, but the profile file is the durable review artifact and must be confirmed by the user before it is treated as tracked source.
- Tests use synthetic valid + invalid suite fixtures for verifier-rule coverage; the creator test invokes the pipeline on `examples/profiles/sample-backend/sample-backend-go.yaml`, asserts the resolved profile order and manifest fields, and asserts the output passes `forma verify`; profile tests cover include resolution, merge order, cycle detection, missing include rejection, unknown-key rejection, and that included sample/backend/Go constraints are emitted into the target bundle. The Layer 1 dogfood test runs `forma_verifier` directly against `source/skill-creator/`; the builder test emits and verifies both Codex and Claude Code `forma-creator` bundles and asserts their fixed target contracts.
- Source-of-truth refs: this conversation (2026-06-05) for the three-layer architecture, Layer-2-inside-Layer-1 organizational decision, plan-first methodology dimensions, and profile surface; Forma's existing `README.md`, `STRUCTURE.md`, `AGENTS.md`, and `plans/issue-forma-bootstrap/plan.md` for naming and convention precedence. No external sources.

## Artifact/Evidence Boundary

- Source-of-truth refs: this conversation (2026-06-05) → Forma's own existing root docs and `plans/issue-forma-bootstrap/plan.md` → no external sources.
- Artifact paths:
  - committed source-of-truth: everything under `src/forma/`, `source/methodology/`, `source/skill-creator/`, `tests/`, `examples/profiles/sample-backend/`, `pyproject.toml`, `.gitignore`.
  - committed generated artifacts (review surface + drift baseline): `examples/generated/sample-backend-go-plan-first-codex/` and `examples/generated/sample-backend-go-plan-first-claude-code/`, each including `.forma-manifest.json`.
  - gitignored transient: `__pycache__/`, `.pytest_cache/`, `*.egg-info/`, `build/`, `dist/`, `.venv/`.
- Evidence paths: `plans/issue-three-layer-suite/runs/task-*.md` written under workflow control by `scripts/forma-workflow.sh complete`.
- State policy: validation runs in the standard clean non-login non-interactive Bash shell; pytest requires `pip install -e .` to have succeeded; `forma verify` and `forma create` must not require network or external API keys.
- Validation gates: per-task `Validate:` runs the relevant pytest subset or shared check; the Layer-1 and Layer-3 dogfood checks are issue-level shared checks; final validation runs the full pytest suite plus both dogfood `forma verify` invocations.
- Metadata/provenance: each generated `.forma-manifest.json` must record target, top-level profile, resolved profile order, methodology git short SHA, methodology tree digest, resolved profile file hashes, generator version, and real UTC timestamp.
- Write boundary: Layer 3 only writes under the user-supplied `--output` path; the committed `examples/generated/sample-backend-go-plan-first-codex/` and `examples/generated/sample-backend-go-plan-first-claude-code/` outputs are the formal Layer-3 writes in this issue and must match what running the creator against the committed top-level sample profile and each explicit target produces.
- Tracking boundary: Layer 1 ad hoc constraints are not tracked after the interaction unless explicitly promoted into a profile file. Layer 3 profiles are tracked source; generated target bundles are reviewable artifacts derived from tracked profiles, methodology, and target adapter rules.
- Repository boundary: Forma's own committed profiles are sanitized examples only. Real downstream profiles with true workflow commands or organization-specific constraints must live in the downstream repository that owns those constraints and be tracked there.

## Constraints

- No runtime target switching from an installed creator in this issue.
- No target-neutral `forma create` installable output; `forma create` requires exactly one target.
- No Layer 3 chat-only ad hoc injection; durable Layer 3 customization must be represented as profile files.
- No automatic committing of agent-authored profiles; an agent may draft or update profiles, but the user must confirm before they become tracked source.
- No LLM-judge verification — Layer 2 v1 is structural + methodology-rule only.
- No `forma init` scaffolding; `examples/profiles/sample-backend/` is hand-authored.
- No real downstream organization profile content in Forma examples; keep sample profiles sanitized and free of business-specific workflow commands, private paths, credentials, or organization-only constraints.
- No CI workflow files.
- Dependency footprint stays at `click`, `pyyaml`, `pytest`; reject Pydantic, Jinja, FastAPI, requests, etc.
- `source/skill-creator/` must remain truly self-contained: copying that directory alone (no other repo files, no `pip install`) must give an agent everything it needs. `scripts/forma_verifier/` therefore stays stdlib-only.
- Layer 3 composes its output directly from `source/methodology/` + resolved profiles; it must not depend on Layer 1's hand-authored bundle to exist.
- Forma's own `source/skill-creator/` must pass `forma verify` (Layer 1 dogfood gate).
- The committed `examples/generated/sample-backend-go-plan-first-codex/` and `examples/generated/sample-backend-go-plan-first-claude-code/` must pass `forma verify` (Layer 3 dogfood gate).
- The profile schema rejects unknown top-level and unknown nested keys, include cycles, and missing includes.

## Acceptance Criteria

- `pip install -e .` from the repository root succeeds and installs both `forma` and `forma_verifier`.
- `forma --help` lists `verify`, `create`, and `build-creator` subcommands.
- `forma verify source/skill-creator/` exits 0 with a success report.
- `forma create --target codex --profile examples/profiles/sample-backend/sample-backend-go.yaml --output /tmp/sample-backend-go-suite-codex` succeeds, emits Codex-ready `shape` / `gauge` / `seal` / `pour` / `flow` skills with `agents/openai.yaml`, includes resolved sample/dev/backend/Go constraints in the relevant skill bodies, and `forma verify /tmp/sample-backend-go-suite-codex` exits 0.
- `forma create --target claude-code --profile examples/profiles/sample-backend/sample-backend-go.yaml --output /tmp/sample-backend-go-suite-claude-code` succeeds, emits Claude Code-ready `shape` / `gauge` / `seal` / `pour` / `flow` skills without Codex metadata, includes the same resolved profile constraints, and `forma verify /tmp/sample-backend-go-suite-claude-code` exits 0.
- `forma create` without `--target` or without `--profile` fails closed.
- The generated `forma-creator` target contract documents the interactive Layer 1 path: the installed creator may accept ad hoc user constraints, must embed them into the generated five-skill bundle, must run Layer 2 verification before install/handoff, and must not treat those constraints as tracked source.
- Profile tests prove that a top-level profile's included profiles are expanded into the generated bundle and that changing profile content changes the generated skill content deterministically except for the manifest timestamp.
- `python -m pytest tests/` passes with at minimum: one test per verifier rule, the creator integration test, and the Layer 1 dogfood test.
- `forma verify examples/generated/sample-backend-go-plan-first-codex/` exits 0.
- `forma verify examples/generated/sample-backend-go-plan-first-claude-code/` exits 0.
- `forma build-creator --source source/skill-creator --output /tmp/forma-creator-dist --target codex` and the same command with `--target claude-code` emit verified `codex/forma-creator/` and `claude-code/forma-creator/` outputs with fixed target contracts.
- `README.md` reflects the three layers as present, contains the install/verify/create/build snippet, and notes Layer 2 ships inside the Layer 1 meta source.
- `STRUCTURE.md` lists `source/`, `src/forma/`, `tests/`, `examples/` as present and explicitly records the Layer-2-inside-Layer-1 plus builder organization notes.

## Validation

Check: pytest
Command: uv run --extra dev pytest -p no:cacheprovider tests/
Note: shared by tasks that touch verifier or creator code

Check: verify-self
Command: uv run --extra dev forma verify source/skill-creator/
Note: Layer 1 dogfood gate — Forma's own meta skill source must pass Layer 2's rules

Check: verify-generated-codex
Command: uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-codex/
Note: Layer 3 dogfood gate — committed Codex generated suite must pass verification

Check: verify-generated-claude-code
Command: uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-claude-code/
Note: Layer 3 dogfood gate — committed Claude Code generated suite must pass verification

## Final Validation

```sh
uv run --extra dev pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma create --target codex --profile examples/profiles/sample-backend/sample-backend-go.yaml --output /tmp/sample-backend-go-suite-codex
uv run --extra dev forma create --target claude-code --profile examples/profiles/sample-backend/sample-backend-go.yaml --output /tmp/sample-backend-go-suite-claude-code
uv run --extra dev forma verify /tmp/sample-backend-go-suite-codex
uv run --extra dev forma verify /tmp/sample-backend-go-suite-claude-code
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-claude-code/
uv run --extra dev forma build-creator --source source/skill-creator --output /tmp/forma-creator-dist --target codex
uv run --extra dev forma build-creator --source source/skill-creator --output /tmp/forma-creator-dist --target claude-code
uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator
uv run --extra dev forma verify /tmp/forma-creator-dist/claude-code/forma-creator
```

## Risks / Notes

- Methodology fragment style is bulleted-rules for v1 (closer to a spec; easier for Layer 3 to compose and for Layer 2 to rule-check). Revisit if Layer 1 agent behavior is poor in practice.
- Layer 1 install paths recommended in README are generated from the meta source: `~/.codex/skills/forma-creator/` and `~/.claude/skills/forma-creator/`. The installed creators are target-fixed; the Codex creator emits Codex-shaped plan-first skills and the Claude Code creator emits Claude Code-shaped plan-first skills.
- Self-hosting check (Layer 3 regenerating Layer 1's bundled references from methodology and proving identity with the hand-authored versions) is deferred to a later issue.
- The committed target-specific `examples/generated/sample-backend-go-plan-first-*` outputs become drift baselines: if subsequent issues change methodology, target rules, profile schema, merge rules, or the creator, these committed outputs must be regenerated alongside the code changes.
