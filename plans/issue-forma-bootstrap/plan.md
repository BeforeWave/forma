# Issue Plan

## Goal

Establish Forma's minimum identity and workflow-convention substrate so subsequent issues have something to extend. Concrete deliverables:

- `README.md` — hero block + three-layer architecture positioning + MIT mention
- `STRUCTURE.md` — intended source-tree map (planned, not current state)
- `AGENTS.md` — minimal agent entrypoint pointing future agents at `plans/issue-<id>/`
- `LICENSE` — MIT license text

## Plan Strategy

- Plan Strategy: step-execution

## Scope

In scope:

- Author four root-level documents (`README.md`, `STRUCTURE.md`, `AGENTS.md`) and `LICENSE` at the Forma repository root.

Out of scope:

- `source/` tree contents (canonical plan-first methodology source fragments — deferred to issue-three-layer-suite)
- Layer 2 programmatic verifier code
- Layer 3 programmatic creator code (manifest, scaffold, build pipeline)
- Business injection layer demonstration
- CI/CD configuration
- Tests
- agentskills.io conformance verification (no skill files exist yet to verify)
- Examples or case studies

## Approach

- Hand-author each document. Forma's own tooling does not exist yet — bootstrap precedes tool-ification.
- Each document intentionally short: sets direction, does not pre-lock internal design decisions for Layers 2 and 3.
- `README.md` states the three-layer architecture as positioning (Layer 1 SKILL.md creator, Layer 2 programmatic verifier, Layer 3 programmatic creator with business injection), names the methodology (plan-first), and notes MIT licensing.
- `STRUCTURE.md` describes the intended source tree (planned, not current).
- `AGENTS.md` points future agents at `plans/issue-<id>/` and notes that the source tree is intentionally empty at bootstrap stage.
- `LICENSE` is the MIT license text with the appropriate copyright line.
- Source-of-truth refs: current conversation (2026-06-05). No external sources by explicit user instruction; Forma's bootstrap is self-contained.

## Constraints

- Do not write any `source/` tree contents in this issue.
- Do not add CI/CD, tests, or tooling code.
- Do not pre-lock Layer 2 or Layer 3 implementation decisions.
- Do not create directories beyond `plans/issue-forma-bootstrap/` and the repository root.

## Acceptance Criteria

- `README.md` exists at the repository root with hero block, three-layer architecture description, plan-first methodology mention, and MIT note.
- `STRUCTURE.md` exists at the repository root with the intended source-tree map.
- `AGENTS.md` exists at the repository root with a minimal entrypoint pointing future agents at `plans/issue-<id>/`.
- `LICENSE` exists at the repository root containing MIT license text.
- No files are added outside the four documents above and the existing `plans/issue-forma-bootstrap/` workflow state.

## Validation

## Final Validation

```sh
# no-programmatic-validation: bootstrap-docs-only
```

No automated test or lint tooling exists yet — Forma will build that capability in later issues. Final validation is human review of the four documents against the three-layer architecture and the constraints above.

## Risks / Notes

- plan-issue artifact commit policy: Forma's own methodology (authored in a later issue) should decide whether plan-issue proposals are persisted as separate artifacts or remain chat-only.
- Bootstrap-only: future issues will populate the `source/` tree (issue-three-layer-suite), Layer 2 verifier, Layer 3 programmatic creator, business injection layer, examples, and tests.
