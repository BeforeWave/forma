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
