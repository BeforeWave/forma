# Forma Creator

Chinese version: [forma-creator.zh-CN.md](./forma-creator.zh-CN.md)

`forma-creator` is Forma's agent-side workflow generation entrypoint.

Use it when a concrete project needs a workflow harness before you are ready to
write durable profile YAML. It helps an agent turn reviewed natural-language
project concerns into temporary injection JSON, generate a target-specific
workflow bundle or Codex plugin, and verify the output before handoff.

## How It Differs From `forma create-bundle`

| Path | Best for | Input | Output |
|---|---|---|---|
| `forma-creator` | Shape a project-specific workflow conversationally. | Reviewed natural-language concerns classified into temporary injection JSON. | Verified one-off harness for the fixed target. |
| `forma explain profile` + agent | Draft a durable profile conversationally. | CLI profile authoring guidance, repository evidence, and human input. | Tracked profile YAML; after review, generate a harness from it. |
| `forma create-bundle` | Deterministic generation from an existing profile. | Reviewed tracked profile YAML. | Repeatable bundle from committed source. |

`forma-creator` and `forma explain profile` + agent are both lightweight entry
points. The first produces a tryable one-off harness; the second produces
versionable profile source. `forma create-bundle` is the deterministic build
path after a profile exists.

## Fixed Target Contract

Each built creator is target-specific:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target claude-code --output /tmp/forma-creator-dist
```

A Codex creator generates Codex-shaped skill bundles and can also generate a
Codex plugin output when the user asks for plugin output. A Claude Code
creator generates Claude Code-shaped skill bundles only. Do not use a
creator built for one target to generate a bundle for another target.

The creator reports output paths and install hints only. It does not install
the generated output into user or project skill roots.

## Temporary Injection Lifecycle

Temporary injection is local to one generated workflow output.

The normal lifecycle is:

1. The user describes project-specific workflow concerns.
2. The agent classifies each constraint before writing JSON.
3. The creator writes a temporary injection JSON file.
4. The creator generates the skill bundle or Codex plugin output allowed by its
   fixed target contract.
5. The creator runs the bundled verifier.
6. The user or receiving agent installs the verified output and tries the
   generated skills.
7. Only useful repeated rules are promoted into a tracked profile.

Temporary injection is not a profile. It should not be treated as reviewed team
policy unless the user explicitly promotes it into profile source.

## Classification Rules

The creator should classify constraints by the narrowest correct target:

Temporary injection maps always use internal stage keys (`shape`, `gauge`,
`seal`, `pour`, `flow`), not generated public skill ids such as `forma-plan`.

| Target | Use for |
|---|---|
| `constraints.default` | Minimal always-true bottom lines. |
| `constraints.shape` | Demand clarification, route selection, scope, and unresolved decisions. |
| `constraints.gauge` | Read-only evidence collection. |
| `constraints.seal` | Plan and task materialization, including task boundaries, validation gates, and proof requirements. |
| `constraints.pour` | Current-task execution, validation gates, and proof. |
| `constraints.flow` | Safe continuation and stop conditions. |
| `conditional_overlays` | Heavy route-specific behavior such as docs-only, migration, generated-baseline, governance, backend, or cross-layer work. |
| `resources` | Explicit references, scripts, or support files selected by the workflow. |

Do not copy README, AGENTS, issue text, or governance docs wholesale into
temporary injection. Extract project-specific constraints and place them where
they belong.

## Source Adapters

If a generated bundle should fetch planning context from an issue tracker,
document exporter, private source helper, or local script, classify that as a
source adapter.

Source adapters are not base Forma capability. Add them only when a profile or
temporary injection explicitly selects them.

## Promotion To Profile

Promote temporary injection into a tracked profile when the rule is:

- repeated across runs;
- reviewed by the owning project;
- safe to share as durable source;
- specific enough to place in a stage constraint, resource, validation command,
  or conditional overlay.

Do not promote rules that are private, experimental, one-off, or based on
temporary local paths.

## Verification

`forma-creator` should run verification before reporting success. Verification
checks generated output structure and methodology rules, but it does not prove
that the injected policy is a good project decision.

See [Verifier](./verifier.md) for the boundary.

## Related Docs

- [Quick Start](./quick-start.md): first-run path using tracked profiles and `forma-creator`.
- [Profile Schema](./profile-schema.md): durable profile source format.
- [Targets](./targets.md): Codex and Claude Code install behavior.
- [Verifier](./verifier.md): what verification checks.
