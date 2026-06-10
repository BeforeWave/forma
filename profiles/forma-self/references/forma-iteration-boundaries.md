# Forma Iteration Boundaries

Use these boundaries when planning or executing changes in the Forma repository.

## Layer Boundaries

- Layer 1 lives under `source/skill-creator/`. It is the self-contained creator skill source and must remain usable after `forma build-creator` injects methodology resources.
- Layer 2 lives under `source/skill-creator/scripts/forma_verifier/`. It must stay stdlib-only for agent-side verification, while remaining importable by the developer CLI.
- Layer 3 lives under `src/forma/creator/` and `src/forma/adapters/`. It composes canonical methodology and tracked profiles into target-specific Plan-First workflow output.
- Canonical methodology lives under `source/methodology/`. Do not duplicate source-of-truth methodology content inside Layer 1.
- Project-owned profiles live under `profiles/`. Sanitized public examples live under `examples/profiles/`. Downstream-specific profiles belong in the downstream repository that owns their constraints.

## Artifact Boundaries

- Active issue planning state lives under `plans/issue-<id>/`.
- Committed release artifacts under `dist/` are default Forma outputs with no tracked profile and no temporary injection unless a future issue explicitly changes the release contract.
- `profiles/forma-self/` output is for temporary self-iteration checks or local installation only; do not commit it into `dist/`.
- Committed generated drift baselines currently live under `examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/` and `examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/`.
- Profile-only examples should be documented as profile-only unless the plan explicitly adds committed generated baselines for them.
- Temporary generated suites should go under `/tmp` or another transient output path and should not be committed.

## Review Boundaries

- Source behavior changes need tests.
- Verifier rule changes need positive and negative rule coverage.
- Profile schema changes need resolver and creator integration tests.
- Generated baseline replacements need create/verify evidence and status review that includes both deletions and additions.
- Documentation changes should keep README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md consistent when their topic overlaps.
