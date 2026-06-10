# Issue Plan

## Goal

- Add same-origin provenance and exact adoption support so creator-generated no-profile Forma workflow bundles and Codex plugins can be converted into durable tracked profile source, then checked for drift against regenerated output.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- cross-layer

## Scope

In scope:

- Add stable normalized payload digests and `base_origin` manifest metadata for generated workflow artifacts.
- Add `forma profile adopt <artifact-path> --output <dir> [--profile-id <id>] [--replace] [--json]`.
- Add `forma drift <artifact-path> [--profile <profile.yaml>] [--creator-source <dir>] [--json]` and `forma drift --release-surface [--json]`.
- Support exact adoption for creator-generated skill bundles for `codex` and `claude-code`, plus creator-generated Codex plugin artifacts.
- Support drift checks for profile-generated bundles/plugins, creator bundles, and the known Forma release surface.
- Keep profile and creator rendering semantics aligned for shared fields so exact adoption can be proven by regenerated payload equality.
- Update tests and regenerated artifacts required by changed source behavior.

Out of scope:

- README, README.zh-CN, `docs/`, `STRUCTURE.md`, `AGENTS.md`, and similar documentation updates.
- `agents-md`, `profile audit`, `profile draft`, source-map export, or heuristic recovery for artifacts without `base_origin`.
- Partial adoption. If a delta cannot be represented by profile schema, add explicit schema/render support or fail closed.
- Installing generated Codex plugins or changing Codex marketplace behavior.

## Approach

1. Add a shared normalized-output contract used by drift and adopt. The normalized payload tree excludes `.forma-manifest.json` and local adoption reports, but includes `SKILL.md`, target metadata, resources, scripts, files, and Codex `.codex-plugin/plugin.json`.
2. Emit `base_origin` in Layer 1 creator-generated artifacts and Layer 3 generated artifacts where the artifact kind has a known no-injection base. `base_origin.base_output_digest` is the proof that the non-injected base is same-origin.
3. Align creator and profile render wording for shared fields such as constraints and validation gates with neutral workflow wording instead of source-specific `injected` or `profile` wording.
4. Implement exact-only profile adoption by comparing the artifact against its same-origin no-injection base, mapping the rendered delta into a profile, copying added resources into the output profile directory, regenerating from that profile, and requiring payload equality.
5. Implement drift checks by regenerating the requested artifact from its source profile or creator source, comparing normalized payloads, and returning `fresh`, `stale`, `invalid`, or `unknown-source`.
6. Regenerate and verify committed generated artifacts that change because of manifest, rendering, or release-surface behavior.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user conversation, the accepted plan proposal, the `forma-ground` handoff, and current repository facts inspected during grounding. The user's explicit no-docs constraint takes precedence over normal documentation-update guidance for this issue.
- Source paths: source edits are expected under `src/forma/`, `source/skill-creator/scripts/create.py`, `source/skill-creator/scripts/forma_verifier/` only if verifier coverage is required, and `tests/`.
- Committed generated artifacts, if changed: `examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/`, `examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/`, `dist/skills/codex/forma-creator`, `dist/skills/claude-code/forma-creator`, `dist/skill-bundles/codex`, `dist/skill-bundles/claude-code`, and `dist/plugins/codex/forma`.
- Transient artifacts: exact-adoption and drift smoke outputs must be written under pytest `tmp_path` or `/private/tmp/forma-adopt-drift-*`; they are not source of truth and must not be committed.
- Evidence paths: task evidence is recorded under `plans/issue-adopt-drift-base-origin/runs/` by the workflow runner.
- State policy: keep planning files committed before execution; during implementation do not modify README/docs/governance docs for this issue.
- Metadata/provenance: `base_origin` uses schema `forma.base-origin.v1`, target, artifact kind, normalization id `forma.normalized-output.v1`, and `base_output_digest`. Profile provenance in adopted regenerated output is expected to differ from creator provenance.
- Validation gates: task-local focused tests must prove primary success and negative cases; final validation must run full tests, verifier checks, release-surface drift, generated-surface verification, and `git diff --check`.

## Constraints

- Do not modify README, README.zh-CN, `docs/`, `STRUCTURE.md`, `AGENTS.md`, or similar documentation files in this issue.
- Keep Layer 1 creator behavior self-contained and stdlib-only.
- Preserve existing `create-bundle`, `create-plugin`, `build-creator`, `verify`, `doctor`, `install`, and `explain` behavior unless the new provenance/rendering contract intentionally changes generated output.
- Exact adoption means regenerated runtime payload equality plus stable manifest semantic equality; full manifest provenance equality is not required.
- If `base_origin` is missing or mismatched, `profile adopt` must fail closed instead of inferring from structure.
- Claude Code plugin adoption is unsupported because Claude Code plugin generation is unsupported.

## Acceptance Criteria

- Generated workflow artifacts include stable `base_origin.base_output_digest` where same-origin base comparison is meaningful.
- Creator and profile generation use neutral shared rendering wording so the same profile delta can regenerate the creator workflow payload exactly.
- `forma profile adopt` writes a durable profile package and `adoption-report.json`, then proves regenerated payload equality before reporting success.
- `forma drift` reports fresh/stale/invalid/unknown-source for single artifacts and checks the known release surface with `--release-surface`.
- Negative tests cover missing `base_origin`, base digest mismatch, unsupported artifact targets, and residual diff that cannot be represented.
- Affected committed generated artifacts are regenerated and verified.
- No README or documentation files are modified.

## Validation

Check: focused-adopt-drift-tests
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_creator.py tests/test_creator_builder.py
Note: task-safe coverage for CLI, profile creation, creator output, manifest provenance, and generated payload behavior

Check: verify-creator-source
Command: uv run --extra dev forma verify source/skill-creator/
Note: task-safe Layer 1 / Layer 2 verification

Check: diff-check
Command: git diff --check
Note: whitespace and patch sanity

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma drift --release-surface
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
uv run --extra dev forma verify dist/skills/codex/forma-creator
uv run --extra dev forma verify dist/skills/claude-code/forma-creator
uv run --extra dev forma verify dist/skill-bundles/codex
uv run --extra dev forma verify dist/skill-bundles/claude-code
uv run --extra dev forma verify dist/plugins/codex/forma
git diff --check
```

## Risks / Notes

- `base_output_digest` is the product-critical same-origin proof; generator version is only explanatory metadata.
- Drift/adopt should prefer normalized payload equality over full manifest equality so adopted profiles keep honest profile provenance.
- Release-surface drift mappings are Forma-specific and should stay local to this repository's known `dist/` and `examples/generated/` paths.
