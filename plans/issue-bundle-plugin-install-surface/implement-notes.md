# Implement Notes

## Task 1: bundle-terminology-contract

Outcome:
- Renamed the Layer 3 creator API, Layer 1 creator script, Layer 2 verifier report/context fields, manifests, tests, and verifier fixtures from suite terminology to bundle terminology.

Decision Notes:
- Existing committed example outputs are byte-compared by `tests/test_creator.py`, so the sample generated Codex and Claude Code bundles were regenerated from the updated creator to keep the committed baseline aligned with the new manifest contract.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 2: cli-create-plugin-install

Outcome:
- Added default-profile-backed `create-bundle`, Codex-only `create-plugin`, and verified local `install` support for single skills, skill bundles, and Codex plugins.

Decision Notes:
- The task validation invokes `create-bundle` without `--profile`, so the generic no-injection default profile was introduced in this task instead of waiting for `default-workflow-profile`; task 3 can still refine positioning and generated metadata around that tracked profile.
- Install classification checks Codex plugin roots before bundle roots so a plugin with nested `skills/` installs as `.codex/plugins/<plugin-id>` rather than expanding into `.codex/skills`.

Plan Gaps Found:
- The task order placed default profile creation after CLI validation that already required the default profile.

Classifications:
- None.

Deviations From Plan:
- Added `profiles/default/forma-plan-first.yaml` during task 2 to satisfy the current task's validation contract.

Follow-ups:
- Task 3 should review the default profile descriptions and plugin metadata for final product wording.
