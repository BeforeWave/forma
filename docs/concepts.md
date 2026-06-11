# Concepts

Chinese version: [concepts.zh-CN.md](./concepts.zh-CN.md)

This page expands the README thesis: Forma compiles project rules into a
dedicated agent workflow, then uses workflow skills to apply those rules to each
task contract.

## What Forma Solves

AGENTS.md, custom skills, and Superpowers can give an agent rules and process.
That helps, but it still leaves a gap: the plan may not apply the team's most
important rules to the current task in a way reviewers can rely on and verify.

Forma fills that layer. It helps the agent extract engineering rules from docs,
code, tests, and conventions, then compiles those rules into workflow skills.
When a task starts, those skills make the agent produce a task contract:
evidence, boundaries, validation, proof, and stop conditions.

## Customize A Workflow In One Sentence

The lightweight entrypoint is `forma-creator`; the team does not need to write
YAML first:

```text
Use forma-creator to customize a workflow for this project.
Read the docs and code, extract the engineering rules, show them to me first;
after I confirm, generate the workflow and install it from the hints.
```

In this path, the rules enter a generated workflow you can try. It is for
exploration, quick adaptation, and project-specific fit.

If the team already wants durable source, ask the agent to draft a profile:

```text
Use Forma to extract engineering rules from this project's docs and code, and
draft a profile for me.
```

After review, the profile can be compiled into workflow outputs repeatedly.

## Three Layers

Forma puts project rules into three layers:

| Layer | Meaning |
|---|---|
| Project rules | Team-approved ways of working: authoritative sources, boundaries, required tools, validation depth, proof, and stop conditions. |
| Workflow output | Installed workflow skills: a Codex, Claude Code, or OpenCode skill bundle; Codex and Claude Code can also use plugin output. |
| Task contract | The plan contract the agent writes for one task under `plans/issue-<id>/`. |

With on-the-spot customization, project rules enter this generated workflow
output. With long-term maintenance, project rules become a tracked profile and
are compiled by Forma.

## Profile vs Task Contract

A profile should not hard-code every future task's files or commands. It
describes durable rules: which evidence is authoritative, which boundaries must
not be crossed, which tools must be used, how deep validation should go, and
when the agent must stop.

A task contract is the result of applying those rules to the current task. At
that point, the agent writes current evidence, file boundaries, task order,
validation commands, proof paths, and stop conditions.

So exact commands and task order in examples are usually task contract output,
not raw profile text. The profile determines what standards the plan must meet;
the task contract says how this task will be done.

## Compiler Model

Forma is a compiler that turns project rules into a dedicated agent workflow.

```text
profile / temporary injection  ->  Forma compiler  ->  workflow output  ->  task contract
durable / on-the-spot rules         compiler            install output       current task contract
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
| `forma-creator` | On-the-spot customization; try a project workflow first. | One-off workflow output you can install and try. |
| `forma explain profile` + agent | Durable source from the start. | Tracked profile YAML, reviewed before compilation. |
| `forma create-bundle` / `forma create-plugin` | A reviewed profile already exists. | Deterministic workflow bundle or plugin. |

All three paths end in verified workflow output. The difference is whether the
rules enter a one-off output first or become a long-term profile first.

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

Do not start by designing the perfect profile. First use `forma-creator` to
create a workflow you can try:

1. Install the CLI and `forma-creator`.
2. Ask the creator to extract rules from project docs and code.
3. Review the rules and fill gaps.
4. Generate and verify the workflow output.
5. Install it and trigger `forma:plan` for plugin output, or the matching
   `forma-*` direct skill trigger for a skill bundle.
6. Inspect the task contract: facts, boundaries, task order, validation, and proof.
7. Promote useful repeated rules into a tracked profile.

See [Quick Start](./quick-start.md) for the concrete path.

## Next Reads

- [Workflow Contract](./workflow-contract.md): stages, gates, boundaries, evidence, and proof.
- [Skill Bundle](./skill-bundle.md): generated output layout and manifest.
- [Profile Schema](./profile-schema.md): durable workflow source format.
- [Forma Creator](./forma-creator.md): on-the-spot generation and temporary injection.
- [Verifier](./verifier.md): what the verifier checks and cannot prove.
- [Targets](./targets.md): target install and metadata behavior.
- [Examples](./examples.md): sample profiles, generated baselines, and real runs.
- [Usage](./usage.md): command reference and install locations.
