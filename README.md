# Forma

**A compiler for project-specific agent workflows.**

Profile in. Skill bundle out. Plan-First by default.

Forma compiles project-specific workflow profiles into skill bundles for agent
coding surfaces such as Codex and Claude Code.

It ships with a Plan-First engineering methodology: clarify the demand, gather
evidence, seal a plan, execute one task at a time, and continue only within
explicit boundaries.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

## Why Forma Exists

Agents can move fast. The hard part is steering the work after the first
prompt.

AI coding changed what counts as a project artifact.

Code, tests, docs, issues, and review comments still matter. But once coding
agents enter the development loop, another artifact becomes critical:

> the workflow an agent follows before and while it changes code.

Teams need to define what an agent must clarify, what evidence it must gather,
when a plan becomes executable, what it may change, when it must stop, and how
validation proof is recorded.

Those rules often live in scattered prompts, `AGENTS.md`, custom skills, review
habits, and team memory. Forma gives them a source format and a compiler.

The bet behind Forma is simple: agents behave better when workflow rules are
not only remembered in chat.

Put the workflow in files. Give it stages. Make proof part of the loop.

That is not a magic guarantee. It is a better control surface.

## Mental Model

```text
workflow profile  ->  Forma compiler  ->  skill bundle
source                compiler            installable artifact
```

Forma compiles:

```text
profile YAML
+ canonical methodology
+ target adapter
+ optional temporary injection
        |
        v
target-specific skill bundle
+ coordinated stage skills
+ references and scripts
+ .forma-manifest.json provenance
+ verifier-compatible structure
```

The same workflow profile can be emitted for different agent environments
instead of being rewritten manually for each tool.

## The Workflow

A typical Forma-generated bundle contains five coordinated stages:

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

| Stage | Plain English | What it does |
|---|---|---|
| `shape` | Clarify the request | Turn a loose request into a bounded proposal. |
| `gauge` | Read before acting | Gather repository, spec, docs, and related evidence before planning. |
| `seal` | Lock the plan | Convert the proposal into an accepted task contract. |
| `pour` | Execute within bounds | Implement one accepted task and record proof. |
| `flow` | Continue safely | Resume from the sealed plan, or stop when proof is missing. |

Not into the `shape` / `gauge` / `seal` / `pour` / `flow` names? Fine. They
are defaults, not doctrine. Projects can rename generated skills while
preserving the underlying stage semantics; see
[Usage: Rename Generated Skills](./docs/usage.md#rename-generated-skills).

## What Forma Adds

Spec docs, planning templates, static skills, and repository instructions can
help an agent understand demand.

Forma adds a narrower control surface:

- a workflow source format: profiles;
- a compiled artifact: skill bundles;
- a review surface: manifests, stages, validation points, and proof.

The result is an installable work loop, not just another plan document.

## Where Forma Fits

Forma is not another prompt template and not another spec tool. It sits at the
agent-workflow layer.

- Spec tools and planning docs define what should be built.
- `AGENTS.md` and repository docs define local context and conventions.
- Generic skill creators package reusable capabilities.
- Forma compiles project-specific workflow rules into deployable skill bundles.

Forma does not replace those layers; it makes agents move through them in a
disciplined order.

## When To Use It

Use Forma when the hard part is not a single edit, draft, or analysis, but the
way that kind of work should happen every time.

The first fit is AI coding: specs, repository evidence, plans, accepted tasks,
validation, and review proof. But the pattern is broader. Forma can fit any
repeatable agent workflow where sources, boundaries, stages, approval, and proof
matter.

If you only need the agent to fix a typo, summarize a page, or remember a few
repository rules, Forma is too much machinery. Use `AGENTS.md`, a direct prompt,
a single custom skill, or a spec tool for those cases.

For the full fit and mental model, read [Concepts](./docs/concepts.md).

## Try It

With `forma` available on `PATH`, generate and verify a Codex workflow bundle:

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

Build a target-fixed `forma-creator`:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma verify /tmp/forma-creator-dist/codex/forma-creator
```

Committed generated examples are drift baselines, not proof of runtime agent
behavior.

For the complete first-run path, install locations, Claude Code output, and
profile authoring details, see [Quick Start](./docs/quick-start.md).

## Two Ways To Start

**Generate from a tracked profile.** Use this for durable team or project rules
that have been reviewed and committed as source.

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
```

**Use `forma-creator`.** Use this for reviewed one-off workflow ideas. The
installed creator helps turn reviewed natural-language workflow ideas into
temporary injection JSON, then generates and verifies a target-specific bundle
before handoff.

Not ready to design a full profile? Try the workflow first. Promote only the
rules that survive real use.

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

Ask Forma for profile or temporary-injection authoring guidance when an external
agent needs rules without reading this source tree:

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

## Documentation

- Start: [Quick Start](./docs/quick-start.md), [Examples](./docs/examples.md).
- Understand: [Concepts](./docs/concepts.md), [Workflow Contract](./docs/workflow-contract.md), [Skill Bundle](./docs/skill-bundle.md).
- Reference: [Profile Schema](./docs/profile-schema.md), [Forma Creator](./docs/forma-creator.md), [Verifier](./docs/verifier.md), [Targets](./docs/targets.md), [Usage](./docs/usage.md).
- [STRUCTURE.md](./STRUCTURE.md): current source tree and ownership boundaries.

## Forma On Forma

Forma compiles the workflow it uses to build Forma.

The self profiles behind that loop live in:

- [profiles/forma-self/forma-self-iteration.yaml](./profiles/forma-self/forma-self-iteration.yaml)
- [profiles/forma-self/base.yaml](./profiles/forma-self/base.yaml)
- [profiles/forma-self/iteration-overlays.yaml](./profiles/forma-self/iteration-overlays.yaml)
- [profiles/forma-self/project.yaml](./profiles/forma-self/project.yaml)

## License

Apache-2.0 - see [LICENSE](./LICENSE).
