# Forma

**Give your coding agents a spine.**

Forma turns your team's engineering discipline - planning, evidence,
boundaries, and validation - into installable plan-first workflows for Codex and
Claude Code.

Agents read before acting, plan before touching code, stay inside accepted
tasks, and leave proof behind.

Not another prompt. Not another spec tool. A workflow compiler for serious
AI-assisted engineering.

Forma is a generator, not the runtime workflow itself. The generated bundle is
what Codex or Claude Code actually uses.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

## Why Forma Exists

AI coding is powerful, but without workflow it often collapses context,
planning, implementation, and validation into one improvised step.

That is where agents drift: they read whatever context is nearby, touch files
outside the task, expand scope by convenience, or claim validation without
proof.

Forma turns the engineering discipline your team already cares about -
planning, evidence, boundaries, validation, and review - into a reusable
workflow that agents can actually follow.

## The Workflow

Forma generates staged agent workflows:

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

Each stage has a job:

| Stage | Plain English | What it does |
|---|---|---|
| `shape` | Clarify the request | Turn a loose request into a bounded proposal. |
| `gauge` | Read before acting | Gather repository, spec, docs, and related evidence before planning. |
| `seal` | Lock the plan | Convert the proposal into an accepted task contract. |
| `pour` | Execute within bounds | Implement one accepted task without scope drift. |
| `flow` | Continue safely | Resume from the sealed plan, or stop when proof is missing. |

Not into those names? Fine. Forma lets a project rename generated skills; see
[Usage: Rename Generated Skills](./docs/usage.md#rename-generated-skills).

## What Forma Generates

Forma composes reusable profile source, the canonical plan-first methodology,
a target agent surface, and optional one-off generation constraints:

```text
profile YAML
+ canonical methodology
+ target = codex | claude-code
+ optional temporary injection
        |
        v
installable workflow bundle
+ five coordinated skills
+ references and scripts
+ .forma-manifest.json provenance
+ verifier-compatible structure
```

These generated skills are not scattered prompts. They are the project's agent
work loop: clarify, ground, seal, execute, and continue with proof.

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

## When To Use It

Use Forma when AI coding is already a normal development mode and your team
needs the same planning, evidence, validation, and stop conditions to hold
across repeated agent runs.

If the problem is a few repository rules, use `AGENTS.md`. If it is one reusable
capability, use a single custom skill. If the main problem is
organizing requirements and spec facts, use a spec tool such as OpenSpec, Spec
Kit, or Kiro.

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

## Where Forma Fits

Forma sits at the agent-workflow layer.

- Spec tools and planning docs define what should be built.
- `AGENTS.md` and repository docs define local context and conventions.
- Generic skill creators package reusable capabilities.
- Forma packages the project-specific workflow that tells the agent how to move
  through clarification, evidence, planning, execution, validation, and safe
  continuation.

Forma does not replace those layers; it makes agents move through them in a
disciplined order.

## Documentation

- [Quick Start](./docs/quick-start.md): install, generate workflow, and build `forma-creator`.
- [Concepts](./docs/concepts.md): methodology, fit, ecosystem comparison, profiles, and injection paths.
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
