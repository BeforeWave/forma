# Forma Creator

Chinese version: [forma-creator.zh-CN.md](./forma-creator.zh-CN.md)

`forma-creator` is Forma's agent-side generation entrypoint.

Use it when you want to try a workflow idea without first writing a durable
profile YAML file. It helps an agent turn reviewed natural-language workflow
constraints into temporary injection JSON, generate a target-specific skill
bundle, and verify that bundle before handoff.

## How It Differs From `forma create`

| Path | Best for | Input | Output |
|---|---|---|---|
| `forma create` | Durable team or project workflow rules. | Reviewed tracked profile YAML. | Repeatable bundle from committed source. |
| `forma-creator` | One-off or experimental workflow ideas. | Reviewed natural-language constraints classified into temporary injection JSON. | One generated bundle for the fixed target. |

`forma create` is the deterministic profile path.

`forma-creator` is the try-it-now path. It is useful before a team knows which
rules deserve to become durable profile source.

## Fixed Target Contract

Each built creator is target-specific:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target claude-code --output /tmp/forma-creator-dist
```

A Codex creator generates Codex-shaped workflow bundles. A Claude Code creator
generates Claude Code-shaped workflow bundles. Do not use a creator built for
one target to generate a bundle for another target.

## Temporary Injection Lifecycle

Temporary injection is local to one generated bundle.

The normal lifecycle is:

1. The user describes workflow constraints.
2. The agent classifies each constraint before writing JSON.
3. The creator writes a temporary injection JSON file.
4. The creator generates the bundle.
5. The creator runs the bundled verifier.
6. The user tries the workflow.
7. Only useful repeated rules are promoted into a tracked profile.

Temporary injection is not a profile. It should not be treated as reviewed team
policy unless the user explicitly promotes it into profile source.

## Classification Rules

The creator should classify constraints by the narrowest correct target:

| Target | Use for |
|---|---|
| `constraints.default` | Minimal always-true bottom lines. |
| `constraints.shape` | Demand clarification, route selection, scope, and unresolved decisions. |
| `constraints.gauge` | Read-only evidence collection. |
| `constraints.seal` | Plan and task materialization. |
| `constraints.pour` | Current-task execution and proof. |
| `constraints.flow` | Safe continuation and stop conditions. |
| `conditional_overlays` | Heavy route-specific behavior such as docs-only, migration, generated-baseline, governance, backend, or cross-layer work. |
| `resources` | Explicit references, scripts, or support files selected by the workflow. |

Do not copy README, AGENTS, issue text, or governance docs wholesale into
temporary injection. Extract workflow rules and place them where they belong.

## Source Adapters

If a generated bundle should fetch planning context from an issue tracker,
document exporter, private source helper, or local script, classify that as a
source adapter.

Source adapters are not base Forma capability. Add them only when a profile or
temporary injection explicitly selects them.

## Promotion To Profile

Promote temporary injection into a tracked profile when the rule is:

- repeated across runs;
- reviewed by the owning team or project;
- safe to share as durable source;
- specific enough to place in a stage constraint, resource, validation command,
  or conditional overlay.

Do not promote rules that are private, experimental, one-off, or based on
temporary local paths.

## Verification

`forma-creator` should run verification before reporting success. Verification
checks generated bundle structure and methodology rules, but it does not prove
that the injected policy is a good product decision.

See [Verifier](./verifier.md) for the boundary.

## Related Docs

- [Quick Start](./quick-start.md): first-run path using tracked profiles and `forma-creator`.
- [Profile Schema](./profile-schema.md): durable profile source format.
- [Targets](./targets.md): Codex and Claude Code install behavior.
- [Verifier](./verifier.md): what verification checks.
