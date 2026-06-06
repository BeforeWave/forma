# Forma

Build project-specific Spec Plan-First agent workflows for teams and repos.

Forma is a Python CLI and creator-skill source for turning a project's specs
and reusable engineering constraints into installable Codex or Claude Code
agent workflows. It does not replace PRDs, issues, or OpenSpec changes. It
uses those demand sources as the spec layer, injects project-owned constraints
on top, and generates a plan-first workflow that must validate those
constraints before implementation.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

## Project Model

Forma builds one thing: a project-specific Spec Plan-First agent workflow.

That workflow is compiled from four inputs:

- **Spec source**: PRDs, GitHub issues, OpenSpec changes, design notes, or task
  plans that define what should be built.
- **Plan-first methodology**: the canonical workflow under
  `source/methodology/`.
- **Project profile**: human-maintained YAML and references that define how
  this team or repo expects agents to plan, gather evidence, validate, and
  execute.
- **Agent target**: Codex or Claude Code.

The output is an installable five-skill suite plus a manifest and verifier
rules. Each skill maps to a concrete engineering action:

- `shape`: turn a demand source into a bounded proposal. It clarifies goal,
  scope, source of truth, unresolved decisions, and selected project-constraint
  route.
- `gauge`: inspect the repo and source materials without changing code. It
  gathers the evidence needed to know what actually constrains the work.
- `seal`: write the final `plan.md` and `tasks.md`. It checks demand coverage,
  injected project constraints, acceptance criteria, task boundaries, and
  validation paths.
- `pour`: execute exactly one accepted task from the sealed plan, update task
  evidence, and run validation.
- `flow`: continue through remaining accepted tasks only when the sealed plan
  allows automatic execution.

## Why This Exists

Specs define the requested change. They usually do not encode every stable
engineering rule a project expects agents to follow.

Project rules often live across README files, AGENTS instructions, validation
scripts, team habits, private source readers, and previous planning decisions.
If those rules stay as loose prompt text, every agent can interpret the same
spec differently.

Forma makes those reusable rules explicit:

- put durable project rules in a reviewed profile;
- classify one-off rules into a temporary injection;
- route heavy rules through conditional overlays;
- inject optional source readers only when a profile or injection owns them;
- make planning and finalization prove that the selected constraints are
  reflected in the sealed plan.

The core value is not a nicer prompt. The core value is a stable plan-first
workflow that turns spec + project constraints into validated execution.

## Profiles Are Human Source

A Forma profile is meant to be maintained by people. Agents can help draft or
revise it for a repo, but the result should still be a readable, reviewable
source file owned by that project.

A profile can define:

- which demand sources are authoritative;
- which repository evidence must be read;
- which validation commands prove work;
- which rules apply during planning, grounding, plan finalization, task
  execution, or automatic execution;
- which conditional routes exist for docs-only, governance, migration,
  generated-baseline, backend, frontend, or cross-layer work;
- which references or scripts are copied into generated skills.

Forma exposes profile authoring guidance through the CLI so an agent can help
write a profile without inspecting this repository:

```bash
uv run --extra dev forma explain profile --target codex
```

## Injection Paths

Forma supports multiple ways to add project rules because rules have different
lifetimes.

**Tracked profile**: durable workflow source for a team, repo, or workflow.
Use this for repeated behavior that should be reviewed and maintained.

**Temporary injection**: one-off JSON used by an installed `forma-creator` when
the user gives natural-language constraints for a single generated suite. The
agent must show the injection path and a classification table before
generation.

**Stage constraints**: targeted rules for one lifecycle stage, such as
planning-only rules for `shape`, read-only grounding rules for `gauge`, or
execution rules for `pour`.

**Conditional overlays**: route-specific constraints that apply only after
`shape` records the chosen scenario in `plan.md`. Use this for expensive or
specialized project behavior.

**Source adapters**: explicit helper scripts or references for loading demand
or evidence from issue trackers, document exporters, private knowledge tools,
or other local sources. They are injected by profile or temporary injection,
not assumed as base capability.

Temporary injection follows the same classification principle:

```bash
uv run --extra dev forma explain temporary-injection --format json --target codex
```

## Command Flow

Generate a Codex workflow from a reviewed profile:

```bash
uv run --extra dev forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
```

Verify the generated workflow:

```bash
uv run --extra dev forma verify /tmp/backend-plan-first-codex
```

Install it into Codex:

```bash
mkdir -p ~/.codex/skills
cp -R /tmp/backend-plan-first-codex/* ~/.codex/skills/
```

Generate the same profile for Claude Code:

```bash
uv run --extra dev forma create \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-claude-code

uv run --extra dev forma verify /tmp/backend-plan-first-claude-code
```

## Creator Skill

Forma can also build a target-fixed `forma-creator` skill. That installed
creator lets an agent convert reviewed natural-language constraints into a
temporary injection, generate a project-specific workflow, and verify the
suite before reporting success.

```bash
uv run --extra dev forma build-creator \
  --output /tmp/forma-creator-dist \
  --target codex

uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator
```

The creator bundle carries its own methodology resources and verifier. A
downstream project does not need the developer `forma` package installed for
agent-side verification.

## Repository Facts

- `source/methodology/`: canonical plan-first methodology used to emit
  `shape`, `gauge`, `seal`, `pour`, and `flow`.
- `source/skill-creator/`: Layer 1 `forma-creator` source, bundled references,
  standalone creator script, and verifier.
- `src/forma/`: developer CLI, profile compiler, runtime asset resolver, and
  target-specific emitters.
- `profiles/forma-self/`: Forma's own human-maintained profile for iterating
  on this repository.
- `examples/profiles/`: sanitized profile examples.
- `examples/generated/`: committed generated baselines used as drift checks.
- `tests/`: verifier, profile, creator, runtime asset, and generated-baseline
  tests.

Detailed source layout lives in [STRUCTURE.md](./STRUCTURE.md).

## Relationship To Spec Tools

Use spec tools to preserve the requested change. Use Forma to preserve how the
agent must turn that spec into a constrained, evidence-backed plan and
execution.

- OpenSpec, PRDs, and issues own demand.
- Forma profiles own project workflow constraints.
- Generated Forma skills own the agent behavior that connects the two.

## Repository Checks

```bash
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
uv run --extra dev pytest -p no:cacheprovider tests/
```

## License

MIT - see [LICENSE](./LICENSE).
