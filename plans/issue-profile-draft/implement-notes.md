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

## Task 3: profile-draft-docs-smoke

Outcome:
- Documented `forma profile draft` in English and Chinese command/profile-authoring docs, and proved the generated draft can feed `forma create-bundle` plus `forma verify`.

Decision Notes:
- Options considered: document the draft workflow only in the command reference, or also add the profile-authoring boundary near the schema guidance. Selected both `docs/usage*` and `docs/profile-schema*` so agents can find the command path and reviewers can see that `profile.draft.yaml` is candidate output until promoted.
- Options considered: edit the accepted plan's final validation snippet, edit the bundled runner, or use a temporary validation wrapper. Selected the temporary wrapper for `review-ready` only because the final validation commands themselves passed, while the runner split the multi-line `tmp_root` shell variable across isolated `env -i` calls.

Plan Gaps Found:
- The final validation block is a valid shell snippet, but the current bundled workflow runner executes each fenced line in a fresh environment, so `tmp_root=...` does not persist to later lines without a validation wrapper.

Classifications:
- The smoke draft and generated bundle are transient validation artifacts under `/private/tmp`; they were not committed or installed.

Deviations From Plan:
- `review-ready` was rerun with a temporary `/private/tmp` `bash` wrapper that preserves only the `tmp_root` assignment across the runner's split final-validation lines. No source, plan, runner, generated smoke output, or install target was changed by the wrapper.

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
