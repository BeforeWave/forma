# Forma Creator

Chinese version: [forma-creator.zh-CN.md](./forma-creator.zh-CN.md)

`forma-creator` is the generation entrypoint installed for an agent. It lets the
agent extract engineering rules from project docs, code, tests, and conventions,
then generate a Forma workflow you can try before the team writes a durable
profile.

The shortest use is to tell the agent:

```text
Use forma-creator to customize a workflow for this project.
Read the docs and code, extract the engineering rules, show them to me first;
after I confirm, generate the workflow and install it from the hints.
```

Users do not need to write JSON. The creator makes the agent clarify the rules
that matter most: authoritative sources, change boundaries, required tools,
validation depth, proof location, and stop conditions. After the user confirms
them, those rules enter the generated workflow output for this run.

## How It Differs From Other Paths

| Path | Best for | Input | Output |
|---|---|---|---|
| `forma-creator` | On-the-spot customization; try a project workflow first. | Project facts, user additions, confirmed rules. | Verified one-off skill bundle or plugin. |
| `forma explain profile` + agent | Durable source from the start. | Profile authoring standard, project facts, team review. | Tracked profile YAML, then compiled workflow. |
| `forma create-bundle` / `forma create-plugin` | A reviewed profile already exists. | Tracked profile YAML. | Repeatable workflow bundle or plugin. |

`forma-creator` is the "try first" path. Rules that keep proving useful and win
team agreement can be promoted into a profile. `forma explain profile` is the
"make it durable first" path. `forma create-bundle` and `forma create-plugin`
are deterministic build commands after a profile exists.

## Fixed Target Contract

Each creator is built for one target:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target claude-code --output /tmp/forma-creator-dist
```

A Codex creator generates Codex-shaped skill bundles and Codex plugin output
when the user asks for it. A Claude Code creator generates Claude Code-shaped
skill bundles and Claude Code plugin output. Do not use a creator built for one
target to generate another target's output.

The creator reports generated output paths, verification results, and install
hints. It does not directly write the generated output into Codex or Claude Code
skill roots for the user.

## What Temporary Injection Is

In the creator path, temporary injection is the internal carrier that passes
on-the-spot rules into the generator. Users usually do not need to write it or
understand it first.

Normal lifecycle:

1. The user asks the agent to customize a workflow with `forma-creator`.
2. The agent reads project docs, code, tests, and existing conventions.
3. The agent extracts engineering rules and asks the user to confirm or add to them.
4. The creator classifies the confirmed rules and writes temporary injection.
5. The creator generates the skill bundle or plugin allowed by the fixed target.
6. The creator runs the bundled verifier.
7. The user or agent installs the verified output from the hints and tries it.
8. Repeated, useful, team-approved rules can be promoted into a tracked profile.

Temporary injection belongs only to the generated workflow output for this run.
It becomes tracked profile source only if the user explicitly promotes it.

## Classification Rules

The creator places confirmed rules in the narrowest correct location:

Temporary injection maps always use internal stage keys (`shape`, `gauge`,
`seal`, `pour`, `flow`), not generated public skill ids such as `forma-plan`.

| Target | Use for |
|---|---|
| `constraints.default` | Minimal always-true bottom lines. |
| `constraints.shape` | Demand clarification, route selection, scope, and unresolved decisions. |
| `constraints.gauge` | Read-only evidence collection. |
| `constraints.seal` | Plan and task materialization, including task boundaries, validation gates, and proof requirements. |
| `constraints.pour` | Current-task execution, validation gates, and proof. |
| `constraints.flow` | Continuation conditions and stop conditions. |
| `conditional_overlays` | Scenario rules such as docs-only, migration, generated-baseline, governance, backend, or cross-layer work. |
| `resources` | References, scripts, or support files explicitly selected by the workflow. |

Do not copy README, AGENTS, issue text, or governance docs wholesale into
temporary injection. Extract rules and place them where they belong.

## Source Adapters

If the generated workflow should fetch planning context from an issue tracker,
document exporter, private source helper, or local script, classify that as a
source adapter.

Source adapters are not base Forma capability. Add them only when a profile or
temporary injection explicitly selects them.

## Promotion To Profile

Promote a creator rule into a tracked profile when it is:

- useful across multiple runs;
- reviewed by the project owner or team;
- safe to share as durable source;
- specific enough to place in a stage constraint, resource, validation command, or conditional overlay.

Do not promote rules that are private, experimental, one-off, or based on
temporary local paths.

## Verification

`forma-creator` should run verification before reporting success. Verification
checks generated output structure and methodology rules, but it does not prove
that the on-the-spot rules are good project decisions.

See [Verifier](./verifier.md) for the boundary.

## Related Docs

- [Quick Start](./quick-start.md): run creator first, then promote durable rules.
- [Profile Schema](./profile-schema.md): durable profile source format.
- [Targets](./targets.md): Codex and Claude Code install behavior.
- [Verifier](./verifier.md): what verification checks.
