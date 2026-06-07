# Concepts

Chinese version: [concepts.zh-CN.md](./concepts.zh-CN.md)

This page expands the README mental model. Read it after the homepage framing
and before writing a large profile.

Agents do not usually fail because they cannot produce text or change files.
They fail because the project-specific way of working is implicit.

Forma is for compiling that way of working into a runtime harness.

## What Changes

After AI coding becomes part of everyday work, code is no longer the only
project output that matters.

The spec an agent follows, the evidence it reads, the plan it seals, the task
boundary it accepts, and the proof it leaves behind all become part of the
project lifecycle. If those outputs are vague, scattered, or only remembered
inside a chat, the agent's work style changes from run to run.

Projects already express engineering style through architecture, code patterns,
test habits, and review standards. With agents in the loop, projects also need
to express how work is delegated: what the agent must clarify, what it must
read, when it may act, when it must stop, and how it proves the result.

Forma treats that agent-working style as source. It compiles project principles
into staged skills, then those skills shape how the agent handles each concrete
development goal.

## Three Layers

Forma works in three layers:

| Layer | Meaning |
|---|---|
| Layer 0: Build the profile | Define the project's long-lived engineering principles and boundaries. |
| Layer 1: Generate the workflow | Forma compiles the profile into a project-specific Plan-First workflow skill bundle. |
| Layer 2: Runtime harness | When a concrete development goal appears, the agent runs under that workflow. |

Keep these layers separate. A profile is not an installed skill. A generated
skill bundle is not the source of truth. The runtime harness is not another
file; it is how the installed workflow constrains the agent while it works.

## Compiler Model

Forma is a compiler for project-specific Plan-First workflow skills.

```text
profile  ->  Forma compiler  ->  workflow skill bundle  ->  runtime harness
source       compiler            installed output            agent behavior
```

Codex and Claude Code are targets. The same profile can produce target-specific
outputs while preserving the workflow contract.

Forma does not execute project tasks directly. It generates the skills an agent
follows while executing tasks.

## Five Core Concepts

| Concept | Meaning |
|---|---|
| Workflow contract | The staged rules for moving from demand to evidence, plan, execution, proof, and review. |
| Profile | Durable project principle source reviewed like project source. |
| Temporary injection | One-off generation input for scoped rules that should not become durable policy by accident. |
| Skill bundle | Target-specific compiled output containing stage skills, references, scripts, and a manifest. |
| Target | The agent environment that loads generated skills, currently Codex or Claude Code. |

See [Workflow Contract](./workflow-contract.md), [Profile Schema](./profile-schema.md),
and [Skill Bundle](./skill-bundle.md) for the detailed pages.

## Default Workflow

The default methodology is plan-first:

```text
clarify -> gather evidence -> lock plan -> execute task
plan    -> ground         -> lock      -> execute
```

These public skill names are defaults:

| Default skill | Plain English | Job |
|---|---|---|
| `forma-plan` | Clarify the request | Turn a loose request into a bounded proposal. |
| `forma-ground` | Read before acting | Gather repository, spec, docs, and related evidence. |
| `forma-lock` | Lock the plan | Convert the proposal into an accepted task contract. |
| `forma-execute` | Execute within bounds | Implement one accepted task and record proof. |

`forma-showhand` is the candy skill for continuous `forma-execute`: after the
plan has been reviewed and fixed, use it to let the agent keep executing the
accepted task list under the same harness.

Not into the public names above? They are defaults, not doctrine. Projects can
rename generated skills while keeping these stage semantics.

## Why It Matters

Forma's value is not that it writes code. It does not.

Forma turns project-specific agent discipline into versioned, installable,
verifiable workflow source. It helps make agent work:

- repeatable: durable rules have a source location and lifecycle;
- staged: clarification, evidence, planning, execution, and proof are not collapsed into one prompt;
- bounded: implementation stays inside accepted tasks;
- reviewable: reviewers can inspect the path from demand to evidence, plan, execution, and proof;
- portable: the same profile can be emitted for supported targets.

## Fit

Use Forma when a project's standing principles should shape how agents handle
development goals at runtime.

AI coding is the first obvious fit, but it is not the only one. Forma can also
fit research, analysis, publishing, design review, customer handoff, governance,
or operations work when the work has repeatable sources, boundaries, stages, and
proof requirements.

You probably do not need Forma when:

- a few local project rules are enough;
- one reusable capability should be a single custom skill;
- the main problem is organizing requirements and spec facts;
- the task has no stable sources, no meaningful boundaries, no acceptance path, and no need for reuse.

Forma can work beside spec tools, planning docs, project instructions, and
generic skill creators. Those layers define demand, local context, or
capabilities. Forma defines how the agent moves through them.

## First Successful Run

Do not begin by designing a perfect profile. Try one small workflow first.

1. Install the CLI.
2. Generate the default Codex plugin or a small target bundle.
3. Install it into one target.
4. Trigger one plan-first task.
5. Inspect the plan, task contract, validation result, and proof.
6. Shape the harness with creator or profile rules only after the workflow proves useful.

See [Quick Start](./quick-start.md) for the concrete path.

## Next Reads

- [Workflow Contract](./workflow-contract.md): stages, gates, boundaries, evidence, and proof.
- [Skill Bundle](./skill-bundle.md): generated output layout and manifest.
- [Profile Schema](./profile-schema.md): durable workflow source format.
- [Forma Creator](./forma-creator.md): one-off workflow generation.
- [Verifier](./verifier.md): what verification checks and cannot prove.
- [Targets](./targets.md): target install and metadata behavior.
- [Examples](./examples.md): end-to-end workflow walkthrough.
- [Usage](./usage.md): command reference and install locations.
