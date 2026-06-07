# Quick Start

Chinese version: [quick-start.zh-CN.md](./quick-start.zh-CN.md)

This page gets you from zero to a running Forma workflow. Start with the default
Codex plugin, then shape the harness only after you have seen one real run.

## Install Forma

Install the CLI:

```bash
pipx install git+https://github.com/BeforeWave/forma.git
forma --help
```

The examples below assume `forma` is available on `PATH`.

## First Run: Default Codex Plugin

Generate and install the default Plan-First plugin:

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma install --target codex --scope project /tmp/forma-codex-plugin
```

Then ask Codex to start with planning:

```text
Use forma-plan to plan this issue first.
```

A useful first run should not jump from goal to patch. It should clarify the
goal, gather evidence, lock an execution contract, then execute tasks with
proof.

## What To Inspect

After a workflow-guided run, look for reviewable output:

- `plans/issue-<id>/plan.md`: clarified goal, scope, approach, validation,
  strategy, and output and proof boundary.
- `plans/issue-<id>/tasks.md`: ordered accepted tasks with delivery targets,
  proof obligations, dependencies, and constraints.
- `plans/issue-<id>/runs/`: execution proof when the workflow records it.

In this repository, real Forma plans live under [`../plans/`](../plans/).

## Shape The Harness With `forma-creator`

Use `forma-creator` when you want an agent to turn project-specific concerns
into a one-off workflow before writing durable profile YAML.

Build and install a Codex creator:

```bash
forma build-creator --target codex --output /tmp/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

Then talk to Codex like a collaborator:

```text
Use forma-creator to customize a workflow for this repo. First look at the
repository structure and common validation paths. I care about generated
outputs coming from source, lightweight checks for docs-only changes, nearby
tests before code changes, and surfacing uncertain calls for me to decide.
```

The creator should classify those concerns, generate a target-specific workflow
bundle or Codex plugin allowed by its fixed target contract, and verify the
output before handoff.

## Generate From A Tracked Profile

Use a tracked profile when project principles are durable enough to review as
source.

Generate Codex skills:

```bash
forma create-bundle \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

Install them into Codex:

```bash
forma install --target codex --scope user /tmp/backend-plan-first-codex
```

The same profile can target Claude Code:

```bash
forma create-bundle \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-claude-code

forma verify /tmp/backend-plan-first-claude-code
forma install --target claude-code --scope user /tmp/backend-plan-first-claude-code
```

## Install Locations

Generated workflows can be installed for one user or into a project:

| Target | Personal install | Project install |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | `$HOME/.codex/plugins` | `.codex/plugins` |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |

Review project skills before trusting them. Generated skills can include
scripts and target-specific tool behavior.

## Ask An Agent To Draft A Profile

Inside a downstream project with Forma installed, tell the agent:

```text
Run:
  forma explain profile --target codex

Use that output as the profile authoring standard.
Inspect this repository and propose a tracked Forma profile.
Show the profile structure before writing files.
Explain each constraint placement and mark unknowns explicitly.
```

Use this as a drafting path, not an auto-commit path. Review the profile before
using it as durable source.

## Next Reads

- [Concepts](./concepts.md): the profile, workflow, and runtime harness model.
- [Workflow Contract](./workflow-contract.md): what the generated workflow enforces.
- [Skill Bundle](./skill-bundle.md): what Forma writes to disk.
- [Profile Schema](./profile-schema.md): how durable workflow source is structured.
- [Forma Creator](./forma-creator.md): how one-off generation works.
- [Verifier](./verifier.md): what `forma verify` checks.
- [Targets](./targets.md): target install and metadata behavior.
- [Usage](./usage.md): command reference and install locations.
