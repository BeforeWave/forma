# Quick Start

Chinese version: [quick-start.zh-CN.md](./quick-start.zh-CN.md)

This page gets you from zero to a running Forma workflow. Start with the default
Codex plugin, then shape the harness after you have seen one real task produce
plan files, task boundaries, validation gates, and proof.

## Install Forma

Install the CLI:

```bash
pipx install git+https://github.com/BeforeWave/forma.git
forma --help
```

The examples below assume `forma` is available on `PATH`.

## First Run: Default Codex Plugin

Generate the default Plan-First plugin:

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
```

Then add that local plugin to a Codex marketplace and install it with
`codex plugin add <plugin>@<marketplace>`, or install it from the Codex plugin
UI.

Send the current issue or task context to Codex and ask it to start with planning:

```text
Use forma-plan to plan this issue first.

Issue:
<paste the current issue, problem context, or task goal here>
```

A useful first run should not jump from goal to patch. The first result should
be a chat-level proposal or handoff, not plan files. It should settle the goal,
scope, approach, validation model, and whether repository grounding is needed.

If repository evidence is needed, ask Codex to use `forma-ground`.

After the proposal and any grounding are accepted, lock the plan:

```text
Use forma-lock to write the plan and task contract.
```

Then execute the next accepted task:

```text
Use forma-execute to execute the next accepted task.
```

## What To Inspect

After a workflow-guided run, look for reviewable output:

- `plans/issue-<id>/plan.md`: clarified goal, scope, approach, validation,
  strategy, and artifact/evidence boundary when needed.
- `plans/issue-<id>/tasks.md`: ordered accepted tasks with delivery targets,
  exact validation commands or shared checks, dependencies, and constraints.
- `plans/issue-<id>/runs/`: task proof when the workflow records completed work.

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
Customize a workflow for this repo.

First inspect the repository structure, validation paths, generated outputs,
and project conventions.

I care about:
- generated outputs must come from source;
- docs-only changes should use lightweight checks;
- behavior changes should look for nearby tests first;
- risky judgments should stop for my confirmation.
```

The creator should classify those concerns, generate the target-specific
workflow bundle or Codex plugin allowed by its fixed target contract, and verify
the output before handoff.

## Two Lightweight Customization Paths

There are two lightweight ways to let an agent shape project rules. Both can be
conversational; they differ by output:

| Path | Input | Output |
|---|---|---|
| `forma-creator` | Natural-language project concerns, classified by the creator into temporary injection. | Verified one-off harness: a skill bundle or Codex plugin. |
| `forma explain profile` + agent | CLI profile authoring guidance, repository inspection, and human input. | Tracked profile YAML; after review, the CLI can regenerate the harness consistently. |

## Generate From A Tracked Profile

Use a tracked profile when project rules are durable enough to review as
source.

Generate Codex skills:

```bash
forma create-bundle --target codex --profile examples/profiles/sample-software/sample-software-plan-first.yaml --output /tmp/software-plan-first-codex
forma verify /tmp/software-plan-first-codex
```

Install them into Codex:

```bash
forma install --target codex --scope user /tmp/software-plan-first-codex
```

The same profile can target Claude Code:

```bash
forma create-bundle --target claude-code --profile examples/profiles/sample-software/sample-software-plan-first.yaml --output /tmp/software-plan-first-claude-code
forma verify /tmp/software-plan-first-claude-code
forma install --target claude-code --scope user /tmp/software-plan-first-claude-code
```

## Install Locations

Generated workflows can be installed for one user or into a project:

| Target | Personal install | Project install |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | Codex marketplace / plugin UI | Codex marketplace / plugin UI |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |

Review project skills before trusting them. Generated skills can include
scripts and target-specific tool behavior.

## Draft A Profile Conversationally With The CLI

Inside a downstream project with Forma installed, tell the agent:

```text
Run:
  forma explain profile --target codex

Use that output as the profile authoring standard.
Inspect this repository and propose a tracked Forma profile.
Show the profile structure before writing files.
Explain each constraint placement and mark unknowns explicitly.
```

This is also a lightweight path, but the output is versionable profile source,
not a one-off harness. Review the profile before using it as durable source.

## Next Reads

- [Concepts](./concepts.md): the project rules, workflow harness, and task execution model.
- [Workflow Contract](./workflow-contract.md): what the generated workflow enforces.
- [Skill Bundle](./skill-bundle.md): what Forma writes to disk.
- [Profile Schema](./profile-schema.md): how durable workflow source is structured.
- [Forma Creator](./forma-creator.md): how one-off generation works.
- [Verifier](./verifier.md): what `forma verify` checks.
- [Targets](./targets.md): target install and metadata behavior.
- [Usage](./usage.md): command reference and install locations.
