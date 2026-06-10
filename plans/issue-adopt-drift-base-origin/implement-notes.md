# Implement Notes

## Task 1: base-origin-render-contract

Outcome:
- Added normalized runtime payload hashing and `base_origin` manifest metadata for profile-generated bundles/plugins, creator bundles, and creator-generated bundles/plugins.
- Regenerated the committed sample `examples/generated` baselines because neutral workflow wording and manifest metadata changed generated output.

Decision Notes:
- Profile-generated and creator-generated bundle/plugin `base_origin` records a freshly rendered no-injection baseline from the same bundled methodology and creator script, so injected or profiled output can later compare only against the same-origin skeleton.
- Codex plugin `base_origin` is computed at the plugin root after `.codex-plugin/plugin.json` is written, so plugin metadata is part of the normalized payload.

Plan Gaps Found:
- None

Classifications:
- The `examples/generated` updates are generated baseline updates caused by source behavior changes, not documentation edits.

Deviations From Plan:
- None

Follow-ups:
- `profile adopt` and `drift` should use `src/forma/origin.py` as the shared normalized payload contract.

## Task 2: exact-profile-adopt

Outcome:
- Added `forma profile adopt <artifact-path> --output <dir> [--profile-id <id>] [--replace] [--json]`.
- Adoption writes a self-contained profile package with `profile.yaml`, copied resources, and `adoption-report.json`, then proves exact normalized payload equality by regenerating the source artifact.

Decision Notes:
- Adoption accepts verified workflow bundles or Codex plugins with valid same-origin `base_origin`; artifacts without `base_origin` still fail closed.
- Same-origin proof is based on regenerating the current release's no-injection creator baseline and comparing that normalized digest to `base_origin.base_output_digest`.
- The extractor maps only structure already represented by profile schema: stage names/directories/display metadata, skill descriptions, constraints, validation commands, decision gate extras, resources, and conditional overlay manifest metadata.
- Any residual regenerated payload diff after profile mapping fails the command instead of being inferred heuristically.

Plan Gaps Found:
- None

Classifications:
- `profile adopt` is an exact promotion path from creator output to durable profile source, not a profile draft or semantic extractor.

Deviations From Plan:
- None

Follow-ups:
- `drift` should reuse the same baseline and normalized payload comparison helpers where possible.

## Task 3: drift-cli

Outcome:
- Added `forma drift <artifact-path> [--profile <profile.yaml>] [--creator-source <dir>] [--json]`.
- Added `forma drift --release-surface [--json]` for the fixed Forma `examples/generated` and `dist` generated surface map.

Decision Notes:
- Drift reports `fresh`, `stale`, `invalid`, or `unknown-source` and exits nonzero only for `invalid`; stale is a successful check result so task 3 can validate reporting before task 4 regenerates stale release surfaces.
- `--profile` performs full regeneration and normalized payload equality for workflow bundles and Codex plugins.
- `--creator-source` fully regenerates creator bundles. For injected creator-generated workflow artifacts, it can prove the no-injection base origin is fresh but returns `unknown-source` unless a profile is supplied.
- Single-artifact drift without source never claims full freshness; it reports `unknown-source` plus base-origin freshness when available.

Plan Gaps Found:
- None

Classifications:
- Current `forma drift --release-surface` reports stale `dist` artifacts and fresh `examples/generated` artifacts before task 4 regeneration.

Deviations From Plan:
- None

Follow-ups:
- Task 4 should regenerate `dist` surfaces and then require release-surface drift to report fresh.

## Task 4: regenerate-release-surfaces

Outcome:
- Regenerated the committed `examples/generated` sample bundles and all `dist` creator, skill-bundle, and Codex plugin surfaces from current source/profile inputs.
- `forma drift --release-surface` now reports `fresh` for every known release-surface artifact.

Decision Notes:
- Examples were regenerated even though task 3 already reported them fresh, keeping this gate as the single release-surface refresh checkpoint.
- Dist creator surfaces were regenerated from `source/skill-creator`; dist workflow bundle/plugin surfaces were kept on the generic no-profile, no-injection creator baseline.

Plan Gaps Found:
- None

Classifications:
- All changed `dist` and `examples/generated` files are generated artifacts, not documentation edits.

Deviations From Plan:
- None

Follow-ups:
- None

## Post-Task Correction: base-origin semantics

Outcome:
- Tightened `base_origin` semantics after downstream plugin smoke validation showed the
  profile-generated path was recording the final artifact digest instead of the
  no-injection creator skeleton digest.
- Profile-generated bundles/plugins now record the same release-local no-injection
  creator baseline digest used by creator-generated artifacts.
- `profile adopt` now accepts any verified workflow artifact with valid same-origin
  `base_origin`, not only artifacts carrying `creator_bundle`; artifacts without
  `base_origin` still fail closed.

Decision Notes:
- `base_origin.base_output_digest` is the non-injected skeleton proof. Profile
  metadata such as `profile.top_level_id`, `profile.bundle_name`, and `profile.org_name`
  is used only to improve adopted profile mapping.
- Codex plugin identity still comes from `.codex-plugin/plugin.json`; manifest
  profile metadata is auxiliary and must not override the plugin payload identity.

Validation:
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_creator.py tests/test_creator_builder.py`
- `uv run --extra dev forma drift --release-surface --json`

## Post-Task Correction: downstream creator adoption proof

Outcome:
- Reclassified committed `dist/skill-bundles/*` and `dist/plugins/codex/forma`
  as generic no-profile, no-injection release surfaces. They must be generated
  from the release-local creator baseline, not from this repository's self
  profile.
- Kept self-profile validation as a temporary-output check from
  `profiles/forma-self/forma-self-iteration.yaml`; self-profiled workflow
  output must not be written into the generic `dist` release surface.
- Proved the intended adoption path with a downstream temporary-injection
  workflow: creator output stayed installable without profile metadata,
  `profile adopt` produced a durable profile, profile regeneration produced the
  same normalized runtime payload, and `drift --profile` reported fresh.
- Added regression coverage for both creator-generated skill bundles and
  creator-generated Codex plugins: the artifact manifest has no `profile`, keeps
  `creator_bundle` and `base_origin`, adopts successfully, regenerates from the
  adopted profile, and drifts fresh.

Decision Notes:
- The downstream proof validates the adopt/drift mechanics and provenance model;
  it does not certify the quality of an agent's project-rule summary.
- `profile adopt` must represent disabled or missing workflow stages explicitly
  with `stages.<stage>.enabled: false`. The current profile schema already
  supports this; no schema update was required.
- Conditional overlay adoption must treat manifest route `references` as derived
  verifier/doctor metadata, not as profile route source. Overlay resources with
  `default` are restored to `resources.default` and marked conditional across the
  emitted stages.
- Existing durable profiles may contain richer rules than a summarized
  creator-injection artifact. In that case, stale drift against the summarized
  artifact is expected and means the two sources are not equivalent.

Process Correction:
- The feedback that refined release-surface ownership, self-profile boundaries,
  downstream adoption proof, disabled-stage handling, and conditional-overlay
  mapping was plan feedback. It should have been recorded in this file before or
  alongside the related code changes instead of being left implicit.

Validation:
- Full test suite passed after the corrections.
- Release-surface drift passed after reinstalling the current CLI and checking
  the generic release surface.

## Delivery Revision: integrate after optional hone stage

Outcome:
- Rebasing this issue onto the current mainline brought in the optional `hone`
  stage and Forma self-profile `forma-reconcile` assertions.
- Resolved integration conflicts by preserving optional-stage behavior and
  base-origin semantics together: creator targets still enumerate only
  `DEFAULT_ENABLED_KINDS`, while creator manifests still receive `base_origin`.
- Updated self-profile plugin coverage to assert both `hone -> forma-reconcile`
  emission and creator-baseline `base_origin` metadata.
- Refreshed `dist/skills/codex/forma-creator` and
  `dist/skills/claude-code/forma-creator` after release-surface drift showed
  they were stale against the rebased `hone` methodology source.

Decision Notes:
- The committed release surfaces remain generic no-profile outputs. The
  self-profile `hone` stage is source/profile behavior, not a generic `dist`
  workflow stage. Creator bundles do carry the optional `hone` source so future
  profile-enabled generation can use the current methodology.
- This revision is merge-readiness work for the same issue, not a plan scope
  change.

Validation:
- `uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_creator.py tests/test_creator_builder.py`
- `uv run --extra dev forma verify source/skill-creator/`
- `uv run --extra dev forma verify dist/skills/codex/forma-creator`
- `uv run --extra dev forma verify dist/skills/claude-code/forma-creator`
- `uv run --extra dev forma drift --release-surface`
- `git diff --check`
