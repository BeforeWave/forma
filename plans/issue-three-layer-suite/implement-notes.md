# Implement Notes

## Task 1: skeleton-and-methodology

Outcome:
- Python project skeleton committed: `pyproject.toml`, `.gitignore`, `src/forma/{__init__,cli.py}` with `verify` / `create` subcommand stubs that exit 0 with placeholder messages. `pip install -e .` succeeds and `forma --help` shows both subcommands.
- Canonical methodology source of truth committed under `source/methodology/`: five skill-kind fragments (`shape`, `gauge`, `seal`, `pour`, `flow`) plus four shared references (`decision-gate`, `plan-strategy`, `task-structure`, `output-format`). Layer 1 (next task) hand-derives its bundled references from these; Layer 3 (later task) composes from these.

Decision Notes:
- Virtualenv: chose not to create `.venv` in the repo. Rationale: local development already had an isolated interpreter, and creating a committed `.venv` convention adds maintenance noise without solving a real problem for v1. If issue-3 introduces CI or external contributors, a `.venv` recommendation can be added in docs without code changes. `.forma-workflow/` and `.venv/` are both in `.gitignore` to keep the option open.
- pyproject.toml package discovery uses `where = ["src", "source/skill-creator/scripts"]` exactly as the plan specifies. The `source/skill-creator/scripts/` directory does not exist yet (Layer 1 task will create it); setuptools accepts missing `where` entries as zero packages found, so the install still succeeds at the end of this task and will pick up `forma_verifier` once the next task creates it.
- CLI subcommand stubs intentionally return success with a placeholder message rather than raising `NotImplementedError`. Rationale: the task acceptance contract requires `forma --help` to work, which means the underlying functions must be importable and callable; exiting 0 makes it easier to smoke-test the dispatcher wiring across tasks 2 and 3 without changing call sites.
- `--methodology` option on `forma create` is included in the stub. Rationale: declaring the option now fixes the CLI surface; Layer 3 implementation in task 3 just supplies the actual auto-detect logic and consumption — no rewiring needed.
- Methodology fragment style is terse bulleted rules per the plan default. Each fragment opens with a "Stage" section that names what comes before and after, followed by "Hard rules" as MUST/MUST NOT bullets. This makes both Layer 2 rule-checking (regex against MUST citations) and Layer 3 composition (substitute terminology / inject extras) tractable.
- Methodology fragments reference siblings and shared references by relative file name (`references/output-format.md`, `gauge.md`, etc.). Layer 2's verifier in the next task will validate these references resolve.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None. All thirteen files land within the stated In-scope list; no out-of-scope files added.

Follow-ups:
- Layer 1 (next task) will hand-derive `source/skill-creator/references/*.md` from `source/methodology/references/*.md`. Until Mode-O ships in issue-3, the relationship is hand-maintained rather than programmatically regenerated.
- `forma create --methodology` auto-detect logic (task 3) should locate `source/methodology/` by walking up from `forma.__file__` until it finds a sibling `source/methodology/` directory; document the exact algorithm in task 3's implement notes.

## Task 2: layer-1-and-verifier

Outcome:
- Layer 1 creator bundle now exists at `source/skill-creator/` with `SKILL.md`, four bundled methodology references, the stdlib-only `scripts/verify.py` entrypoint, and the embedded `forma_verifier` package.
- `forma verify <path>` now imports `forma_verifier`, prints the human-readable report, and exits nonzero on verifier errors.
- Verifier coverage now includes structural rules, methodology marker rules, valid/invalid fixtures, and Layer 1 dogfood verification.

Decision Notes:
- Kept Layer 2 organizationally inside `source/skill-creator/scripts/` while also making it importable as `forma_verifier` through the existing two-root setuptools package discovery. This preserves the no-pip agent path and the developer CLI/test path.
- The Layer 1 `SKILL.md` names Mode-S output explicitly and keeps Mode-O out of the task scope. It instructs agents to generate exactly `shape/`, `gauge/`, `seal/`, `pour/`, and `flow/`, keep each skill self-contained, and run `python scripts/verify.py <generated-suite-path>` before success.
- The bundled references are concise hand-derived copies of the canonical methodology references, not generated artifacts. They avoid duplicating every stage fragment in full; the stage-specific musts stay in `SKILL.md` plus verifier rules.
- Tests mutate the valid fixture in temp directories to isolate each rule, while keeping a committed invalid fixture as a review surface for multi-error behavior.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- Task 3 should use `forma_verifier.verify()` directly after emission so generated sample output is proven by the same rules as `forma verify`.

## Task 3: layer-3-creator-and-example

Outcome:
- Layer 3 creator package now exists under `src/forma/creator/` with injection schema validation, methodology composition, suite emission, and provenance manifest generation.
- `forma create --inject examples/injection/sample-org --output examples/generated/sample-org-plan-first` now generates the committed Mode-S suite and verifies it before returning success.
- `examples/injection/sample-org/injection.yaml` covers org name, terminology, validation command overrides, and extra Decision Gate dimensions.
- `tests/test_creator.py` covers sample injection loading, schema rejection for unsupported keys, explicit methodology discovery, valid suite emission, committed-output drift, verifier dogfood, and output-directory safety.

Decision Notes:
- Used `uv run --extra dev ...` for task validation after the user clarified that Forma should use uv for Python dependencies.
- Kept business injection additive rather than rewriting canonical methodology text. Generated skills include local terminology and validation-command sections while preserving commands, file paths, artifact names, and verifier-required methodology markers.
- Manifest provenance records `methodology_source_revision` as the current git short SHA and `generated_at` as the real generation timestamp. `methodology_tree_digest` remains as the exact content fingerprint for review and drift checks.
- The emitter replaces only known Forma output paths (`shape`, `gauge`, `seal`, `pour`, `flow`, `.forma-manifest.json`) and refuses directories with unrelated files.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- If issue-3 adds Mode-O, keep the current additive injection schema strict and add a separate explicit mode/schema branch rather than loosening v1 unknown-key rejection.

## Task 4: docs-refresh

Outcome:
- README now reflects the current three-layer state, documents uv and editable-install entrypoints, shows verify/create/build-creator walkthrough commands, and names generated `forma-creator` install paths for Codex and Claude skill roots.
- STRUCTURE now lists `source/`, `src/forma/`, `examples/`, and `tests/` as present, describes the Layer-2-inside-Layer-1 organization, and maps the creator package/test/example layout.
- The current usable Layer 1 skill is now treated as a meta skill source; `forma build-creator --target codex` generates `codex/forma-creator`, and `--target claude-code` generates `claude-code/forma-creator`.
- Each generated `forma-creator` is single-target. The builder injects `references/agent-target.md`; the Codex creator is constrained to emit Codex-format `shape` / `gauge` / `seal` / `pour` / `flow` skills, and the Claude Code creator is constrained to emit Claude Code-format skills.
- AGENTS was also corrected from bootstrap wording to the current source-workspace model so future agent entry does not contradict the materialized tree.

Decision Notes:
- Included uv-first commands because the user clarified Forma should use uv for Python dependency execution.
- Kept the pip editable install path in README because issue-three-layer-suite acceptance explicitly called for a fresh-clone editable install walkthrough.
- Kept one meta skill source instead of duplicating source trees. Codex-specific creator metadata lives under `interfaces/codex/openai.yaml`; builder output maps it to `agents/openai.yaml` only for Codex and writes target-specific plan-first output rules into each generated creator.
- Updated AGENTS even though the task named README/STRUCTURE, because leaving it as "source tree is empty" would misroute future repo work.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- Added AGENTS cleanup as a docs-only consistency fix.

Follow-ups:
- None.

## Post-Task Sample Profile Additions

Outcome:
- Added `examples/profiles/sample-software/` as a sanitized composable profile stack modeled after a downstream software workflow family.
- The sample preserves the software plan-first behavior shape: Chinese plan collaboration, Impact Profile/Impact Boundary selection, read-only grounding, sealed `plan.md`/`tasks.md`, one-task review-gated implementation, and safe showhand execution.
- Added creator tests that load the new profile, generate a Codex suite, assert the expected stage names/resources/manifest metadata, and verify the generated suite.

Decision Notes:
- Used `software-plan-first-*` stage names instead of preserving a downstream-specific prefix. Rationale: Forma committed examples must stay sanitized and must not promote downstream repository naming into a generic sample.
- Adapted downstream workflow-state wording to Forma's current `plans/issue-<id>/` and bundled `scripts/forma-workflow.sh` model. Rationale: copying a downstream-specific state model directly into the sample would conflict with this issue's generated suite runtime.

Validation:
- `uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py`
- `uv run --extra dev forma create --target codex --profile examples/profiles/sample-software/sample-software-plan-first.yaml --output /tmp/forma-sample-software-codex`
- `uv run --extra dev forma create --target claude-code --profile examples/profiles/sample-software/sample-software-plan-first.yaml --output /tmp/forma-sample-software-claude-code`
- `uv run --extra dev forma verify /tmp/forma-sample-software-codex`
- `uv run --extra dev forma verify /tmp/forma-sample-software-claude-code`
- `uv run --extra dev pytest -p no:cacheprovider tests/`
- `git diff --check`

## Post-Task Documentation Additions

Outcome:
- Added `README.zh-CN.md` as a Chinese project overview and usage guide.
- Linked the Chinese document from `README.md`.
- Added `README.zh-CN.md` to the top-level file map in `STRUCTURE.md`.

Validation:
- `git diff --check README.md README.zh-CN.md STRUCTURE.md`
- `rg -n -e "--inject|\\.plan-first" README.md README.zh-CN.md STRUCTURE.md`

## Post-Task Self-Iteration Profile Additions

Outcome:
- Added `profiles/forma-self/` as a project-owned tracked profile stack for managing Forma's own development iterations.
- Added `forma-self-iteration.yaml` as the top-level profile, producing the canonical `forma-shape`, `forma-gauge`, `forma-seal`, `forma-pour`, and `forma-flow` skill names.
- Added conditional `Iteration Area` routing for docs-only, methodology/verifier, creator/profile, generated-baseline, and cross-layer iterations.
- Added Forma-specific references for layer/artifact boundaries, validation selection, and profile policy.
- Documented the project-owned profile stack in README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md.
- Added creator tests proving the profile resolves, emits Codex and Claude Code suites, records overlay metadata, and passes verification.

Decision Notes:
- Placed the profile under `profiles/forma-self/` instead of `examples/profiles/`. Rationale: this is Forma-owned operational source, not a sanitized public example.
- Did not add committed generated baselines for the self-iteration profile. Rationale: the profile is intended as reusable project source; issue-three-layer-suite's committed drift baselines remain `sample-backend-go`.

Validation:
- `uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py`
- `uv run --extra dev forma create --target codex --profile profiles/forma-self/forma-self-iteration.yaml --output /tmp/forma-iteration-codex`
- `uv run --extra dev forma create --target claude-code --profile profiles/forma-self/forma-self-iteration.yaml --output /tmp/forma-iteration-claude-code`
- `uv run --extra dev forma verify /tmp/forma-iteration-codex`
- `uv run --extra dev forma verify /tmp/forma-iteration-claude-code`
- `uv run --extra dev pytest -p no:cacheprovider tests/`
- `git diff --check README.md README.zh-CN.md STRUCTURE.md AGENTS.md profiles/forma-self tests/test_creator.py`

## Task 5: target-aware-create-builder

Outcome:
- `forma create` is now target-specific and profile-driven: it requires `--target codex|claude-code` plus `--profile <file>`, resolves composable profiles, emits five plan-first skill directories, writes target/provenance metadata, and verifies the output before returning success.
- Codex generated suites include `agents/openai.yaml` in every generated skill; Claude Code generated suites omit Codex-only metadata. Layer 2 verifier target rules now enforce both layouts when `.forma-manifest.json` records a target.
- Forma's committed profile example was corrected to sanitized `examples/profiles/sample-backend/`, with committed drift baselines at `examples/generated/sample-backend-go-plan-first-codex/` and `examples/generated/sample-backend-go-plan-first-claude-code/`.

Decision Notes:
- Options considered for profile examples: commit realistic downstream-specific profiles in Forma, or keep Forma examples sanitized and put real profiles in their owning downstream repositories. Selected sanitized Forma examples plus downstream-owned real profiles. Rationale: Forma is the generic builder; real downstream profiles can contain workflow commands and organization-specific constraints that should be tracked in the owning downstream repo, not in Forma's public/reference examples.
- Implemented the minimal profile resolver in this task even though resolver hardening is also a follow-up task. Rationale: the current task's `--profile` CLI and deterministic target output acceptance cannot work without include resolution, merge order, and provenance recording. The next task can harden edge cases and docs without changing the architecture.
- Kept generated skill bodies and target metadata deterministic from target + methodology + resolved profile. `generated_at` remains the only default time-varying manifest field, with `FORMA_GENERATED_AT` available for reproducible review baselines.

Plan Gaps Found:
- The task ordering split target-aware create before profile resolver hardening, but target-aware create already depends on a working resolver. Handled by implementing the necessary resolver behavior here and leaving remaining hardening/documentation to the next task.

Classifications:
- None.

Deviations From Plan:
- Replaced the earlier downstream-named profile example with sanitized `sample-backend` profiles after the user clarified that real downstream profiles must live under their owning directory/repository.

Follow-ups:
- The docs task must remove stale `--inject` / `sample-org` README and STRUCTURE examples and describe the sanitized Forma example versus downstream real-profile boundary.

## Task 6: profile-resolver-hardening

Outcome:
- Profile resolver hardening tests now cover unknown nested keys, unknown stage keys, include cycles, missing includes, merge order, de-duplication, later-profile overrides, and sample profile sanitization.
- `profiles.py` now states the tracking boundary in code comments: agents may draft profile files, but ad hoc Layer 1 constraints are not tracked unless the user explicitly promotes and reviews them as profile source.

Decision Notes:
- Kept the hardening task focused on tests and source comments because the required resolver behavior had to be implemented during task 5 to make `forma create --profile` functional. This task verifies those semantics rather than moving the architecture again.

Plan Gaps Found:
- None beyond the task-5 ordering gap already recorded.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 7: target-aware-docs-refresh

Outcome:
- README now documents `forma create --target <agent> --profile <file> --output <dir>`, sanitized sample-backend profile generation, both target-specific generated drift baselines, and the two authoring paths.
- STRUCTURE now maps `src/forma/creator/profiles.py`, sanitized profile examples, target-specific generated outputs, and the downstream real-profile boundary.
- AGENTS now tells future agents to keep Forma examples sanitized and put real downstream profiles in their owning repositories.

Decision Notes:
- Updated AGENTS alongside README/STRUCTURE even though the task names README and STRUCTURE. Rationale: AGENTS is the repo entrypoint for future agents; leaving out the real-profile boundary there would make the same downstream-profile mistake likely to recur.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- Added AGENTS wording as an agent-facing consistency fix.

Follow-ups:
- None.
