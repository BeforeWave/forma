# Implement Notes

## Task 1: stage-vocabulary-and-lock-policy

Outcome:
- Replaced legacy workflow vocabulary in canonical methodology, creator guidance, docs, and tests; lock-stage guidance now requires user confirmation before plan/task commits.

Decision Notes:
- Kept canonical internal stage keys stable while changing generated/user-visible stage vocabulary to Forma's current plan, ground, lock, execute, and showhand wording.
- Treated showhand as execution-only after plan lock; plan creation or repair remains a lock-stage responsibility.

Plan Gaps Found:
- The task required source and docs changes together because stale vocabulary validation scans `source/methodology`, `source/skill-creator`, `docs`, and `tests`.

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Later tasks still need adapter code, description generation, policy alignment, process-gate notes hardening, and regenerated release artifacts.

## Task 2: workflow-target-adapters

Outcome:
- Added a workflow target adapter for Codex, Claude Code, and OpenCode bundle/plugin differences, and moved bundle/plugin target behavior out of the emitter and plugin builder.

Decision Notes:
- Kept composition target-neutral except for the resource path rename needed after task 1; target-specific decoration, Codex `openai.yaml`, plugin localization, plugin metadata, and unsupported plugin checks now live behind `workflow_adapter`.
- Kept OpenCode plugin output unsupported through the adapter instead of adding a plugin artifact path.

Plan Gaps Found:
- The source generator still needed its resource path updated from `plan-issue-rules.md` to `plan-stage-rules.md` before target adapter validation could generate bundles.

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Description quality, docs/test policy alignment, implement-notes process-gate checks, and regenerated release artifacts remain for later tasks.

## Task 3: description-generation-quality

Outcome:
- Split generated trigger descriptions from body guidance for Layer 3 and self-contained creator output, and stopped emitting empty conditional-reference instructions for routes without overlay resources.

Decision Notes:
- Used `stages.<stage>.short_description` only for trigger/UI surfaces while keeping `skills.<stage>.description` or methodology descriptions as the long body guidance.
- Kept verifier enforcement conditional on actual conditional reference resources so a bundle is not forced to contain an empty `Conditional References` section.

Plan Gaps Found:
- Task validation had to be narrowed in the plan correction commit because full creator/CLI regression depends on committed example and release artifacts that later tasks own.

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Docs/examples policy alignment, implement-notes process-gate checks, and regenerated release artifacts remain for later tasks.

## Task 4: docs-tests-policy-alignment

Outcome:
- Aligned sample profile sources and committed generated example bundles with the new public stage names and lock-stage policy.

Decision Notes:
- Kept release `dist/` untouched for the dedicated release-artifact task; this task only updates source examples and test fixtures needed for creator/runtime validation.
- Restored generated examples from the previously verified regenerated output, then relied on task validation to prove they still match the current generator.

Plan Gaps Found:
- Full `tests/test_creator.py` validation depends on committed generated examples, so sample profile/generated fixture updates are required before later release artifact regeneration.

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Implement-notes process-gate checks and default no-profile release artifacts remain for later tasks.

## Task 5: implement-notes-process-gate

Outcome:
- Added implement-notes guidance and runner review checks for process-gate exception wording in current-task decision notes.

Decision Notes:
- Scoped the runner check to the current task's `Decision Notes:` block so ordinary implementation rationale remains valid while gate-exception wording fails review.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Regenerated default no-profile release artifacts remain for the final task.

## Task 6: regenerate-and-verify-release-artifacts

Outcome:
- Regenerated default no-profile creator, skill-bundle, and plugin release artifacts under `dist/`.
- Updated profile adoption to preserve trigger short descriptions separately from long body descriptions so profile round-trip validation can represent the regenerated output.

Decision Notes:
- Used only default generation commands for `dist/`; self-profile generation was not written to the release surface.

Plan Gaps Found:
- Final validation exposed that profile adoption still treated the generated frontmatter description as the long skill description after task 3 split trigger copy from body guidance.

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- None
