# Implement Notes

## Task 1: bundle-terminology-contract

Outcome:
- Renamed the Layer 3 creator API, Layer 1 creator script, Layer 2 verifier report/context fields, manifests, tests, and verifier fixtures from suite terminology to bundle terminology.

Decision Notes:
- Existing committed example outputs are byte-compared by `tests/test_creator.py`, so the sample generated Codex and Claude Code bundles were regenerated from the updated creator to keep the committed baseline aligned with the new manifest contract.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 4: plan-lock-sharpness-contract

Outcome:
- Added execution-contract completeness gates to `forma-plan` methodology and fail-closed finalization rules to `forma-lock`, then refreshed committed generated examples that embed those canonical references.

Decision Notes:
- The task's generated-surface validation depends on the default profile from task 2/3; the same canonical methodology changes also affect existing committed sample generated outputs, so those baselines were regenerated to keep drift tests meaningful.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 2: cli-create-plugin-install

Outcome:
- Added default-profile-backed `create-bundle`, Codex-only `create-plugin`, and verified local `install` support for single skills, skill bundles, and Codex plugins.

Decision Notes:
- The task validation invokes `create-bundle` without `--profile`, so the generic no-injection default profile was introduced in this task instead of waiting for `default-workflow-profile`; task 3 can still refine positioning and generated metadata around that tracked profile.
- Install classification checks Codex plugin roots before bundle roots so a plugin with nested `skills/` installs as `.codex/plugins/<plugin-id>` rather than expanding into `.codex/skills`.

Plan Gaps Found:
- The task order placed default profile creation after CLI validation that already required the default profile.

Classifications:
- None.

Deviations From Plan:
- Added `profiles/default/forma-plan-first.yaml` during task 2 to satisfy the current task's validation contract.

Follow-ups:
- Task 3 should review the default profile descriptions and plugin metadata for final product wording.

## Task 3: default-workflow-profile

Outcome:
- Confirmed the default no-injection profile emits `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand`, and tightened Codex plugin metadata coverage.

Decision Notes:
- Because the profile source already had to land in task 2, this task focused on product-facing plugin metadata and tests that bind the plugin id, name, Plan-First positioning, and skill descriptions.

Plan Gaps Found:
- None beyond the task-order gap recorded in task 2.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 5: creator-target-contracts

Outcome:
- Updated installed `forma-creator` behavior so bundle output is explicit, Codex-targeted creators can also emit verified Codex plugin artifacts, and Claude Code-targeted creators reject plugin artifact requests.

Decision Notes:
- Plugin generation was implemented inside the standalone Layer 1 creator script rather than importing Layer 3 plugin helpers, so an installed creator remains usable without a Forma source checkout.
- The generic creator `SKILL.md` no longer contains the Codex plugin command. Codex plugin generation is advertised only through the generated Codex `references/agent-target.md`; Claude Code target references present workflow-bundle output only.
- Generated creator output prints install hints and artifact paths, but does not copy files into user or project install roots.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 6: dist-release-surface

Outcome:
- Made top-level `dist/` committable and generated the release artifact set for Codex/Claude Code creator skills, Codex/Claude Code default workflow bundles, and the Codex plugin.

Decision Notes:
- Generated `dist/skill-bundles/codex` and `dist/skill-bundles/claude-code` only through explicit `forma create-bundle --output ...` commands.
- Generated `dist/plugins/codex/forma` only through `forma create-plugin --target codex --output ...`; the plugin output has `.codex-plugin/plugin.json`, root `.forma-manifest.json`, and nested `skills/`, with no sibling `skill-bundles/` output.
- Verified all five release roots with `forma verify` before handing the task to workflow completion.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 7: docs-agent-discovery

Outcome:
- Updated README quick-try paths, command reference docs, target/install docs, `AGENTS.md`, new `CLAUDE.md`, discovery metadata, and generated creator release artifacts for the bundle/plugin/install surface.

Decision Notes:
- Homepage quick-try copy now gives agent handoff wording for Codex plugin, skill bundle, and creator skill artifacts while keeping `forma install` scoped to verified local paths.
- `AGENTS.md` is target-neutral and names the committed `dist/` release surface; `CLAUDE.md` points Claude Code agents back to `AGENTS.md` and records that Claude Code plugin output is unsupported.
- The `source/skill-creator` description and Codex UI metadata were updated, so `dist/skills/codex/forma-creator` and `dist/skills/claude-code/forma-creator` were regenerated in this task.
- Full validation caught one remaining removed-command test path in `tests/test_runtime_assets.py`; it now uses `create-bundle` with no compatibility alias.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Post-delivery consolidation: public names, creator boundary, and README onboarding

Feedback:
- Post-delivery review found public naming drift, unclear creator stage-key boundaries, and README onboarding copy that mixed quick-start commands with release-artifact installation details.

Outcome:
- Updated installed `forma-creator` defaults and `rename.prefix` behavior so generated public skill ids use plan/ground/lock/execute/showhand names by default.
- Preserved internal methodology/profile/injection stage keys `shape`, `gauge`, `seal`, `pour`, and `flow`; documented that public skill ids are output names, trigger names, or `rename.stages` values, not schema keys.
- Regenerated Codex and Claude Code `forma-creator` dist artifacts and added tests so the public defaults and stage-key boundary stay covered.
- Removed user-facing internal stage-key tables and examples from high-level docs while keeping the schema-key boundary in creator/profile/injection authoring guidance.
- Reworked README quick onboarding around installing the CLI, generating the default Codex Plan-First plugin, installing it, and optionally using `forma-creator` for project-specific workflow habits.
- Moved Claude Code details, explicit verification, install locations, artifact paths, and profile authoring details out of README quick start and into Usage.
- Sharpened README positioning around Forma as a compiler for project-specific Plan-First skills and the generated runtime harness that leaves reviewable `plan.md`, `tasks.md`, and run evidence.
- Included the pending docs cleanup from the working tree before the squash: Quick Start now leads with the default Codex plugin first run, Usage describes one-off creator naming in natural language, and related docs use output/runtime-harness wording consistently.

Boundary:
- Did not rename internal methodology/profile stage keys or `profiles/forma-self/` self-iteration skills.
- Did not change CLI behavior, workflow schema, or generated release artifacts during README/docs follow-up edits.
- Kept verifier recognition compatible with legacy installable names, but public creator and docs no longer list legacy names as the default surface.

Validation:
- `uv run --extra dev pytest -p no:cacheprovider tests/test_creator_builder.py`
- `uv run --extra dev forma verify source/skill-creator/`
- `uv run --extra dev forma verify dist/skills/codex/forma-creator`
- `uv run --extra dev forma verify dist/skills/claude-code/forma-creator`
- `uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_layer_1_dogfood.py tests/test_docs_links.py`
- `uv run --extra dev pytest -p no:cacheprovider`
- `uv run --extra dev python dist/skills/codex/forma-creator/scripts/create.py --output /private/tmp/forma-creator-default-smoke-20260607-1417`
- `uv run --extra dev forma verify /private/tmp/forma-creator-default-smoke-20260607-1417`
- `git diff --check`
