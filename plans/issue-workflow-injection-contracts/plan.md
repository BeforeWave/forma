# Issue Plan

## Goal

Make Forma's creator-generated workflow bundles classify natural-language constraints before generation, so temporary injection JSON keeps always-on defaults light and routes expensive rules to the correct stage or conditional overlay.

## Plan Strategy

- Plan Strategy: step-execution

## Scope

In scope:

- Add a Layer 1 temporary injection generation standard under `source/skill-creator`.
- Require installed `forma-creator` bundles to load that standard before writing temporary injection JSON.
- Require agents using `forma-creator` to output the temporary injection file path and a classification table for injected constraints.
- Keep `constraints.default` limited to minimal always-on bottom lines.
- Route planning/materialization rules to `shape`, `gauge`, or `seal`.
- Route daily execution rules to `pour` or `flow`.
- Route docs, generated-baseline, migration, governance, and cross-layer rules through conditional overlays.
- Update sample profiles, Forma self profiles, committed generated baselines, and installed Codex bundles to demonstrate the classification contract.

Out of scope:

- Changing target skill package names or the canonical `forma-*` self-iteration skill names.
- Adding organization-specific downstream profiles or private workflow commands.
- Changing the temporary injection JSON schema to store classification metadata.
- Pushing local history to a remote.

## Approach

1. Define the Layer 1 standard for extracting and classifying natural-language constraints, then wire it into `forma-creator` instructions and target-fixed creator bundles.
2. Update profiles, docs, generated baselines, and installed Codex bundles so routine execution remains narrow and heavy guidance is stage-specific or conditional.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user request, installed `forma-*` workflow constraints, repository docs, current source tree, generated baselines, tests, and existing plan artifacts.
- Artifact paths:
  - active plan: `plans/issue-workflow-injection-contracts/plan.md`
  - active tasks: `plans/issue-workflow-injection-contracts/tasks.md`
  - active notes: `plans/issue-workflow-injection-contracts/implement-notes.md`
  - active runs: `plans/issue-workflow-injection-contracts/runs/task-*.md`
  - generated self bundle: `/tmp/forma-self-iteration-codex`
  - generated creator bundle: `/tmp/forma-creator-dist/codex/forma-creator`
  - installed self bundle: `~/.codex/skills/forma-{shape,gauge,seal,pour,flow}`
  - installed creator bundle: `~/.codex/skills/forma-creator`
- Generated-output policy:
  - committed generated baselines are derived from committed sample profiles;
  - self-iteration bundles and installed creator bundles are verified generated artifacts outside the committed tree.

## Constraints

- Layer 1 owns the standard for converting natural language into temporary injection JSON.
- Do not copy README, AGENTS, or other user docs verbatim into temporary injection.
- Keep `constraints.default` limited to minimal always-on bottom lines.
- Put planning and plan materialization rules under `shape`, `gauge`, or `seal`.
- Put daily execution rules under `pour` or `flow`.
- Put broad docs, generated-baseline, migration, governance, or cross-layer rules behind `conditional_overlays`.
- Do not make routine `forma-pour` / `forma-flow` read root governance docs, all run evidence, generated baselines, or full profile stacks by default.
- Keep downstream organization-specific commands and private paths out of committed sample profiles.

## Acceptance Criteria

- Layer 1 creator source includes a temporary injection generation standard with constraint classification rules and classification-table output requirements.
- Target-fixed generated `forma-creator` bundles include the temporary injection standard and require it from the target contract.
- Sample profiles and `profiles/forma-self` demonstrate light defaults with heavier rules in stage-specific constraints or conditional overlays.
- Generated and installed Codex `forma-pour` / `forma-flow` do not unconditionally require reading README.md, README.zh-CN.md, STRUCTURE.md, or AGENTS.md.
- Tests and verifier checks pass.
- `git log --pretty=fuller --date=iso-strict --reverse` shows equal AuthorDate and CommitDate per commit and a strictly increasing sequence.

## Validation

Check: full-tests
Command: uv run --extra dev pytest -p no:cacheprovider tests/
Note: full Forma test suite

Check: verify-layer-1
Command: uv run --extra dev forma verify source/skill-creator/
Note: Layer 1 / Layer 2 dogfood verification

Check: verify-generated-codex
Command: uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-codex/
Note: committed Codex generated baseline verification

Check: verify-generated-claude-code
Command: uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-claude-code/
Note: committed Claude Code generated baseline verification

Check: verify-self-bundle
Command: uv run --extra dev forma verify /tmp/forma-self-iteration-codex/
Note: generated Codex self-iteration bundle verification

Check: verify-creator-bundle
Command: uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator/
Note: generated Codex creator bundle verification

Check: inspect-installed-creator-standard
Command: rg -n "temporary-injection-generation.md|classification table|constraints.default" ~/.codex/skills/forma-creator/SKILL.md ~/.codex/skills/forma-creator/references/agent-target.md ~/.codex/skills/forma-creator/references/temporary-injection-generation.md
Note: installed creator should expose the Layer 1 temporary injection standard

Check: diff-check
Command: git diff --check
Note: whitespace and patch sanity check

Check: fuller-log-date-order
Command: git log --pretty=fuller --date=iso-strict --reverse
Note: confirms commit dates are explicit, equal per commit, and increasing

## Final Validation

```sh
uv run --extra dev pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-claude-code/
uv run --extra dev forma verify /tmp/forma-self-iteration-codex/
uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator/
git diff --check
git log --pretty=fuller --date=iso-strict --reverse
```

## Risks / Notes

- Layer 1 generation guidance affects how agents create future temporary injection JSON. The standard must stay explicit enough for agent behavior and narrow enough not to become a second profile schema.
- Installed bundle verification matters because current agent behavior depends on installed skills, not only source files.
