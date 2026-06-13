# Profile Schema

Chinese version: [profile-schema.zh-CN.md](./profile-schema.zh-CN.md)

A profile is source for long-term engineering rules the team accepts.

It describes how the project wants agents to work: which sources are
authoritative, which boundaries must not be crossed, which tools or source
helpers must be used, how deep validation should go, where proof belongs, and
when the agent must stop for review.

A profile does not write the current task's concrete plan. Current files,
commands, review gates, and proof paths are resolved by the workflow in the
task contract.

Profiles are strict YAML files: unknown top-level or nested keys are rejected so
mistakes do not silently change the generated workflow contract.

## Minimal Profile

```yaml
profile:
  id: sample-docs-workflow
  description: Minimal docs workflow profile.
bundle:
  name: sample-docs-workflow
  description: Documentation workflow skills.
constraints:
  default:
    - Preserve unrelated user work.
  shape:
    - Clarify the documentation audience and acceptance criteria before planning.
  gauge:
    - Use project docs and nearby source files as evidence before proposing doc behavior changes.
  seal:
    - Each accepted task must name evidence, boundary, validation, proof, and stop conditions.
  pour:
    - Use lightweight markdown or link checks for docs-only changes.
workflow_adds:
  pour:
    - Stop before review-ready if documentation evidence is missing.
output_adds:
  pour:
    - Include the documentation evidence paths in the final report.
```

For a complete composable example, start with:

```text
examples/profiles/sample-software/sample-software-plan-first.yaml
```

That top-level profile includes sanitized software defaults and renames the
generated stage skills without depending on organization-specific paths or
private workflow commands.

## Top-Level Keys

| Key | Purpose |
|---|---|
| `profile` | Stable profile `id` and optional human description. |
| `includes` | Relative paths or profile ids resolved before the local file. |
| `bundle` | Review-facing bundle `name` and `description`. |
| `plugin` | Optional plugin-level display metadata for plugin outputs. |
| `org` | Optional owning organization or project name. |
| `stages` | Per-stage installable names, directories, display labels, prompts, and `enabled` flags. |
| `resources` | Stage resources copied into generated skills as `references`, `scripts`, or `files`. |
| `skills` | Per-stage trigger descriptions without changing stage semantics. |
| `terminology` | Project vocabulary emitted into generated skill guidance. |
| `validation_commands` | Default or stage-specific validation commands. |
| `decision_gate_extras` | Extra dimensions `shape` must settle. |
| `constraints` | Default or stage-specific engineering rules. |
| `workflow_adds` | Default or stage-specific workflow steps rendered into `## Workflow`. |
| `output_adds` | Default or stage-specific output requirements rendered into `## Output`. |
| `conditional_overlays` | Route-specific constraints, resources, and validation activated after the plan records the selected route. |

## Includes

Use `includes` to compose project rules from general to specific:

```yaml
profile:
  id: sample-software-workflow
includes:
  - sample-software-base
  - sample-software
```

Included profiles are resolved before the local profile. Later profiles can
refine earlier fields according to the merge rules implemented by Forma.

Use includes for stable layers such as project defaults, development rules,
domain rules, and language rules. Do not use includes to hide one-off user
instructions; use temporary injection for that.

## Stage Names And Target Display

Use `stages` when the generated skill names should use project language:

```yaml
stages:
  shape:
    name: software-workflow-plan
    directory: software-workflow-plan
    display_name: Software Workflow Plan
    short_description: Clarify software work before finalizing a plan.
    default_prompt: Clarify the software task and stop before repository inspection.
```

The stage keys remain `shape`, `gauge`, `seal`, `pour`, and `flow`. Only the
installable names, directories, display labels, and prompts are renamed.

## Plugin Display Metadata

When a profile is used with `forma build plugin`, `bundle.name` remains the
plugin id and must stay lower kebab-case. Codex plugin `interface.displayName`
defaults to a title-cased version of that id. Use `plugin.display_name` only
when the plugin's install-surface brand label needs different casing or wording:

```yaml
bundle:
  name: api-tools
plugin:
  display_name: API Tools
```

This does not change the plugin id, the generated skill names, or Codex
plugin triggers such as `<plugin-id>:plan`.

## Constraints

Keep `constraints.default` light. Put rules in the stage that needs them:

| Stage constraint | Use for |
|---|---|
| `constraints.shape` | Demand clarification, route selection, scope, plan strategy, and unresolved decisions. |
| `constraints.gauge` | Read-only grounding and evidence collection. |
| `constraints.seal` | Boundaries, validation, proof, and stop conditions the task contract must include. |
| `constraints.pour` | Current-task execution, validation gates, review gates, and proof. |
| `constraints.flow` | Continuation conditions and stop conditions. |

Bad pattern:

```yaml
constraints:
  default:
    - Always read all docs, all plans, all generated baselines, and all run evidence.
```

Better pattern:

```yaml
constraints:
  default:
    - Preserve unrelated user work.
  gauge:
    - Read only evidence needed for the selected scope.
  seal:
    - Put exact validation commands or shared checks into each accepted task.
  pour:
    - Execute only the current accepted task and record proof under `plans/issue-<id>/runs/`.
```

`constraints` render into `## Requirements`. Use `workflow_adds` when a profile
must strengthen a stage's ordered workflow, completion gate, or stop condition.
Use `output_adds` when a profile must add required fields to the stage's final
response. Both fields use the same `default` and stage-specific shape as
`constraints`, but render into `## Workflow` and `## Output` respectively.

```yaml
workflow_adds:
  mend:
    - After committing a confirmed rework contract, resolve and report the execution handoff disposition before stopping.
output_adds:
  mend:
    - Include `Execution Handoff:` with the sent or blocked disposition.
```

## Resources

Resources copy stage-owned files into generated skills:

```yaml
resources:
  shape:
    references:
      - source: references/backend-workflow-rules.md
        dest: backend-rules.md
    scripts:
      - source: ../../../source/methodology/resources/shared/script/github_issue_context.py
        dest: github_issue_context.py
```

Use resources for stable references and explicit helpers. Source readers and
helper scripts should be selected by a profile or temporary injection; they
should not appear as unowned base capability.

## Validation Commands

Use `validation_commands` to give generated skills validation guidance:

```yaml
validation_commands:
  default:
    - python -m pytest tests/
  pour:
    - go test ./...
```

Validation commands are workflow guidance. They do not replace the proof path
written into the task contract for the current task.

## Conditional Overlays

Use conditional overlays for route-specific behavior:

```yaml
conditional_overlays:
  docs-only:
    constraints:
      pour:
        - Keep edits limited to documentation files.
    validation_commands:
      pour:
        - git diff --check
```

Put heavier or scenario-specific rules here, such as docs-only, migration,
generated-baseline, governance, backend, or cross-layer constraints.

## Temporary Injection And Profile

Use a tracked profile when a rule is durable and should be reviewed as project
source.

Use temporary injection when a rule is:

- one-off;
- private to the current generation;
- experimental;
- not ready to become maintained policy;
- found through `forma-creator` and still needs trial use before becoming durable.

Temporary injection should classify confirmed rules before writing JSON. Do not
copy large source documents into injection just to preserve context.

## Common Mistakes

- Putting broad reading rules in `constraints.default`.
- Renaming semantic stage keys instead of `stages.<stage>.name`.
- Copying private downstream commands into public examples.
- Keeping rules in temporary injection long after they should become a reviewed profile.
- Adding source readers without making a profile or injection own them.
- Treating `forma verify` as a replacement for human profile review.

## Related Docs

- [Workflow Contract](./workflow-contract.md): how profile rules reach current task contracts.
- [Skill Bundle](./skill-bundle.md): generated output layout.
- [Forma Creator](./forma-creator.md): how on-the-spot rules enter one-off workflows.
- [Examples](./examples.md): sample profiles and real run evidence.
- [Usage](./usage.md): command reference.
