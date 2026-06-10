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
