# Quick Start

Chinese version: [quick-start.zh-CN.md](./quick-start.zh-CN.md)

This page gets you from zero to Forma: install the CLI, install
`forma-creator` for the agent, let it extract project rules from docs and code,
then generate a workflow you can try. Once the rules prove useful, promote them
into a tracked profile.

## 1. Install CLI And Creator

Install the Forma CLI:

```bash
pipx install forma-cli
forma --help
```

For Codex, build and install the creator skill:

```bash
forma build-creator --target codex --output /tmp/forma-creator
forma verify /tmp/forma-creator/codex/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

Start a new agent thread and say:

```text
Use forma-creator to customize a workflow for this project.
Read the docs and code, extract the engineering rules, show them to me first;
after I confirm, generate the workflow and install it from the hints.
```

The creator makes the agent extract rules from project facts: authoritative
sources, change boundaries, validation depth, proof, and stop conditions. After
you confirm them, it generates and verifies a workflow output you can try, then
reports the output path and install hints.

## 2. Try The Generated Workflow

After installing the generated output, start a new thread:

```text
Use forma-plan to plan this issue first.

Issue:
<paste the current issue, problem context, or task goal here>
```

The first useful output should be a proposal, not a patch. It should state the
goal, scope, project rules, and validation approach before touching files.

If repository evidence is needed, continue with:

```text
Use forma-ground to gather the evidence needed for this plan.
```

After evidence and the approach are accepted, lock the task contract:

```text
Use forma-lock to write the plan and task contract.
```

Then execute one accepted task:

```text
Use forma-execute to execute the next accepted task.
```

## 3. Inspect The Outputs

Look for these files:

- `plans/issue-<id>/plan.md`: current goal, scope, project rules, evidence paths, and validation strategy.
- `plans/issue-<id>/tasks.md`: ordered accepted tasks with boundaries, validation, and stop conditions.
- `plans/issue-<id>/runs/`: execution proof, validation results, and review records.

In this repository, real Forma plans live under [`../plans/`](../plans/).

## 4. Promote Rules Into A Profile

If you want durable profile source from the start, ask the agent:

```text
Use Forma to extract engineering rules from this project's docs and code, and
draft a profile for me. After I approve the profile, generate, verify, and
install the Codex workflow from it.
```

The agent uses `forma explain profile --target codex` to load the profile
authoring standard. The flow is: draft profile, review it, then generate,
verify, and install the workflow from the hints.

If you already have a reviewed profile, generate deterministically:

```bash
forma create-bundle --target codex --profile myproject.yaml --output /tmp/bundle
forma verify /tmp/bundle
forma install --target codex --scope project /tmp/bundle
```

The same profile can target Claude Code:

```bash
forma create-bundle --target claude-code --profile myproject.yaml --output /tmp/bundle-cc
forma verify /tmp/bundle-cc
forma install --target claude-code --scope user /tmp/bundle-cc
```

## Choose A Path

| Path | Best for | Output |
|---|---|---|
| `forma-creator` | On-the-spot customization; try a project workflow first. | Verified one-off skill bundle or Codex plugin. |
| `forma explain profile` + agent | Durable, reviewable source from the start. | Tracked profile YAML, then compiled workflow. |
| `forma create-bundle` | A reviewed profile already exists. | Repeatable workflow bundle from profile source. |

## Install Locations

Generated workflows can be installed for one user or into a project:

| Target | Personal install | Project install |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | Codex marketplace / plugin UI | Codex marketplace / plugin UI |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |

Review project skills before trusting them. Generated skills can include
scripts and target-specific tool behavior.

## Verify Outputs

Always verify before installing, committing, or sharing a generated bundle or
plugin source:

```bash
forma verify /tmp/myproject-bundle
```

Verification checks structure and methodology rules. It does not prove the
profile is a good project decision or that the agent will always obey the
workflow. See [Verifier](./verifier.md).

## Next Reads

- [Concepts](./concepts.md): rules, workflow outputs, task contracts, and stage boundaries.
- [Workflow Contract](./workflow-contract.md): what the generated workflow defines.
- [Forma Creator](./forma-creator.md): on-the-spot customization and temporary injection.
- [Profile Schema](./profile-schema.md): durable profile source.
- [Skill Bundle](./skill-bundle.md): what Forma writes to disk.
- [Verifier](./verifier.md): what `forma verify` checks.
- [Targets](./targets.md): target install and metadata behavior.
- [Usage](./usage.md): full command reference.
