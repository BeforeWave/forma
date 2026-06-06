# Concepts

Chinese version: [concepts.zh-CN.md](./concepts.zh-CN.md)

This page explains Forma's mental model and core terms. Read this after the
README and before writing a large profile.

Agents do not usually fail because they cannot produce text or change files.
They fail because the shape of the work is implicit.

Forma is the place for the "how this work should happen" part.

## Compiler Model

Forma is a compiler for project-specific agent workflows.

```text
workflow profile  ->  Forma compiler  ->  skill bundle
source                compiler            installable artifact
```

The profile is source. The generated skill bundle is the deployment artifact.
Codex and Claude Code are target surfaces.

Forma does not execute project tasks directly. It generates the workflow an
agent follows while executing tasks.

## Three Layers

Keep these layers separate:

| Layer | Meaning |
|---|---|
| Forma itself | The generator, CLI, verifier, creator builder, methodology source, and target adapters. |
| Generated bundle | The workflow skills installed into Codex or Claude Code. |
| Profile and temporary injection | The input layer for durable and one-off workflow rules. |

Collapsing these layers causes confusion. A profile is not an installed skill.
A generated skill is not the source of truth. A temporary injection is not a
durable team policy unless it is promoted into a reviewed profile.

## Five Core Concepts

| Concept | Meaning |
|---|---|
| Workflow contract | The staged rules for moving from demand to evidence, plan, execution, proof, and continuation. |
| Profile | Durable workflow source reviewed like project source. |
| Temporary injection | One-off generation input for scoped rules that should not become durable policy by accident. |
| Skill bundle | Target-specific compiled artifact containing stage skills, references, scripts, and a manifest. |
| Target surface | The runtime agent environment, currently Codex or Claude Code. |

See [Workflow Contract](./workflow-contract.md), [Profile Schema](./profile-schema.md),
and [Skill Bundle](./skill-bundle.md) for the detailed pages.

## Default Workflow

The default methodology is plan-first:

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

These stage names are defaults:

| Stage | Plain English | Job |
|---|---|---|
| `shape` | Clarify the request | Turn a loose request into a bounded proposal. |
| `gauge` | Read before acting | Gather repository, spec, docs, and related evidence. |
| `seal` | Lock the plan | Convert the proposal into an accepted task contract. |
| `pour` | Execute within bounds | Implement one accepted task and record proof. |
| `flow` | Continue safely | Resume from the sealed plan, or stop when proof is missing. |

Not into those names? They are defaults, not doctrine. Projects can rename
generated skills while keeping these stage semantics.

## Why It Matters

Forma's value is not that it writes code. It does not.

Forma turns repeated AI-working discipline into versioned, installable,
verifiable workflow source. It helps make agent work:

- repeatable: durable rules have a source location and lifecycle;
- staged: clarification, evidence, planning, execution, and proof are not collapsed into one prompt;
- bounded: implementation stays inside accepted tasks;
- reviewable: reviewers can inspect the path from demand to evidence, plan, execution, and proof;
- portable: the same workflow can be emitted for supported target surfaces.

## Fit

Use Forma when AI agents are already part of recurring work and the workflow
needs stable planning, evidence, validation, proof, and stop conditions.

AI coding is the first obvious fit, but it is not the only one. Forma can also
fit research, analysis, publishing, design review, customer handoff, governance,
or operations work when the work has repeatable sources, boundaries, stages, and
proof requirements.

You probably do not need Forma when:

- a few repository rules in `AGENTS.md` are enough;
- one reusable capability should be a single custom skill;
- the main problem is organizing requirements and spec facts;
- the task has no stable sources, no meaningful boundaries, no acceptance path, and no need for reuse.

Forma can work beside spec tools, planning docs, `AGENTS.md`, and generic skill
creators. Those layers define demand, local context, or capabilities. Forma
defines how the agent moves through them.

## First Successful Run

Do not begin by designing a perfect profile. Try one small workflow first.

1. Choose a small sample profile.
2. Generate a Codex or Claude Code skill bundle.
3. Verify the generated bundle.
4. Install it into one target surface.
5. Trigger one plan-first task.
6. Inspect the plan, task contract, validation result, and run evidence.
7. Promote only useful rules into durable profile source.

See [Quick Start](./quick-start.md) for the concrete path.

## Next Reads

- [Workflow Contract](./workflow-contract.md): stages, gates, boundaries, evidence, and proof.
- [Skill Bundle](./skill-bundle.md): generated artifact layout and manifest.
- [Profile Schema](./profile-schema.md): durable workflow source format.
- [Usage](./usage.md): command reference and install locations.
