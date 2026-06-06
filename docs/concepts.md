# Concepts

Chinese version: [concepts.zh-CN.md](./concepts.zh-CN.md)

## Forma's Layers

There are three layers to keep separate.

**Forma itself**

Forma is the generator, creator, and toolchain. It reads profiles, methodology, and target surfaces to generate workflow bundles.

**Forma-generated bundle**

This is the actual workflow skill bundle installed into Codex or Claude Code. It constrains how the agent works.

**Profile / temporary injection**

This is the input layer for project rules. Durable rules live in tracked profiles. One-off rules live in temporary injection.

These layers should not be collapsed.

Forma does not directly execute project tasks. Forma generates the workflow agents follow when executing tasks.

## What Forma Generates

Forma-generated output is the workflow an agent actually uses after
installation into Codex or Claude Code. A normal bundle has five coordinated
skills:

| Forma stage | Current meaning | Plainer user-facing name |
|---|---|---|
| `shape` | bounded proposal | Plan Issue / clarify the demand |
| `gauge` | read-only evidence | Ground Plan / understand the current state |
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
five target-specific skills
+ references
+ scripts
+ manifest
+ verifier-compatible structure
```

The `shape` / `gauge` / `seal` / `pour` / `flow` names are the Forma stage
metaphor. Projects can rename the installable skill directories and display
labels to match their own language while preserving the stage semantics.

## Why It Matters

Forma makes agent work:

- **repeatable**: project rules have a location and lifecycle, not just a
  context window;
- **staged**: clarify, gather evidence, seal a plan, execute, and prove are not
  collapsed into one prompt;
- **bounded**: implementation stays inside accepted tasks instead of expanding
  with convenience;
- **reviewable**: reviewers can inspect the path from spec to plan to proof, not
  only the final diff;
- **portable**: the same workflow style can be emitted for different agent
  surfaces.

The main value is not that Forma writes code. It does not. The value is that it
turns a team's repeated AI-working discipline into versioned, installable,
verifiable workflow source.

## Core Assets

Forma is useful because the workflow is represented as source, not memory.

**Profiles** record durable project rules: source-of-truth expectations,
validation commands, stage constraints, conditional routes, and explicit source
adapters. They are reviewed and maintained like other project artifacts.

**Manifests** make generated bundles auditable. `.forma-manifest.json` records
the target, methodology version or digest, resolved profile stack, profile file
hashes, generated skills, and generator provenance.

**Verification** keeps the output from being just generated markdown. `forma
verify` checks structural and methodology contracts for both `forma-creator`
bundles and generated plan-first suites.

## When Not To Use Forma

Forma is deliberately heavier than a repository instruction file or a single
custom skill. Do not start with Forma if the problem is just "make this agent
remember a few rules."

Use `AGENTS.md` when repo-level guidance is enough. Use one Codex or Claude Code
skill when you need one reusable capability. Use OpenSpec, Spec Kit, Kiro, or
similar tools when the main problem is organizing requirements and spec facts.

Use Forma when the repeated problem is the agent's whole work loop: what it must
clarify, what it must read, how it turns evidence into a plan, when execution is
allowed, which validation proves the result, and where that proof is left.

## First Successful Run

The quickest useful demo is concrete:

1. Choose a sample profile.
2. Generate a Codex or Claude Code workflow bundle.
3. Verify the generated bundle.
4. Install it into the selected agent's skill directory.
5. Trigger one plan-first task.
6. Inspect the plan, task contract, validation, and run evidence.
7. Adjust the profile only after the workflow proves useful.

The samples in this repo are meant to support that path:

- `examples/profiles/sample-software/` shows a generic software plan-first
  workflow with Chinese collaboration, impact boundaries, grounding, validation,
  and safe continuation gates.
- `examples/profiles/sample-backend/` shows a Spec/issue-driven backend workflow
  with explicit source-reading, planning, validation, and execution boundaries.
- `examples/generated/*-codex/` and `examples/generated/*-claude-code/` show the
  same workflow style emitted as target-specific skills for Codex and Claude
  Code.

Do not begin by designing a perfect profile. Generate one small workflow, run it
on one planned task, then promote only the rules that prove useful into durable
profile source.

## Who Is It For? Software Teams, And Beyond

Forma is not for every agent use case.

You probably do not need Forma when:

- you only ask an agent to edit small files occasionally;
- the repository has few rules and `AGENTS.md` is enough;
- planning, validation, and proof do not need to become stable workflow;
- human review is the only durable control surface.

Software teams are the first obvious fit, especially when:

- the team already uses PRDs, issues, OpenSpec, Spec Kit, Kiro, or other SDD artifacts to drive development;
- different work types have different rules, such as backend, migration, generated-baseline, docs-only, governance, or cross-layer work;
- agents must read repository evidence before implementation;
- validation gates matter to project quality;
- you need stable plan-first handoffs;
- the same workflow should be installable across agent surfaces;
- an individual or team already has AI coding discipline and wants to turn it into maintainable source.

The first users will likely be software teams: engineering teams, tech leads, engineering productivity groups, platform teams, and AI coding power users.

But Forma is not only for them. If you are no longer asking an agent for a small favor and are instead asking it to follow a repeatable way of working, Forma is worth a look. The next section shows what that looks like for different roles.

## How Different People Use Forma

Different people do not need the same workflow. Forma is not just "five skills for developers." It is a way to turn repeated working discipline into reusable agent workflow.

- **Individual AI coding power users** use Forma to preserve their own habits: read the issue and latest plan first, surface risks, change one task at a time, and do not report done before validation passes.
- **Engineering teams** encode their Spec-first, review, testing, migration, generated-baseline, and API-boundary rules into a profile so different agents and surfaces follow the same rhythm.
- **Engineering productivity and platform teams** productize agent usage. Instead of publishing best-practice docs, they ship installable, verifiable, iteratable workflow bundles.
- **Tech leads and reviewers** require agents to present plans, evidence, and validation paths before implementation. Reviewers see why the agent read certain sources and why the scope stayed bounded.
- **Product managers and Spec owners** make PRDs, issues, OpenSpec changes, design notes, and acceptance criteria the source of truth for agent planning. The point is not only implementation; it is keeping agents inside demand boundaries.
- **Data and business analysts** require agents to confirm metric definitions, data sources, time windows, and sample limits before producing reports, charts, and caveats.
- **Researchers** encode research questions, source priority, citation rules, fact/inference boundaries, and counterexample checks so conclusions have a visible path.
- **Content, brand, and publishing teams** make agents read the brief, audience, voice, banned language, and citation requirements before drafting or editing.
- **Design and product experience teams** require agents to read PRDs, designs, user feedback, and component constraints before producing critique or revision plans.
- **Sales, customer success, and delivery teams** turn account facts, prior commitments, risks, approval points, and next steps into a handoff workflow. Agents can draft follow-up, but they cannot invent customer context.
- **Compliance, security, and governance teams** make agents identify applicable rules, evidence gaps, human approval points, and actions that must not be crossed. Forma matters here because it helps agents stop.
- **Operations and SRE teams** turn runbooks into staged workflows: confirm environment, blast radius, rollback path, execution window, and validation before taking action.

In short: if you have a durable answer to "I need the agent to work this way every time," Forma has a place to put it.

## Beyond Software

Forma starts from AI coding, but the underlying problem is broader: make an agent work from a clear objective, read the right sources first, plan before acting, move through stages, and leave reviewable proof.

This section is not another role list. The previous section covers people. This one covers the shape of work that is worth turning into a Forma workflow.

Forma is worth trying when the work has:

- a spec-like input: a brief, research question, report request, customer ask, policy constraint, or operations task;
- sources that must be read first: documents, meeting notes, spreadsheets, designs, CRM records, issues, or runbooks;
- boundaries that matter: metric definitions, brand rules, permissions, sensitive information, approval lines, or delivery scope;
- distinct stages: clarify, gather evidence, plan, execute, review;
- validation or acceptance: recalculation, citation checks, fact checks, human approval, or pre-publish checklists;
- proof needs: reviewers should see why the agent acted, not only the final artifact.

If the work has no stable sources, no meaningful boundaries, no acceptance path, and no need for reuse, Forma is probably too much. A direct prompt is faster.

If that feels too formal, you probably do not need Forma. If it sounds like the thing you keep re-explaining to every agent, Forma is the place to put it.

## Beyond Software Mini Example

A research team could use Forma to generate a workflow where:

- `shape` clarifies the research question, audience, scope, and citation standard;
- `gauge` reads only the approved source folders, notes, datasets, and prior memos;
- `seal` writes an outline with acceptance criteria, source coverage, and caveats;
- `pour` drafts one accepted section and records which sources support each claim;
- `flow` continues only while the outline, source limits, and review rules still hold.

The generated skills would not make the agent a better researcher by magic.
They would make the team's research discipline explicit enough to reuse,
review, and improve.

## Spec-Driven Tools And Forma

OpenSpec, Spec Kit, Kiro, and other SDD workflows make the spec layer more explicit.

They usually focus on:

- requirements;
- proposals;
- design;
- deltas;
- task lists;
- spec and implementation alignment.

Forma is not trying to replace those tools.

Forma does not replace those artifacts or consume them as the primary generator input. It generates the workflow agents use to read, organize, and act on those artifacts with the project's rules in place.

In short:

```text
Spec-driven tools organize demand and facts.
Forma organizes agent workflow around those facts.
```

That is why Forma can work alone or beside a spec-oriented toolchain. Existing PRDs, issues, proposals, design notes, or task lists can all become material that Forma-generated workflows require agents to read and respect.

## Generic Skill Creators And Forma

Generic skill creators create capabilities.

For example:

```text
Create a skill that reviews API changes.
Create a skill that writes release notes.
Create a skill that audits security risk.
```

Those skills are useful, but they are usually capability-oriented.

Forma is workflow-oriented. It generates the way a project expects agents to work around specs:

```text
shape -> gauge -> seal -> pour -> flow
```

The difference is not "one skill vs many skills." The difference is ownership:

- a generic skill belongs to a capability;
- a Forma-generated bundle belongs to a project workflow;
- a generic skill explains how to perform an action;
- a Forma-generated bundle explains how work is planned, evidenced, bounded, executed, and proven.

## AGENTS.md And Forma

`AGENTS.md` is a repo-level instruction surface.

It is good for:

- current repository entry rules;
- files agents should read first;
- repository boundaries;
- default commands;
- what not to touch;
- local checkout-specific notes.

Forma does not replace `AGENTS.md`.

Forma is for reusable, classifiable rules that should enter workflow stages.

The same rule is natural-language guidance in `AGENTS.md`. In Forma, it can become:

- a profile constraint;
- a stage constraint;
- a conditional overlay;
- a source adapter;
- a generated skill resource;
- a workflow contract the verifier can inspect.

For example, `AGENTS.md` might say:

```text
Migration work must inspect schema files, generated baselines, and run migration validation.
```

Inside `AGENTS.md`, that is a global instruction. The agent must decide when and how it applies.

Inside Forma, it can enter workflow structure:

- `shape`: identify whether the task selects the migration route;
- `gauge`: gather schema and baseline evidence read-only;
- `seal`: write migration validation into the task contract;
- `pour`: run the validation while executing the accepted task;
- `flow`: stop if the migration route is not safe for automatic continuation.

`AGENTS.md` lets an agent read a rule. Forma lets the rule enter the workflow.

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

Profiles should be reviewed and maintained by people. Agents can help draft them, but temporary ideas should not become durable profile source by accident.

## Temporary Injection

Temporary injection is the one-off rule path.

Use it for:

- special constraints needed for one generation;
- rules not stable enough for a profile;
- private source readers;
- one-off validation gates;
- scoped user instructions given during a generation session.

Temporary injection should not directly copy README, AGENTS, issue text, or large project documents. It should be classified first, then written as JSON.

## Stage Constraints

Not every rule should be global.

Forma places rules into workflow stages:

- `shape`: demand clarification, scope, route, and plan strategy;
- `gauge`: read-only grounding and evidence collection;
- `seal`: plan/task materialization and validation contracts;
- `pour`: single-task execution and proof;
- `flow`: automatic continuation boundaries.

This avoids pushing every rule into one prompt and making the agent classify everything at runtime.

## Generated Skill Quality

A generated skill should have one clear job. If a skill's `SKILL.md` becomes a
large policy document, move stable detail into `references/`, move route-specific
rules into conditional overlays, or split capability-specific guidance into a
separate skill.

Good generated suites usually have:

- short, decisive skill descriptions;
- stage-specific instructions rather than one global rule pile;
- shallow references that load only when needed;
- scripts and source adapters only when a profile or temporary injection owns
  them;
- light `constraints.default`;
- one visible validation path for the work the stage performs.

This is why Forma separates default constraints, stage constraints, conditional
overlays, resources, and source adapters. The generator should not merely paste
every rule into every skill.

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

## Source Adapters

Source adapters are explicit source readers or helpers.

Examples:

- issue tracker readers;
- document exporters;
- private knowledge helpers;
- local source lookup scripts.

They are not Forma base capability. A generated bundle should use them only when a profile or temporary injection explicitly owns them.
