# Forma Iteration Boundaries

Use these boundaries when planning or executing changes in the Forma repository.

## Layer Boundaries

- Layer 1 lives under `source/skill-creator/`. It is the self-contained creator skill source and must remain usable after `forma build creator` injects methodology resources.
- Layer 2 lives under `source/skill-creator/scripts/forma_verifier/`. It must stay stdlib-only for agent-side verification, while remaining importable by the developer CLI.
- Layer 3 lives under `src/forma/creator/` and `src/forma/adapters/`. It composes canonical methodology and tracked profiles into target-specific Plan-First workflow output.
- Canonical methodology lives under `source/methodology/`. Do not duplicate source-of-truth methodology content inside Layer 1.
- Forma's self-profile source lives under `.forma/`. Sanitized public examples live under `examples/profiles/`. Downstream-specific profiles belong in the downstream repository that owns their constraints.

## Artifact Boundaries

- Active issue planning state lives under `plans/issue-<id>/`.
- Committed release artifacts under `dist/` are product default workflow outputs generated without an explicit `--profile` and with no temporary injection unless a future issue explicitly changes the release contract.
- `.forma/` is durable self-profile source for this repository. Generated output from `.forma/` is for temporary checks or local installation only; do not commit that output into `dist/`.
- Public examples are profile source by default. Do not commit `examples/generated/` output unless the active issue explicitly makes generated drift baselines part of the review surface.
- Profile-only examples should remain profile-only unless the plan explicitly adds committed generated baselines for them.
- Temporary generated suites should go under `/tmp` or another transient output path and should not be committed.

## Review Boundaries

- Source behavior changes need tests.
- Verifier rule changes need positive and negative rule coverage.
- Profile schema changes need resolver and creator integration tests.
- Generated baseline replacements need create/verify evidence and status review that includes both deletions and additions.
- Documentation changes should keep README.md, README.zh-CN.md, STRUCTURE.md, and AGENTS.md consistent when their topic overlaps.
