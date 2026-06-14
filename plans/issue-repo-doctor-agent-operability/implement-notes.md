# Implement Notes

## Task 1: remove-artifact-doctor

Outcome:
- Removed the CLI-reachable artifact doctor path and replaced artifact-doctor tests with rejection coverage for the old bare-path and hidden subcommand routes.

Decision Notes:
- Chose deletion rather than deprecation because the locked issue explicitly rejects artifact doctor compatibility. Generated artifact validity remains with `forma verify`; installation compatibility remains with `forma install` and build/plugin handoff guidance.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- Later tasks still need to remove stale artifact doctor references from `forma explain agent` and reader docs.

## Task 2: repo-doctor-report

Outcome:
- Replaced the repo doctor `ActionableReport` wrapper with a dedicated `forma.repo-doctor.report.v1` report model and renderer set for `human`, `agent`, and `json`.

Decision Notes:
- Chose a small source-owned report object in `src/forma/repo_doctor.py` instead of extending the shared report envelope, because the locked plan intentionally breaks the old JSON contract and needs top-level repo-operability fields for `init --from-report`.
- Classified common package and CI files as `tooling-signals` only. They can support Agent review; explicit documented commands are required for the `validation` domain to become `contract`.
- Kept Forma presence under `agent-specific-integrations.forma` with `optional` status. Missing `.forma/` can produce programmatic actions while core readiness remains tied to the core domains.

Plan Gaps Found:
- None

Classifications:
- `needs-agent` is used when core domains are missing, signaled, or warned; no `needs-human` status is produced unless a later task adds owner-decision-only blockers.

Deviations From Plan:
- None

Follow-ups:
- `init --from-report` still needs to consume the new schema and materialize deterministic base configuration plus handoff inputs.

## Task 3: init-from-report

Outcome:
- Added `forma init --from-report <report>` support that validates a repo-doctor report, plans or applies deterministic `.forma` base files, and writes report-derived Agent handoff inputs.

Decision Notes:
- Stored report-derived handoff inputs under `.forma/agent-operability/` so the files live beside Forma base configuration and can be tracked as draft project source.
- Sanitized the tracked `doctor-report.json` subject to `.`. The transient report may contain an absolute subject, but the materialized handoff copy should stay portable.
- Kept `from-report` status as `needs-agent` because deterministic file materialization is only the bridge to Agent remediation.

Plan Gaps Found:
- None

Classifications:
- Schema, command, missing subject, and subject mismatch are classified as `unsafe` init blockers.

Deviations From Plan:
- None

Follow-ups:
- Docs and `forma explain agent` still need to describe the new report-driven init path.

## Task 4: docs-explain-sync

Outcome:
- Updated `forma explain agent`, usage docs, target docs, and CLI tests so public guidance describes repo-only doctor behavior and the report-driven init path.

Decision Notes:
- Replaced artifact-doctor guidance with `forma verify`, build command `agent/json` handoff, and explicit install-boundary language because generated artifact validation now belongs to those surfaces.
- Kept reader docs concise and placed the fuller repo-doctor to `init --from-report` workflow in the usage command reference and Agent guide.

Plan Gaps Found:
- None

Classifications:
- Old `forma doctor <path>` guidance is stale product routing and was removed from docs and `explain agent`.

Deviations From Plan:
- None

Follow-ups:
- None

## Task 6: rework-001-cli-adoption-contract

Outcome:
- Normalized repo-doctor adoption output, init-from-report wording, and explain-agent guidance around Forma workflow source and project-rule management.

Decision Notes:
- Chose `owner_confirmations` for the new Forma adoption approval list while preserving the existing top-level `human_decisions` report field and `human-decisions.md` filename for compatibility with the accepted repo-doctor schema.
- Kept `.forma` cleanup as an explicit-owner-request policy in doctor output instead of presenting `.forma` retention as an approval question.

Plan Gaps Found:
- None

Classifications:
- Existing top-level `human_decisions` remains a compatibility field; adoption-specific approval points now use `owner_confirmations`.

Deviations From Plan:
- None

Follow-ups:
- None
