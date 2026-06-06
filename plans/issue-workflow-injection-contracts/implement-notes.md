# Implement Notes

## Task 1: layer-1-injection-classification

Outcome:
- Added the Layer 1 temporary injection generation standard and wired installed creator instructions to load it before writing temporary injection JSON.
- Added canonical profile authoring principles beside the temporary injection standard so target-fixed creators and CLI guidance share the same source-level policy.

Decision Notes:
- Kept durability metadata out of the injection JSON schema. The required durability and promotion decision is reported in the agent's classification table instead.

Plan Gaps Found:
- The previous creator guidance allowed agents to write temporary injection JSON without a first-class constraint classification standard.

Classifications:
- Layer 1 instruction behavior change with creator-builder output contract coverage.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 2: profile-execution-classification

Outcome:
- Updated sample profiles and `profiles/forma-self` to demonstrate light defaults, stage-specific rules, and conditional overlays for heavy scenarios.
- Regenerated committed backend generated baselines, the Codex self-iteration bundle, and the installed Codex `forma-*` and `forma-creator` bundles.
- Added a read-only `forma explain` CLI surface that assembles profile and temporary-injection guidance from canonical references for agents that cannot inspect Forma source files.
- Packaged canonical methodology and Layer 1 creator source as installed runtime assets so `forma explain`, default `forma create`, and default `forma build-creator` work outside a Forma source checkout.

Decision Notes:
- Kept root governance docs available through planning/finalization stages and conditional execution overlays, not routine `pour` / `flow` defaults.
- Kept explain output read-only stdout and source-backed; the CLI formats reference contents instead of maintaining another copy of profile rules.
- Used `importlib.resources` for installed assets and kept source-checkout paths as development overrides/fallbacks.

Plan Gaps Found:
- Sample profiles did not explicitly demonstrate the same temporary injection classification principle Layer 1 now requires.

Classifications:
- Layer 3 profile and generated-output update with installed-artifact verification.

Deviations From Plan:
- None.

Follow-ups:
- Remote publication remains a separate explicit decision.
