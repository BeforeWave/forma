# Quick Start

Chinese version: [quick-start.zh-CN.md](./quick-start.zh-CN.md)

This page gets you from zero to Forma: have the agent extract project rules,
review them, then generate, verify, and install a workflow you can try. Commit
the profile only when the rules need long-term reuse; for a trial workflow, the
profile can be temporary.

Start with a workflow you can try. Ask the agent to extract the project rules,
show the proposed profile, then build, verify, and install it after approval.

## 1. Install The CLI

Install the Forma CLI:

```bash
pipx install forma-cli
forma --help
```

Then tell the agent:

```text
Use Forma to manage this project's engineering rules as a Codex workflow.
Extract the rules, show me the profile you propose, then after I approve it, build, verify, and install the workflow.
```

The agent should load Forma's profile guidance itself, then turn project rules
into a profile: stage constraints, tool habits, validation, proof, and stop
conditions. After you approve it, the profile can be saved to a temporary path,
used to generate a workflow, verified, and installed for the target.

If you need to reproduce the commands manually, a Codex direct skill bundle
looks like this:

```bash
forma build bundle --target codex --profile /tmp/myproject-profile.yaml --output /tmp/myproject-workflow
forma verify /tmp/myproject-workflow
forma install --target codex --scope project /tmp/myproject-workflow
```

If the profile's directory already contains `reinstall-workflow.sh`, run that
profile-local script instead of reconstructing build, verify, drift, install, or
marketplace commands from the guide. Agent-side reusable install setup and reuse
rules for a manual build/install process live in `forma explain agent`.

## 2. Try The Generated Workflow

After installing the generated output, start a new thread:

```text
Use forma:plan to plan this issue first.

Issue:
<paste the current issue, problem context, or task goal here>
```

Use `forma:*` triggers for plugin output. If you installed a direct skill
bundle instead, use its `forma-*` skill triggers.

The first useful output should be a proposal, not a patch. It should state the
goal, scope, project rules, and validation approach before touching files.

If repository evidence is needed, continue with:

```text
Use forma:ground to gather the evidence needed for this plan.
```

After evidence and the approach are accepted, lock the task contract:

```text
Use forma:lock to write the plan and task contract.
```

Then execute one accepted task:

```text
Use forma:execute to execute the next accepted task.
```

## 3. Inspect The Outputs

Look for these files:

- `plans/issue-<id>/plan.md`: current goal, scope, project rules, evidence paths, and validation strategy.
- `plans/issue-<id>/tasks.md`: ordered accepted tasks with boundaries, validation, and stop conditions.
- `plans/issue-<id>/runs/`: execution proof, validation results, and review records.

In this repository, real Forma plans live under [`../plans/`](../plans/).

## 4. Reuse Or Maintain Rules

If these rules should be shared or maintained long term, commit the reviewed
profile. Future workflow output can then be generated deterministically:

```bash
forma build bundle --target codex --profile myproject.yaml --output /tmp/bundle
forma verify /tmp/bundle
forma install --target codex --scope project /tmp/bundle
```

The same profile can target Claude Code:

```bash
forma build bundle --target claude-code --profile myproject.yaml --output /tmp/bundle-cc
forma verify /tmp/bundle-cc
forma install --target claude-code --scope user /tmp/bundle-cc
```

Or OpenCode:

```bash
forma build bundle --target opencode --profile myproject.yaml --output /tmp/bundle-opencode
forma verify /tmp/bundle-opencode
forma install --target opencode --scope project /tmp/bundle-opencode
```

## Choose A Path

| Path | Best for | Output |
|---|---|---|
| `forma explain agent` -> profile authoring | Extract project rules into a workflow; keep the profile temporary or commit it later. | Profile plus verified workflow bundle or plugin. |
| `forma build bundle` / `forma build plugin` | A reviewed profile already exists. | Repeatable workflow output from profile source. |
| `forma-creator` | Optional on-the-spot generation when you do not want to handle a profile file first. | Verified one-off skill bundle or plugin. |

## Install Locations

Generated workflows can be installed for one user or into a project:

| Target | Personal install | Project install |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.agents/skills` |
| OpenCode skills | `$HOME/.config/opencode/skills` | `.opencode/skills` |
| Codex plugins | Codex marketplace / plugin UI | Codex marketplace / plugin UI |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

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
- [Profile Schema](./profile-schema.md): how profiles describe stage constraints, tool habits, validation, and proof.
- [Forma Creator](./forma-creator.md): optional on-the-spot generation and temporary injection.
- [Skill Bundle](./skill-bundle.md): what Forma writes to disk.
- [Verifier](./verifier.md): what `forma verify` checks.
- [Targets](./targets.md): target install and metadata behavior.
- [Usage](./usage.md): full command reference.
