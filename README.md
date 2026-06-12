<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**Turn project rules into a dedicated agent workflow.**

AGENTS.md, custom skills, and Superpowers can give an agent rules and process.
For lightweight projects, that is usually enough.

Forma turns project rules into workflow skills. Those skills make the agent
preview how the rules apply to the current task before implementation, then
execute against a task contract and leave proof.

Once Forma is installed, one sentence can have the agent generate that workflow
from the current project.

> **Good fit:** repositories with many rules, boundaries, validation needs, and
> reviewable planning or execution records.
>
> **Not a good fit:** lightweight cases that only need a few personal agent
> preferences.

---

## Same Goal, Different Plan Shapes

For the same goal, "add rate limiting to settings", a plain plan may say: read
the code, add the limiter, run tests.

Forma's difference is that project rules enter the workflow, so the agent
writes different planning priorities. You do not have to remind it every time.

| Rule emphasis | Planning priority becomes |
|---|---|
| API compatibility first | Which endpoints, fields, and generated files are affected, and whether API review is needed. |
| Rollout first | Which switch to use, how to disable or roll back, and how to test invalid config. |
| User experience first | How rate limiting appears, and how copy, component state, and accessibility are checked. |
| Operations first | Who sees the state, and how they decide, handle, and trace it. |

This is not a required checklist. It shows how the same request can produce
different planning boundaries and acceptance checks under different project
rules.

---

## What Forma Produces

Most users see three things:

| Name | What it does |
|---|---|
| `profile` | A structured description of extracted engineering rules: stage constraints, tool habits, validation, proof, and stop conditions. |
| `workflow bundle / plugin` | Generated from the profile and installed into Codex, Claude Code, or OpenCode so the agent follows the same rules. |
| `task contract` | The task boundary the agent writes before implementation: goal, scope, validation, and proof. |

Commit the profile only when the rules need long-term reuse. For a trial
workflow, it can be a temporary file and does not need to be kept.

The default workflow uses four stages to manage the task contract
lifecycle, plus one continuous execution entrypoint:

| Stage | Purpose |
|---|---|
| `plan` | Align the goal with project rules and produce a reviewable proposal; do not write files or execute work. |
| `ground` | Gather the evidence required by the rules from code, docs, issues, tests, and related sources. |
| `lock` | Write the accepted approach into `plan.md` and `tasks.md`, locking the task contract. |
| `execute` | Execute one accepted task, run validation, record proof, and stop when review is needed. |

`showhand` is the continuous execution entrypoint: once a plan is locked,
it continues remaining tasks until blocked, validation fails, or human input is
needed.

Trigger names depend on the installed output. A Forma plugin exposes plugin-local
stages like `plan` and supports Codex-qualified triggers such as `forma:plan`.
A direct skill bundle is installed as standalone skills with the `forma-*`
prefix.

When the team updates a profile, it updates which rules the workflow guards.

---

## What A Task Contract Looks Like

This is a simplified excerpt from one real Forma `plan.md`:

```text
Goal:
  Make Forma CLI help clear enough for agents to choose
  the right command path without trial and error.

Scope:
  Update root CLI help, no-argument behavior, tests/test_cli.py,
  docs/usage.md, and docs/usage.zh-CN.md.

Out of scope:
  Do not change create-bundle, create-plugin, install, verify,
  or explain execution semantics.
  Do not restore forma create or add a compatibility alias.

Approach:
  Make `forma` with no arguments exit 0 and print the same
  agent-facing routing guidance as `forma --help`.
  Each command help should say what the agent should run next.

Validation:
  uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
  uv run --extra dev forma
  uv run --extra dev forma --help
```

This is not a note added after implementation. It is the task boundary the agent
locks before editing code. The task list and execution proof are recorded in
[`plans/issue-cli-agent-facing-help/`](./plans/issue-cli-agent-facing-help/).

---

## Start Using Forma

The lightest path is to have the agent summarize project rules, then generate
and install a workflow:

```bash
pipx install forma-cli
```

Then tell the agent:

```text
Use Forma to generate a Codex workflow for this project.
Show me the project rules you extracted first; after I approve them, generate and install it.
```

The agent should load Forma's profile guidance itself, then generate, verify,
and install the workflow after you approve the rules.

After the generated workflow is installed, start a new thread:

```text
Use forma:plan to plan this issue first.

Issue:
<your task or issue>
```

If you installed a direct skill bundle rather than a plugin, use the matching
`forma-*` skill trigger instead.

The first useful response should be a proposal, not a patch.

> **If the agent edits files immediately**, the workflow was not loaded or was
> not triggered; Forma is not running.

If the rules should be shared or maintained long term, keep the profile in
version control. If you already have a reviewed profile, use `forma
create-bundle --profile <profile.yaml>` or `forma create-plugin --profile
<profile.yaml>` to generate workflow output. Full commands are in [Quick
Start](./docs/quick-start.md) and [Usage](./docs/usage.md).

---

## Who It Fits

**Good fit:**

- Repositories that use coding agents frequently
- Projects with generated files, fixtures, migrations, public APIs, or sensitive data paths
- Teams whose rules are hard to apply reliably through prompts alone
- Teams that need reviewable agent plans and execution records
- Work where the agent should stop when scope, evidence, or permission is unclear

**Probably not a good fit:**

- Spelling fixes, one-off summaries, or tiny edits

---

## Real Samples And Runs

The repository contains more than concept docs.

`examples/profiles/` contains sanitized profiles derived from real workflow
families. They show how teams express engineering rules, source-reading rules,
validation depth, proof, and stop conditions.

`examples/generated/` contains committed baselines compiled from those profiles.
They are used to inspect generated output and catch drift; they do not prove
that a real agent will always execute correctly.

`plans/issue-*/` is Forma's own development record. Each issue records `plan.md`,
`tasks.md`, and `runs/task-*.md` with real task contracts, validation results,
and proof. Judge a run by those records.

---

## Status

Forma is still early. It supports skill bundles for Codex, Claude Code, and
OpenCode today. Plugin source is supported for Codex and Claude Code.

It helps agents plan before they act and leave evidence after they act. Each run
still needs to be judged by the contract and proof it leaves behind.

Current focus: easier profile generation, smoother bundle/plugin installation,
stronger verification, and more real runs.

Forma also uses its own plan-before-execute workflow for development; this
repository's profile source lives in
[`profiles/forma-self/`](./profiles/forma-self/).

---

## Documentation

**Start here:**

| | |
|---|---|
| [Quick Start](./docs/quick-start.md) | First run, workflow generation, verification, and installation. |
| [Concepts](./docs/concepts.md) | Project rules, workflow outputs, task contracts, and stage boundaries. |
| [Workflow Contract](./docs/workflow-contract.md) | How task contracts organize evidence, boundaries, validation, and proof. |

**Reference:**

| | |
|---|---|
| [Profile Schema](./docs/profile-schema.md) | How to structure a profile when rules need long-term maintenance. |
| [Skill Bundle](./docs/skill-bundle.md) | Generated output layout. |
| [Verifier](./docs/verifier.md) | What verification checks and cannot prove. |
| [Targets](./docs/targets.md) | Codex, Claude Code, and OpenCode target behavior. |
| [Examples](./docs/examples.md) | Sanitized sample profiles, generated baselines, and real tracked runs. |
| [Usage](./docs/usage.md) | Command reference. |

Apache-2.0 - see [LICENSE](./LICENSE)
