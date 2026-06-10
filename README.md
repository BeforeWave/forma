<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**Compile project rules into a dedicated agent workflow.**

AGENTS.md, custom skills, and Superpowers can give an agent rules and process.
For lightweight projects, that is usually enough.

Forma compiles project rules into workflow skills. Those skills make the agent
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

## Same Goal, Different Standards

For the same goal, "add rate limiting to settings", a plain plan may say: read
the code, add the limiter, run tests.

Different teams define an acceptable plan differently. Forma-generated workflow
skills bring those standards into planning, so the agent must state boundaries
and acceptance criteria before it edits code.

| Team concern | Constraint in the task contract |
|---|---|
| API contract stability | Classify API impact, response shape, and generator proof before changing handlers. |
| Runtime control stability | Reuse existing config, rollout switches, or limiter paths; cover allowed, limited, disabled, and invalid-config cases. |
| Design-system consistency | Map to an existing component state, name the copy source, and record responsive and accessibility proof. |
| Operator efficiency | Put the state where an operator can act, preserve table and filter flow, and align runbook, telemetry, and audit behavior. |

Four teams receiving the same issue can produce four different task contracts.
Forma does not decide which standard is right; it compiles the standard your
team already trusts.

---

## What Forma Produces

Forma produces three things:

| Output | Meaning |
|---|---|
| `profile` | Team-approved practices kept in version control for review and maintenance. |
| `workflow bundle / plugin` | Agent workflow installed into Codex or Claude Code. |
| `task contract` | The plan contract the agent writes for one task, recorded under `plans/issue-<id>/`. |

The default workflow uses four stage skills to manage the task contract
lifecycle, plus one continuous execution entrypoint:

| Skill | Purpose |
|---|---|
| `forma-plan` | Align the goal with project rules and produce a reviewable proposal; do not write files or execute work. |
| `forma-ground` | Gather the evidence required by the rules from code, docs, issues, tests, and related sources. |
| `forma-lock` | Write the accepted approach into `plan.md` and `tasks.md`, locking the task contract. |
| `forma-execute` | Execute one accepted task, run validation, record proof, and stop when review is needed. |

`forma-showhand` is the continuous execution entrypoint: once a plan is locked,
it continues remaining tasks until blocked, validation fails, or human input is
needed.

When the team updates a profile, it updates which rules the workflow guards.
Regenerate the bundle or plugin, and the agent plans and executes against the
new constraints.

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
  build-creator, or explain execution semantics.
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

The lightest path is to install `forma-creator` and let the agent read the
current project rules to generate a trial workflow:

```bash
pipx install beforewave-forma
forma build-creator --target codex --output /tmp/forma-creator
forma verify /tmp/forma-creator/codex/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

Then tell the agent:

```text
Use forma-creator to customize a workflow for this project.
Summarize the key rules for me first.
After I confirm, generate and install it from the hints.
```

After the generated workflow is installed, start a new thread:

```text
Use forma-plan to plan this issue first.

Issue:
<your task or issue>
```

The first useful response should be a proposal, not a patch.

> **If the agent edits files immediately**, the workflow was not loaded or was
> not triggered; Forma is not running.

For shared or long-lived team rules, use the tracked profile path:

```text
Use Forma to extract engineering rules from this project's docs and code,
and draft a profile for review.
After I confirm the profile, generate, verify, and install the Codex workflow
from it.
```

If you already have a reviewed profile, use `forma create-bundle --profile
<profile.yaml>` or `forma create-plugin --profile <profile.yaml>` to generate
workflow output. Full commands are in [Quick Start](./docs/quick-start.md) and
[Usage](./docs/usage.md).

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

`examples/generated/` contains Codex and Claude Code baselines compiled from
those profiles. They are used to inspect generated output and catch drift; they
do not prove that a real agent will always execute correctly.

`plans/issue-*/` is Forma's own development record. Each issue records `plan.md`,
`tasks.md`, and `runs/task-*.md` with real task contracts, validation results,
and proof. Judge a run by those records.

---

## Status

Forma is still early.

Forma writes team rules into workflow and task contracts, but it does not make
the model perfectly obedient. Judge each run by the actual contract and proof
the agent leaves behind.

Current focus:

- Lower the cost of extracting project rules and generating profiles.
- Make workflow bundles and Codex plugins easier to install.
- Improve generated bundle verification.
- Add examples with real task contracts, execution, validation, and proof.

Committed generated examples are mainly drift checks. Runtime behavior should be
judged by the contract and proof left by the agent during a real run.

Forma also uses its own plan-before-execute workflow for development; this
repository's profile source lives in
[`profiles/forma-self/`](./profiles/forma-self/).

---

## Documentation

**Start here:**

| | |
|---|---|
| [Quick Start](./docs/quick-start.md) | First run, creator path, and tracked-profile path. |
| [Concepts](./docs/concepts.md) | Project rules, workflow outputs, task contracts, and stage boundaries. |
| [Workflow Contract](./docs/workflow-contract.md) | How task contracts organize evidence, boundaries, validation, and proof. |

**Reference:**

| | |
|---|---|
| [Profile Schema](./docs/profile-schema.md) | YAML source for durable engineering rules. |
| [Forma Creator](./docs/forma-creator.md) | Conversational workflow generation and temporary injection. |
| [Skill Bundle](./docs/skill-bundle.md) | Generated output layout. |
| [Verifier](./docs/verifier.md) | What verification checks and cannot prove. |
| [Targets](./docs/targets.md) | Codex and Claude Code target behavior. |
| [Examples](./docs/examples.md) | Sanitized sample profiles, generated baselines, and real tracked runs. |
| [Usage](./docs/usage.md) | Command reference. |

Apache-2.0 - see [LICENSE](./LICENSE)
