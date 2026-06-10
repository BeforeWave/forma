# Implement Notes

## Task 2: optional-stage-contract

Outcome:
- Added an optional `hone` stage contract to profile loading while preserving five-stage default generation.

Decision Notes:
- Kept `DEFAULT_ENABLED_KINDS` separate from all known `KINDS` so `hone` can be accepted by profile schema without being emitted by default.
- Updated bundle composition to require and load methodology files only for enabled stages, preventing default no-profile generation from depending on optional `hone` source files.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Later tasks must add the actual `hone` methodology source and bundled creator/verifier support before enabling `forma-reconcile` in the self profile.

## Task 3: reconcile-methodology

Outcome:
- Added the `hone` methodology source and `reconcile-rules.md` reference for read-only, stage-aware delivery reconciliation.

Decision Notes:
- Kept `hone` as a normal methodology source only when enabled, while preserving default creator references as exactly the five public stages.
- Filtered disabled optional stage files out of bundle methodology digests so adding `hone` source does not make default five-stage outputs drift.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Bundled creator and verifier still need explicit `hone` support before self-profile generation can emit `forma-reconcile`.

## Task 4: bundled-creator-verifier

Outcome:
- Updated verifier recognition for optional `hone` and `forma-reconcile`, including positive and negative verifier coverage.

Decision Notes:
- Left the standalone creator's default generation at the existing five public stages; `hone` is profile-enabled, not a temporary-injection default.
- Added `hone` to verifier stage recognition and Codex plugin emitted-skill validation so profile-generated artifacts can be checked once self profile enables `forma-reconcile`.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- The self profile still needs to explicitly enable `hone` and validate generated bundle/plugin output.

## Task 5: self-profile-validation

Outcome:
- Enabled `forma-reconcile` only in the Forma self profile and validated that self-profile bundle/plugin output includes it while default output remains five-stage.

Decision Notes:
- Kept generated validation artifacts in temporary directories and did not commit `dist/` or generated release surfaces.
- Left standalone creator temporary-injection output as five-stage; `forma-reconcile` is profile-enabled through Layer 3, not a generic no-profile default.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- External Codex plugin installation is outside the committed repository surface; the generated self-profile plugin was verified as installable input, but no repository file records an installed plugin state.
