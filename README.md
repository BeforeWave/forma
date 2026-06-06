# Forma

**A compiler for project-specific agent workflows.**

Forma turns workflow profiles into portable skill bundles for Codex and Claude
Code.

It gives coding agents a spine: how they clarify, gather evidence, plan,
execute, validate, and continue becomes explicit, versioned, portable, and
verifiable.

Forma is not the runtime agent. It is not a generic skill creator. It is not
another prompt template.

The profile is source. The generated skill bundle is the deployment artifact.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

## Why Forma Exists

AI coding changed what counts as a project artifact.

Code, tests, docs, issues, and review comments still matter. But once coding
agents enter the development loop, another artifact becomes critical:

> the workflow an agent follows before and while it changes code.

Teams need to define what an agent must clarify, what evidence it must gather,
when a plan becomes executable, what it may change, when it must stop, and how
validation proof is recorded.

Those rules often live in scattered prompts, `AGENTS.md`, custom skills, review
habits, and team memory. Forma gives them a source format and a compiler.

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

These names are defaults, not the product. Projects can rename generated skills
while preserving the underlying stage semantics; see
[Usage: Rename Generated Skills](./docs/usage.md#rename-generated-skills).

## What Forma Adds

Spec docs, planning templates, static skills, and repository instructions can
help an agent understand demand.

Forma does something narrower and stricter: it packages the workflow contract
itself.

It defines which evidence must be gathered before planning, when a plan becomes
executable, which task is currently accepted, what counts as validation proof,
and when continuation must stop.

The result is not just a better plan document. It is an installable work loop
that constrains how the agent moves from demand to evidence, from evidence to
plan, from plan to execution, and from execution to safe continuation.

## Where Forma Fits

Forma sits at the agent-workflow layer.

- Spec tools and planning docs define what should be built.
- `AGENTS.md` and repository docs define local context and conventions.
- Generic skill creators package reusable capabilities.
- Forma compiles project-specific workflow rules into deployable skill bundles.

Forma does not replace those layers; it makes agents move through them in a
disciplined order.

## When To Use It

Use Forma when AI coding is already a normal development mode and your team
needs the same planning, evidence, validation, and stop conditions to hold
across repeated agent runs.

You probably do not need Forma when the problem is a few repository rules, one
isolated reusable capability, or basic organization of requirements and spec
facts. Use `AGENTS.md`, a single custom skill, or a spec tool for those cases.

For the full methodology, fit, and ecosystem discussion, read
[Concepts](./docs/concepts.md).

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

- [Quick Start](./docs/quick-start.md): install, generate workflow, and build `forma-creator`.
- [Concepts](./docs/concepts.md): mental model, fit, ecosystem comparison, profiles, and injection paths.
- [Usage](./docs/usage.md): command reference, repository checks, and installed CLI behavior.
- [STRUCTURE.md](./STRUCTURE.md): current source tree and ownership boundaries.

## Forma On Forma

Forma is planned and developed through workflows generated by Forma itself. The
self profiles behind that loop live in:

- [profiles/forma-self/forma-self-iteration.yaml](./profiles/forma-self/forma-self-iteration.yaml)
- [profiles/forma-self/base.yaml](./profiles/forma-self/base.yaml)
- [profiles/forma-self/iteration-overlays.yaml](./profiles/forma-self/iteration-overlays.yaml)
- [profiles/forma-self/project.yaml](./profiles/forma-self/project.yaml)

## License

Apache-2.0 - see [LICENSE](./LICENSE).
