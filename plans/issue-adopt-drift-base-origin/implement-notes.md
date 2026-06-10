# Implement Notes

## Task 1: base-origin-render-contract

Outcome:
- Added normalized runtime payload hashing and `base_origin` manifest metadata for profile-generated bundles/plugins, creator bundles, and creator-generated bundles/plugins.
- Regenerated the committed sample `examples/generated` baselines because neutral workflow wording and manifest metadata changed generated output.

Decision Notes:
- Profile-generated bundle/plugin `base_origin` records the normalized digest of the generated profile payload itself; profile output has no separate temporary-injection layer.
- Creator-generated bundle/plugin `base_origin` records a freshly rendered no-injection baseline from the same bundled methodology and creator script, so injected output can later compare only against the same-origin skeleton.
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
- Adoption only accepts creator-generated workflow bundles or Codex plugins with valid `base_origin`; profile-generated artifacts and artifacts without creator provenance fail closed.
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
- Dist creator surfaces were regenerated from `source/skill-creator`; dist workflow bundle/plugin surfaces were regenerated from `profiles/forma-self/forma-self-iteration.yaml`.

Plan Gaps Found:
- None

Classifications:
- All changed `dist` and `examples/generated` files are generated artifacts, not documentation edits.

Deviations From Plan:
- None

Follow-ups:
- None
