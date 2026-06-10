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
