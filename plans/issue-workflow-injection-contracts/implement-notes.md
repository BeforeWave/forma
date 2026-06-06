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

## Task 3: source-adapter-injection-boundary

Outcome:
- Removed GitHub issue context loading from base `shape` / `seal` methodology requirements and from default copied generated-skill resources.
- Added optional generic script-resource adapter guidance as a reusable packaged reference for explicit profile or temporary injection usage, with the GitHub issue helper kept as a concrete sample script.
- Updated Layer 1 guidance and CLI-backed profile/temporary-injection references to classify source-context adapters as stage-specific injection/profile behavior, not `constraints.default`.
- Added a concrete script resource injection template to the canonical references and creator instructions so both `forma explain temporary-injection` and installed `forma-creator` show agents how to copy a helper script into `scripts/`.
- Renamed the sanitized Go backend sample to `sample-backend-go-github-issue-tracked` and made it explicitly opt into generic script-resource usage plus the GitHub issue helper for `shape` and `seal`, proving the helper is profile-owned rather than base methodology.
- Regenerated committed backend baselines and fresh Codex creator build artifacts for verification.

Decision Notes:
- GitHub issue loading is a source-context adapter, not a baseline plan-first capability. It should be available to profiles or temporary injection, but not emitted into every base `shape` / `seal` skill.
- The adapter usage reference must stay generic. The concrete GitHub issue helper is only a sample script/resource selected by the sample profile or temporary injection.

Plan Gaps Found:
- The previous base methodology made `gh issue view` behavior unconditional, which coupled every generated suite to GitHub CLI availability and authentication.

Classifications:
- Cross-layer methodology, Layer 1 guidance, generated-output, and installed-bundle boundary correction.

Deviations From Plan:
- None.

Follow-ups:
- None.
