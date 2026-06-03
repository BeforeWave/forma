# Implement Notes

## Task 1: bootstrap-docs

Outcome:
- README.md, STRUCTURE.md, AGENTS.md, and LICENSE authored at the repository root. Forma now has its minimum identity and workflow-convention substrate; source tree and tooling remain intentionally absent for later issues.

Decision Notes:
- LICENSE copyright holder: chose "BeforeWave" (the publishing entity per the configured `origin` remote at `the configured origin remote`) over the local git `user.name`. Rationale: MIT attribution conventionally names the publishing entity, and this repository will live under that organization.
- README does not name specific agent platforms for Layer 1 (e.g., Codex, Claude Code); instead it uses "any compatible agent". Rationale: keeps the document self-contained per the bootstrap instruction to avoid external-source semantics; specific platform support belongs in a later issue that introduces the corresponding adapters.
- STRUCTURE uses two tables (top-level paths + per-issue planning state) and explicit "present" / "planned" status to keep the planned tree readable. Path names in planned rows are tentative; later issues may revise them as the methodology source and tooling materialize.
- AGENTS.md is intentionally minimal — a "Read first" list pointing future agents at `plans/issue-<id>/` plus a short "Working rules" block. Avoids pre-committing to any source/ path or tooling convention that does not yet exist.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None. All four documents + LICENSE land within the stated scope and constraints (no `source/`, no CI/CD/tests/tooling, no Layer 2/3 pre-lock).

Follow-ups:
- plan-issue artifact commit policy remains undecided; Forma's own methodology (a later issue) should settle whether plan-issue proposals are persisted as separate artifacts or remain chat-only.
- Tentative path names in STRUCTURE.md (`source/`, `tools/`, `examples/`, `tests/`) may be revised by subsequent issues; treat them as planning intent, not naming commitments.
