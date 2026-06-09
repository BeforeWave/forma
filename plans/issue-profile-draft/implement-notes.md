# Implement Notes

## Task 1: profile-draft-cli-contract

Outcome:
- Added the `forma profile draft` CLI route, deterministic explicit-source collection, three-file draft package writing, output replacement policy, and `load_profile()` self-check coverage.

Decision Notes:
- Options considered: render only the minimal `profile` mapping needed by `load_profile()`, or include the default Forma Plan-First stage and skill metadata in every draft. Selected the default stage metadata because later accepted criteria require the reviewed draft to feed `forma create-bundle` plus `forma verify`; keeping that structure in the first draft avoids a YAML shape that passes the loader but cannot produce a verified Plan-First bundle.
- Options considered: merge new files into an existing output directory with `--replace`, or clean the output directory before writing. Selected clean replacement because the command promises exactly `profile.draft.yaml`, `missing-decisions.md`, and `agent-review.md`.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- None

## Task 2: profile-draft-extractor

Outcome:
- Added conservative extraction coverage for stage-specific constraints, supported validation commands, unsupported explicit sources, and review-only missing decisions.

Decision Notes:
- Options considered: place ambiguous validation-looking lines with no recognized command in `validation_commands`, or let them continue through rule and missing-decision classification. Selected continued classification so path references such as `plans/issue-<id>/runs/` remain execution constraints instead of disappearing as failed command extraction.
- Options considered: treat every broad planning phrase as `constraints.default`, or keep `constraints.default` limited to always-on safety rules such as preserving unrelated work. Selected the minimal default path because broad reading, generated baselines, adapter material, route-specific rules, and private/local paths must stay out of default constraints.

Plan Gaps Found:
- None

Classifications:
- Broad root-doc reading, generated-baseline/release checks, adapter-like source collection, route-specific rules, one-off task material, and private/local paths are reported in `missing-decisions.md`.

Deviations From Plan:
- None

Follow-ups:
- None
