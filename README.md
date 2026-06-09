<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**Customize a project workflow in one sentence, so agents plan, validate, and
deliver by your team's rules.**

Coding agents usually get into trouble in real projects not because they cannot
write code, but because they start implementation before the team's delivery
rules have been applied to the task.

Many teams already have agent-facing docs and ask agents to plan before
execution. The hard part is whether the plan applies project rules to the
current task: which facts count, what may change, how the result is proved, and
when the agent must stop.

Forma writes those rules into how the agent works. You can tell the agent:

```text
Use the Forma CLI to install forma-creator, then have it read this project's
docs and code, extract the rules, and generate a workflow I can use personally.
```

Forma brings those rules out of docs and conventions and into each task run.
The agent cannot stop at a rough plan; it must explain evidence, boundaries,
validation, proof, and stop conditions according to project standards.

---

## How Forma Works

Forma manages project rules across three layers:

- `profile`: team-approved practices, kept in version control for review and maintenance.
- `workflow output`: the installed agent workflow, as a Codex / Claude Code skill bundle or a Codex plugin.
- `task contract`: the plan contract the agent writes for one task, recorded under `plans/issue-<id>/`.

The default workflow uses four core skills to manage the task contract:

| Skill | Purpose |
|---|---|
| `forma-plan` | Align the goal with project rules and produce a reviewable proposal; do not write files or execute work. |
| `forma-ground` | Collect the evidence required by the rules from code, docs, issues, tests, and related sources. |
| `forma-lock` | Write the accepted approach into `plan.md` and `tasks.md`, locking the task contract. |
| `forma-execute` | Execute one accepted task, run validation, record proof, and stop when review is needed. |

`forma-showhand` is the continuous execution entrypoint: once a plan is locked,
it continues remaining tasks until blocked, validation does not pass, or human
input is needed.

When the team updates a profile, it updates which rules the workflow guards.
Regenerate the bundle or plugin, and the agent plans and executes against the
new constraints.

---

## Start Using Forma

`forma-creator` is the lightest entrypoint: use natural language to have the
agent read the project, extract rules, and generate a workflow for personal use.
When those rules need team review and ongoing iteration, move them into a
profile.

For personal use:

```text
Use forma-creator to customize a workflow for this project.
Summarize the key rules for me first.
After I confirm, generate and install it from the hints.
```

For long-term team maintenance, prepare a profile first:

```text
Use the Forma CLI profile path for this project:
draft a profile from project facts for review, then generate, verify, and
install the Codex workflow from that profile.
```

After installation, start a new thread:

```text
Use forma-plan to plan this issue first.

Issue:
<your task or issue>
```

The first useful response should be a proposal, not a patch. If the agent edits
files immediately, the workflow was not loaded or was not triggered.

Codex skill bundle, Claude Code, plugin, and install-location details are in
[Quick Start](./docs/quick-start.md) and [Usage](./docs/usage.md).

---

## Same Goal, Different Team Standards

For the same goal, "add rate limiting to settings", a plain plan may say:
read the code, add the limiter, run tests. A Forma-generated workflow carries
the team's rules into planning, so the agent first sets this task's work
boundaries and acceptance standard:

- API contract stability: classify API impact, response shape, and generator proof before changing handlers.
- Runtime control stability: reuse existing config, rollout switches, or limiter paths, and cover allowed, limited, disabled, and invalid-config cases.
- Design-system consistency: map to an existing component state, name the copy source, and record responsive and accessibility proof.
- Operator efficiency: place the state where an operator can act, preserve table and filter flow, and align runbook, telemetry, and audit behavior.

If the agent's plan does not apply those project rules, implementation has not
earned its start. See [Workflow Contract](./docs/workflow-contract.md) for a
detailed task-contract example and [Examples](./docs/examples.md) for profiles
and real tracked runs.

---

## Who It Fits

Forma starts with coding agents because software work has concrete source files,
generated outputs, tests, diffs, and review proof.

It fits projects with many rules, boundaries, and validation requirements: the
team does not only want an agent to perform one capability, but to plan,
validate, and stop according to project standards across tasks.

The same method can fit research, analysis, operations, release, governance,
customer handoff, or internal process execution when the work has stable
sources, clear boundaries, validation, and proof.

If the work only needs a few local preferences or one reusable capability, a
regular custom skill may be enough.

---

## Real Samples And Runs

The repository contains more than concept docs.

`examples/profiles/` contains sanitized profiles derived from real workflow
families. They show how teams express engineering rules, source-reading rules,
validation depth, proof, and stop conditions.

`examples/generated/` contains Codex and Claude Code baselines compiled from
those profiles. They are used to inspect generated output and catch drift.

`plans/issue-*/` is Forma's own development record. Each issue records `plan.md`,
`tasks.md`, and `runs/task-*.md` with real task contracts, validation results,
and proof from Forma development.

---

## Status

Forma is still early.

Forma writes team rules into the workflow and task contract, but it does not make
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

| | |
|---|---|
| [Quick Start](./docs/quick-start.md) | First run, creator path, and tracked-profile path. |
| [Concepts](./docs/concepts.md) | Project rules, workflow outputs, task contracts, and stage boundaries. |
| [Workflow Contract](./docs/workflow-contract.md) | How task contracts organize evidence, boundaries, validation, and proof. |
| [Profile Schema](./docs/profile-schema.md) | YAML source for durable engineering rules. |
| [Forma Creator](./docs/forma-creator.md) | Conversational workflow generation and temporary injection. |
| [Skill Bundle](./docs/skill-bundle.md) | Generated output layout. |
| [Verifier](./docs/verifier.md) | What verification checks and cannot prove. |
| [Targets](./docs/targets.md) | Codex and Claude Code target behavior. |
| [Examples](./docs/examples.md) | Sanitized sample profiles, generated baselines, and real tracked runs. |
| [Usage](./docs/usage.md) | Command reference. |

Apache-2.0 - see [LICENSE](./LICENSE)
