# Concepts

Chinese version: [concepts.zh-CN.md](./concepts.zh-CN.md)

This page expands the README thesis: Forma turns project rules into a
dedicated agent workflow, then uses workflow skills to apply those rules to each
task contract.

## What Forma Solves

AGENTS.md, custom skills, and Superpowers can give an agent rules and process.
That helps, but it still leaves a gap: the plan may not apply the team's most
important rules to the current task in a way reviewers can rely on and verify.

Forma fills that layer. It helps the agent extract engineering rules from docs,
code, tests, and conventions, then turns those rules into workflow skills.
When a task starts, those skills make the agent produce a task contract:
evidence, boundaries, validation, proof, and stop conditions.

## Generate A Workflow In One Sentence

The lightweight entrypoint is to have the agent extract project rules, show them
for review, then generate the workflow:

```text
Use Forma to generate a Codex workflow for this project.
Show me the project rules you extracted first; after I approve them, generate and install it.
```

The agent should organize extracted rules into a profile. The profile can be
temporary input for a trial workflow; commit it only when the rules need to be
shared or maintained long term.

## Three Layers

Forma puts project rules into three layers:

| Layer | Meaning |
|---|---|
| Profile | A structured description of extracted engineering rules: stage constraints, tool habits, validation, proof, and stop conditions. |
| Workflow output | Workflow skills generated from the profile and installed for the agent as a skill bundle or plugin. |
| Task contract | The plan contract the agent writes for one task under `plans/issue-<id>/`. |

For a trial, the profile can be a temporary local file. For long-term
maintenance, the profile becomes tracked source and Forma regenerates workflow
outputs from it.

## Profile vs Task Contract

A profile should not hard-code every future task's files or commands. It
describes engineering rules: which evidence is authoritative, which boundaries
must not be crossed, which tools must be used, how deep validation should go,
and when the agent must stop.

A task contract is the result of applying those rules to the current task. At
that point, the agent writes current evidence, file boundaries, task order,
validation commands, proof paths, and stop conditions.

So exact commands and task order in examples are usually task contract output,
not raw profile text. The profile determines what standards the plan must meet;
the task contract says how this task will be done.

## Generation Model

Forma turns the project rules in a profile into a dedicated agent workflow.

```text
profile  ->  Forma generator  ->  workflow output  ->  task contract
rules        generator             install output       current task contract
```

Codex, Claude Code, and OpenCode are the current skill-bundle targets. The same
profile can generate different target outputs while preserving task-level
workflow semantics.

Forma does not execute project tasks directly. It generates the workflow skills
an agent follows while executing tasks.

## Default Workflow

The default workflow has a plan-before-execute shape:

```text
goal -> proposal -> evidence -> task contract -> task execution -> proof
```

Four core stages manage the task contract lifecycle:

| Stage | Purpose | Boundary |
|---|---|---|
| `plan` | Align the goal with project rules and produce a proposal. | Do not write files or execute work. |
| `ground` | Gather the facts required by the rules. | Read-only; do not decide final tasks. |
| `lock` | Write `plan.md` and `tasks.md`, locking the task contract. | Materialize only the accepted approach. |
| `execute` | Execute one accepted task, run validation, and record proof. | Do not cross task boundaries or bypass stop conditions. |

`showhand` is the autopilot entrypoint for `execute`, not a fifth
planning stage. After the plan is locked, it continues accepted tasks until
blocked, validation does not pass, or human input is needed.

Output names depend on the install shape. Plugins expose plugin-local stages
such as `plan`, and Codex plugin triggers can use `forma:*` names such as
`forma:plan`. Direct skill bundles use standalone `forma-*` skill names.
Projects can rename generated skills, but the stage semantics should remain the
same.

## Three Paths

| Path | Best for | Result |
|---|---|---|
| `forma explain profile` + agent | Extract project rules into a workflow; keep the profile temporary or commit it later. | Profile plus verified workflow output. |
| `forma build bundle` / `forma build plugin` | A reviewed profile already exists. | Deterministic workflow bundle or plugin. |
| `forma-creator` | Optional on-the-spot path when you do not want to handle a profile file first. | One-off workflow output you can install and try. |

All three paths end in verified workflow output. The default mental model is
that rules first become a profile; whether to keep that profile is your choice.

## Why Boundaries And Proof Matter

Forma's value is writing project rules into the agent's work path:

- which facts must be confirmed first;
- which boundaries must not be crossed;
- which validation can prove the result;
- where proof is recorded;
- when the agent must stop for review.

Once these enter the task contract, reviewers inspect more than the patch. They
can also inspect whether the agent planned, gathered evidence, validated, and
proved the work according to project-approved rules.

This is still not a behavior guarantee. Models and host environments still
matter. Forma provides a clearer control surface: workflow, task contract, and
proof remain inspectable.

## Fit

Use Forma when a project's engineering rules should shape how an agent handles
specific tasks.

AI coding is the first fit, but not the only one. Research, analysis,
operations, governance, release, and customer handoff work can use similar
workflows when the work has stable sources, boundaries, stages, validation, and
proof.

You probably do not need Forma when:

- a few local rules are enough;
- one reusable capability should be a single custom skill;
- the main problem is unsettled requirements or source facts;
- the task has no stable sources, boundaries, acceptance path, or reuse need.

Forma can work beside spec tools, planning docs, project instructions, and
generic skill creators. Those layers define demand, local context, or
capabilities. Forma defines how the agent moves through them and what proof it
must leave.

## First Successful Run

Do not start by designing the perfect profile. First create a workflow you can
try:

1. Install the CLI.
2. Ask the agent to extract rules from project docs and code.
3. Review the rules and fill gaps.
4. Generate and verify the workflow output.
5. Install it and trigger `forma:plan` for plugin output, or the matching
   `forma-*` direct skill trigger for a skill bundle.
6. Inspect the task contract: facts, boundaries, task order, validation, and proof.
7. Commit the profile only if the rules should be reused.

See [Quick Start](./quick-start.md) for the concrete path.

## Next Reads

- [Workflow Contract](./workflow-contract.md): stages, gates, boundaries, evidence, and proof.
- [Skill Bundle](./skill-bundle.md): generated output layout and manifest.
- [Profile Schema](./profile-schema.md): how profiles describe stage constraints, tool habits, validation, and proof.
- [Forma Creator](./forma-creator.md): optional on-the-spot generation and temporary injection.
- [Verifier](./verifier.md): what the verifier checks and cannot prove.
- [Targets](./targets.md): target install and metadata behavior.
- [Examples](./examples.md): sample profiles, local build instructions, and real runs.
- [Usage](./usage.md): command reference and install locations.
