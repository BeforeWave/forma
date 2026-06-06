# Forma

**Turn your spec discipline into reusable agent workflows.**

Forma turns project-specific planning rules, evidence requirements, validation gates, and execution boundaries into installable Spec Plan-First workflow skills for Codex and Claude Code.

It is for teams and power users who already ask agents to work from specs, plans, evidence, and validation instead of one-off prompts.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

## The Shift

After AI coding, code is no longer the only first-class project artifact.

The spec an agent executes, the workflow it follows, the evidence it reads, the plan it seals, and the proof it leaves behind all become part of the project lifecycle.

Teams used to express style through code style, architecture patterns, and review habits. Now they also express style through how agents work: what to read first, how to plan, when to stop, how to validate, and how to leave proof.

Different SDD methods, planning rituals, validation expectations, and workflow constraints become a new kind of team style.

Forma gives that style shape.

## What Forma Is

Forma is a generator, not the runtime workflow itself.

It composes project-owned workflow rules, plan-first methodology, target agent surfaces, and optional one-off generation constraints into project-specific Spec Plan-First workflow bundles.

```text
Forma composes:
  project profile: reusable workflow rules and constraints
  methodology: plan-first stages, gates, and proof requirements
  target surface: Codex or Claude Code
  optional temporary injection: one-off generation constraints

into:
  installable, target-specific workflow skills
```

Those generated skills then guide agents as they read PRDs, issues, specs, task plans, briefs, repository evidence, and validation results.

It is not about writing one more prompt. It is about placing rules in the right location: default constraints, stage constraints, conditional overlays, resources, and source adapters.

## What Forma Generates

The Forma-generated bundle is the workflow an agent actually uses.

After installation into Codex or Claude Code, it usually consists of five coordinated skills:

```text
shape -> gauge -> seal -> pour -> flow
```

- `shape`: turn demand into a bounded proposal;
- `gauge`: gather repo, spec, docs, and history evidence read-only;
- `seal`: turn the plan and tasks into a reviewable, verifiable execution contract;
- `pour`: execute one accepted task and record proof;
- `flow`: continue only when the sealed plan allows it.

These skills are not scattered prompts. They are the project's own agent work loop.

Not into those names? Fine. Forma lets a project rename generated skills; see [Usage: Rename Generated Skills](./docs/usage.md#rename-generated-skills).

## Why It Matters

Forma makes agent work:

- **repeatable**: project rules have a location and lifecycle, not just a context window;
- **staged**: clarify, ground, seal, execute, and prove are not collapsed together;
- **bounded**: execution stays inside accepted tasks instead of drifting with convenience;
- **reviewable**: reviewers see how the agent moved from spec to implementation, not only the diff;
- **portable**: the same workflow style can be generated for different agent surfaces.

## Who Is It For? Software Teams, And Beyond

Software teams are Forma's most natural starting point. You may need Forma if AI coding is already a normal development mode for you and these problems keep repeating:

- the same spec leads different agents to read different sources and miss different validations;
- your team has SDD, planning, and validation habits scattered across docs, prompts, and past decisions;
- the repo has multiple work routes: backend, migration, generated-baseline, docs-only, governance, cross-layer;
- you want agents to produce a reviewable plan before implementation;
- you want Codex, Claude Code, or another agent surface to follow the same workflow.

If you only ask agents to edit small files occasionally, `AGENTS.md`, a prompt, or one custom skill is often enough.

Forma is not software-only: if the work depends on what to read, how to plan, who approves, and what proof remains, the same workflow pattern may fit. See [Concepts: Beyond Software](./docs/concepts.md#beyond-software) for the work pattern and [How Different People Use Forma](./docs/concepts.md#how-different-people-use-forma) for role-specific examples.

Forma is for people who want to make their way of working reusable and reviewable.

## Where Forma Sits

Forma is not the same category as spec-driven tools like OpenSpec, Spec Kit, or Kiro. Those tools organize demand and facts. Forma generates the workflow agents follow when they read, organize, and act on that material.

Forma is not a generic skill creator like Codex `skill-creator` or Claude Code Skill Creator. Those tools create capabilities; Forma creates project workflow.

Forma does not replace `AGENTS.md`. `AGENTS.md` lets an agent read rules; Forma lets reusable rules enter staged workflow.

```text
Spec tools organize demand.
Generic skill creators create capabilities.
AGENTS.md gives repo-level guidance.
Forma turns your spec discipline into reusable agent workflows.
```

## Documentation

- [Quick Start](./docs/quick-start.md): install, generate workflow, and build `forma-creator`.
- [Concepts](./docs/concepts.md): core concepts, ecosystem comparison, profiles, and injection paths.
- [Usage](./docs/usage.md): command reference, repository checks, and installed CLI behavior.
- [STRUCTURE.md](./STRUCTURE.md): current source tree and ownership boundaries.

## Two Ways To Start

### Ask an agent to draft a profile

To turn a project's durable workflow rules into source, tell an agent inside that project:

```text
Run:
  forma explain profile --target codex

Use that output as the profile authoring standard.
Inspect this repository and propose a tracked Forma profile for it.

Find:
- authoritative demand sources;
- planning and grounding expectations;
- validation commands and proof requirements;
- stage-specific constraints;
- recurring work routes and overlays;
- source adapters or helper scripts that should be explicit.

Do not write files yet.
Show the proposed profile structure, explain each constraint placement,
and mark unknowns that need human confirmation.
```

Use this path to turn real team habits into a durable profile.

### Use `forma-creator` to try workflow ideas fast

Do not want to design a full profile first? Install the target-specific `forma-creator`, then throw workflow ideas at the agent:

```text
Use forma-creator to turn these workflow ideas into a Plan-First bundle for this repo.

Rules I want to try:
- identify the real source of truth before planning;
- read only evidence needed for the chosen scope;
- put acceptance and validation into every task;
- execute one accepted task at a time;
- stop before API, database, generated-baseline, or cross-layer work unless the plan explicitly says to continue.

Before generating, show how you classified these rules.
After generating, verify the bundle.
```

Use this path to test the feel quickly. Promote rules that stick into a tracked profile.

## Try It

With `forma` available on `PATH`, generate and verify a workflow bundle:

```bash
forma --help
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
forma verify /tmp/backend-plan-first-codex
```

Build a target-fixed `forma-creator`:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

For install paths, Claude Code output, and profile authoring details, see [Quick Start](./docs/quick-start.md).

## Forma On Forma

Btw: Forma is planned and developed through workflows generated by Forma itself. The self profiles behind that loop live in:

- [profiles/forma-self/forma-self-iteration.yaml](./profiles/forma-self/forma-self-iteration.yaml)
- [profiles/forma-self/base.yaml](./profiles/forma-self/base.yaml)
- [profiles/forma-self/iteration-overlays.yaml](./profiles/forma-self/iteration-overlays.yaml)
- [profiles/forma-self/project.yaml](./profiles/forma-self/project.yaml)

## License

Apache-2.0 - see [LICENSE](./LICENSE).
