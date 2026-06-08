# Profile Schema

Chinese version: [profile-schema.zh-CN.md](./profile-schema.zh-CN.md)

A profile is Layer 0 source: durable project rules and boundaries.

Profiles describe how Forma should specialize the canonical Plan-First
methodology for a project, route, language, or target naming convention. They
are strict YAML files: unknown top-level or nested keys are rejected so mistakes
do not silently change the generated workflow contract.

## Minimal Profile

```yaml
profile:
  id: sample-docs-workflow
  description: Minimal docs workflow profile.
bundle:
  name: sample-docs-workflow
  description: Documentation Plan-First skills.
constraints:
  default:
    - Keep default rules minimal.
  shape:
    - Clarify the documentation audience and acceptance criteria before planning.
  pour:
    - Run markdown or link checks when docs behavior changes.
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
| `org` | Optional owning organization or team name. |
| `stages` | Per-stage installable names, directories, display labels, prompts, and `enabled` flags. |
| `resources` | Stage resources copied into generated skills as `references`, `scripts`, or `files`. |
| `skills` | Per-stage trigger descriptions without changing stage semantics. |
| `terminology` | Project vocabulary emitted into generated skill guidance. |
| `validation_commands` | Default or stage-specific validation commands. |
| `decision_gate_extras` | Extra dimensions `shape` must settle. |
| `constraints` | Default or stage-specific workflow requirements. |
| `conditional_overlays` | Route-specific constraints, resources, and validation activated after the plan records the selected route. |

## Includes

Use `includes` to compose project rules from general to specific:

```yaml
profile:
  id: sample-software-plan-first
includes:
  - sample-software-base
  - sample-software
```

Included profiles are resolved before the local profile. Later profiles can
refine earlier fields according to the merge rules implemented by Forma.

Use includes for stable layers such as project defaults, development policy,
domain policy, and language policy. Do not use includes to hide one-off user
instructions; use temporary injection for that.

## Stage Names And Target Display

Use `stages` when the generated skill names should use project language:

```yaml
stages:
  shape:
    name: software-plan-first-plan-issue
    directory: software-plan-first-plan-issue
    display_name: Software Plan-First Plan Issue
    short_description: Clarify software work before finalizing a plan.
    default_prompt: Clarify the software task and stop before repository inspection.
```

The stage keys remain `shape`, `gauge`, `seal`, `pour`, and `flow`. Only the
installable names, directories, display labels, and prompts are renamed.

## Constraints

Keep `constraints.default` light. Put rules in the stage that needs them:

| Stage constraint | Use for |
|---|---|
| `constraints.shape` | Demand clarification, route selection, scope, plan strategy, and unresolved decisions. |
| `constraints.gauge` | Read-only grounding and evidence collection. |
| `constraints.seal` | Plan materialization, accepted tasks, validation contracts, and handoff certification. |
| `constraints.pour` | Current-task files, commands, validation gates, review gates, and proof. |
| `constraints.flow` | Safe continuation and stop conditions. |

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

## Resources

Resources copy stage-owned files into generated skills:

```yaml
resources:
  shape:
    references:
      - source: references/backend-plan-first-rules.md
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

Validation commands are guidance for the workflow. They do not remove the need
for task-specific validation in locked plans.

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

Put heavy or scenario-specific rules here, such as docs-only, migration,
generated-baseline, governance, backend, or cross-layer constraints.

## Temporary Injection Vs Profile

Use a tracked profile when a rule is durable and should be reviewed as project
source.

Use temporary injection when a rule is:

- one-off;
- private to the current generation;
- experimental;
- not ready to become maintained policy.

Temporary injection should classify natural-language rules before writing JSON.
Do not copy large source documents into injection just to preserve context.

## Common Mistakes

- Putting broad reading rules in `constraints.default`.
- Renaming semantic stage keys instead of `stages.<stage>.name`.
- Copying private downstream commands into public examples.
- Using temporary injection for rules that should be reviewed profiles.
- Adding source readers without making a profile or injection own them.
- Treating `forma verify` as a replacement for human profile review.

## Related Docs

- [Workflow Contract](./workflow-contract.md): what the profile specializes.
- [Skill Bundle](./skill-bundle.md): generated output layout.
- [Forma Creator](./forma-creator.md): temporary injection before durable profile promotion.
- [Examples](./examples.md): sample profile walkthrough.
- [Usage](./usage.md): command reference.
