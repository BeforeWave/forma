# Concepts

Chinese version: [concepts.zh-CN.md](./concepts.zh-CN.md)

This page explains the mental model behind Forma.

Read this after the README and before writing a large profile.

Forma is easiest to understand if you keep three layers separate:

1. **Forma itself** — the generator and toolchain.
2. **The generated bundle** — the workflow skills installed into Codex or Claude Code.
3. **Profile and temporary injection** — the input layer for durable and one-off rules.

Forma does not directly execute project tasks. It generates the workflow that an agent follows while executing tasks.

---

## Forma's Layers

### Forma itself

Forma reads profiles, the canonical Plan-First methodology, target-surface rules, and optional one-off generation constraints.

It emits target-specific workflow bundles.

### Forma-generated bundle

The generated bundle is what Codex or Claude Code actually uses.

A normal plan-first bundle contains five coordinated skills that map to the same workflow stages:

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

### Profile and temporary injection

Profiles contain durable project rules and should be reviewed like source.

Temporary injection contains one-off generation constraints and should not become permanent policy by accident.

---

## What Forma Generates

The generated output is an installable workflow bundle.

The exact skill names and directories may be renamed by a profile or temporary injection, but the semantic stages remain:

| Forma stage | Current meaning | Plain user-facing name |
|---|---|---|
| `shape` | bounded proposal | Plan Issue / clarify the demand |
| `gauge` | evidence gathering | Ground Plan / understand the current state |
| `seal` | execution contract | Finalize Plan / lock acceptance and validation |
| `pour` | accepted task with proof | Implement Feature / execute one task |
| `flow` | controlled continuation | Continue Work / proceed only when safe |

The input/output model is:

```text
profile YAML
+ canonical methodology
+ optional temporary injection
+ target = codex | claude-code
        |
        v
Forma compiler
        |
        v
target-specific workflow bundle
+ coordinated skills
+ references and scripts selected by the profile or injection
+ .forma-manifest.json provenance
+ verifier-compatible structure
```

The stage names are Forma's internal metaphor. Projects can rename generated skill names and display labels while preserving stage semantics.

---

## Why It Matters

Forma's value is not that it writes code. It does not.

Forma turns repeated AI-working discipline into versioned, installable, verifiable workflow source.

It helps make agent work:

- **repeatable**: durable project rules have a source location and lifecycle;
- **staged**: clarification, evidence gathering, planning, execution, and proof are not collapsed into one prompt;
- **bounded**: implementation stays inside accepted tasks instead of expanding by convenience;
- **reviewable**: reviewers can inspect the path from demand to evidence, plan, execution, and proof;
- **portable**: the same workflow style can be emitted for supported target surfaces.

---

## Core Assets

Forma is useful because workflow is represented as source, not memory.

### Profiles

Profiles record durable project rules:

- source-of-truth expectations;
- validation commands;
- stage constraints;
- conditional routes;
- generated skill resources;
- explicit source adapters.

Profiles should be reviewed and maintained by people. Agents can help draft them, but temporary ideas should not become durable profile source without review.

### Manifests

Generated bundles include `.forma-manifest.json`.

The manifest records provenance such as target information, methodology version or digest, resolved profile stack, profile hashes, generated skills, and generator provenance.

### Verification

`forma verify` checks generated plan-first suites and `forma-creator` bundles for structural and methodology consistency.

Verification does not replace content review. It keeps generated output from being an unchecked pile of markdown.

---

## When Not To Use Forma

Forma is heavier than a repository instruction file or a single custom skill.

Do not start with Forma if the problem is only "make this agent remember a few rules."

Use:

- `AGENTS.md` when repo-level guidance is enough;
- one Codex or Claude Code skill when you need one reusable capability;
- OpenSpec, Spec Kit, Kiro, or similar tools when the main problem is organizing requirements and spec facts.

Use Forma when the repeated problem is the agent's whole work loop:

- what it must clarify;
- what it must read;
- how it turns evidence into a plan;
- when execution is allowed;
- which validation proves the result;
- when continuation must stop.

---

## First Successful Run

The quickest useful demo is concrete:

1. Choose a small sample profile.
2. Generate a Codex or Claude Code workflow bundle.
3. Verify the generated bundle.
4. Install it into the selected agent's skill directory.
5. Trigger one plan-first task.
6. Inspect the plan, task contract, validation result, and run evidence.
7. Adjust the profile only after the workflow proves useful.

The samples in this repository support that path:

- `examples/profiles/sample-software/` shows a generic software plan-first workflow.
- `examples/profiles/sample-backend/` shows a Spec/issue-driven backend workflow with source reading, planning, validation, and execution boundaries.
- `examples/generated/*-codex/` and `examples/generated/*-claude-code/` show emitted target-specific skills.

Do not begin by designing a perfect profile. Generate one small workflow, run it on one planned task, then promote only useful rules into durable profile source.

---

## Who Is It For?

Forma is mainly for teams and individuals who already use AI agents for recurring work and want that work to follow a stable process.

The first obvious fit is software work:

- individual AI coding power users preserving their own habits;
- engineering teams encoding Spec-first, review, testing, migration, generated-baseline, and API-boundary rules;
- engineering productivity and platform teams productizing agent usage through installable bundles;
- tech leads and reviewers requiring plans, evidence, and validation paths before implementation;
- product managers and Spec owners keeping agents inside demand boundaries.

Forma can also be useful outside software when work has a repeatable shape:

- a clear objective or spec-like input;
- sources that must be read first;
- boundaries that matter;
- distinct stages;
- validation or acceptance;
- proof needs for reviewers.

Examples include research, analysis, publishing, design review, customer handoff, governance, and operations work.

This does not mean every task needs Forma. If the work has no stable sources, no meaningful boundaries, no acceptance path, and no need for reuse, a direct prompt is faster.

---

## Beyond Software Example

A research team could use Forma to generate a workflow where:

- `shape` clarifies the research question, audience, scope, and citation standard;
- `gauge` reads only approved source folders, notes, datasets, and prior memos;
- `seal` writes an outline with acceptance criteria, source coverage, and caveats;
- `pour` drafts one accepted section and records which sources support each claim;
- `flow` continues only while the outline, source limits, and review rules still hold.

The generated skills would not make the agent a better researcher by magic. They would make the team's research discipline explicit enough to reuse, review, and improve.

---

## Spec-Driven Tools And Forma

OpenSpec, Spec Kit, Kiro, and other SDD workflows make the spec layer more explicit.

They usually focus on requirements, proposals, design, deltas, task lists, and alignment between spec and implementation.

Forma does not replace those artifacts or consume them as its primary generator input. It generates the workflow agents use to read, organize, and act on those artifacts with project rules in place.

```text
Spec-driven tools organize demand and facts.
Forma organizes agent workflow around those facts.
```

Forma can work alone or beside a spec-oriented toolchain.

---

## Generic Skill Creators And Forma

Generic skill creators create capabilities.

For example:

```text
Create a skill that reviews API changes.
Create a skill that writes release notes.
Create a skill that audits security risk.
```

Forma is workflow-oriented. It generates the way a project expects agents to move through work:

```text
shape -> gauge -> seal -> pour -> flow
```

The difference is ownership:

- a generic skill belongs to a capability;
- a Forma-generated bundle belongs to a project workflow;
- a generic skill explains how to perform an action;
- a Forma-generated bundle explains how work is planned, evidenced, bounded, executed, and proven.

---

## AGENTS.md And Forma

`AGENTS.md` is a repo-level instruction surface.

It is good for:

- repository entry rules;
- files agents should read first;
- repository boundaries;
- default commands;
- local checkout-specific notes.

Forma does not replace `AGENTS.md`.

Forma is for reusable, classifiable rules that should enter workflow stages.

For example, `AGENTS.md` might say:

```text
Migration work must inspect schema files, generated baselines, and run migration validation.
```

Inside Forma, the same policy can become staged workflow structure:

- `shape`: identify whether the task selects the migration route;
- `gauge`: gather schema and baseline evidence;
- `seal`: write migration validation into the task contract;
- `pour`: run validation while executing the accepted task;
- `flow`: stop if the migration route is not safe for automatic continuation.

`AGENTS.md` lets an agent read a rule. Forma lets the rule enter the workflow.

---

## Profile

A profile is maintainable workflow source, not a prompt dump.

It records durable rules:

- authoritative spec sources;
- planning evidence requirements;
- validation gates;
- stage-specific constraints;
- conditional overlays;
- generated skill references;
- explicit source adapters.

Profiles should be reviewed and maintained by people.

---

## Temporary Injection

Temporary injection is the one-off rule path.

Use it for:

- special constraints needed for one generation;
- rules not stable enough for a profile;
- private source readers;
- one-off validation gates;
- scoped user instructions given during a generation session.

Temporary injection should not directly copy README, AGENTS, issue text, or large project documents. It should be classified first, then written as JSON.

---

## Stage Constraints

Not every rule should be global.

Forma places rules into workflow stages:

- `shape`: demand clarification, scope, route, and plan strategy;
- `gauge`: grounding and evidence collection;
- `seal`: plan/task materialization and validation contracts;
- `pour`: single-task execution and proof;
- `flow`: automatic continuation boundaries.

This avoids pushing every rule into one prompt and making the agent classify everything at runtime.

---

## Generated Skill Quality

A generated skill should have one clear job.

If a skill's `SKILL.md` becomes a large policy document, move stable detail into `references/`, move route-specific rules into conditional overlays, or split capability-specific guidance into a separate skill.

Good generated suites usually have:

- short, decisive skill descriptions;
- stage-specific instructions rather than one global rule pile;
- shallow references that load only when needed;
- scripts and source adapters only when a profile or temporary injection owns them;
- light `constraints.default`;
- one visible validation or proof path for the work the stage performs.

The generator should not merely paste every rule into every skill.

---

## Conditional Overlays

Some rules apply only in specific scenarios.

Examples:

- docs-only;
- backend;
- migration;
- generated-baseline;
- governance;
- cross-layer.

Those rules belong in conditional overlays, not default constraints.

The default layer should stay light. Heavy rules should activate by stage or scenario.

---

## Source Adapters

Source adapters are explicit source readers or helpers.

Examples:

- issue tracker readers;
- document exporters;
- private knowledge helpers;
- local source lookup scripts.

They are not Forma base capability. A generated bundle should use them only when a profile or temporary injection explicitly owns them.
