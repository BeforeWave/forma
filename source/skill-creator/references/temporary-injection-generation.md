# Temporary Injection Generation Standard

Use this standard when converting user natural language into a temporary
injection JSON for `scripts/create.py`. The injection is a one-off generated
artifact, not a tracked profile.

## Stage Key Boundary

Temporary injection JSON must address stages only by internal stage keys:
`shape`, `gauge`, `seal`, `pour`, `flow`, `hone`, and `mend`.

`hone` and `mend` are optional stages. Temporary injection for those stages
affects generated output only when the generation also enables the stage.

Do not use generated output names such as plugin-local `plan`/`showhand` names
or direct skill names using the `forma-*` pattern as JSON keys. Generated output
names are installable output names and user-facing trigger names; they are not
the schema keys for `stages`, `skills`, `constraints`, `validation_commands`,
`resources`, `conditional_overlays`, or `rename.stages`.

When renaming output skills, keep the internal key on the left side and put the
final generated skill name on the right side, for example
`"shape": "acme-plan"` and `"flow": "acme-showhand"`.

## Extraction Rules

- Do not copy README, AGENTS, governance docs, issue text, or other user docs
  verbatim into the injection.
- Extract only workflow constraints, validation preferences, local references,
  display text, final installable skill names, plugin display metadata, and
  conditional route decisions that affect the generated workflow bundle or
  plugin.
- Keep source-specific examples concise and sanitized. Do not include private
  paths, credentials, business secrets, or organization-only commands unless
  the current user explicitly wants those values in this one generated bundle.
- If a constraint is one-off for this generation only, include it only in the
  temporary injection, mark it as non-durable in the classification table, and
  do not recommend committing it as a tracked profile.
- Treat source-context integrations such as issue tracker readers, document
  exporters, or other CLI/API context loaders as optional source adapters. Do
  not make them base workflow capability through `constraints.default`.

## Classification Targets

Classify every extracted constraint before writing JSON.

- `constraints.default`: Applies to all `shape`, `gauge`, `seal`, `pour`, and
  `flow`. Use it only for the lightest constraints that are always true, such
  as protecting private content, preserving unrelated user work, or keeping
  output scoped to the current issue.
- `constraints.shape`: Planning and proposal-convergence rules, including
  decisions the user must settle before plan finalization.
- `constraints.gauge`: Read-only repository inspection and grounding rules.
- `constraints.seal`: Rules for writing final `plan.md`, `tasks.md`, and
  plan-level decisions.
- `constraints.pour`: Daily current-task execution rules.
- `constraints.flow`: Automated remaining-task execution rules.
- `constraints.hone`: Read-only reconciliation rules.
- `constraints.mend`: Same-issue rework contract rules.
- `conditional_overlays`: Heavy rules that should apply only after `shape`
  records a selected scenario in `plan.md`, such as docs-only,
  generated-baseline, migration, governance, backend, frontend, or coordinated
  multi-surface routes.
- `resources`: Adapter references, scripts, or support files needed by an
  explicitly selected source-context integration. Add these only when the
  current generation needs that adapter.
- `plugin.display_name`: Codex plugin install-surface display label. Use this
  only when plugin output needs brand casing or wording that cannot be derived
  from `rename.prefix`; it must not change plugin id, skill names, or triggers.

## Source Adapter Classification

When the user asks a generated bundle to load planning context from an external
source, classify the behavior as an injected source adapter:

- Put shape-time fetch/clarification behavior in `constraints.shape`.
- Put finalization-time source confirmation behavior in `constraints.seal`.
- Add only the adapter reference/script resources required by those stages.
- Mark one-off adapters as non-durable unless the owning repository or team
  wants this source integration every time.
- Promote an adapter into a tracked profile only when it is repeated, reviewed,
  and owned by that downstream repository.

Do not put issue fetching, document exports, private source readers, or similar
source adapters in `constraints.default`.

## Script Resource Injection Template

Use `resources.<stage>.scripts` when an adapter script should be copied into a
generated stage skill's `scripts/` directory. Pair it with a generic or
adapter-specific usage reference under `resources.<stage>.references`; the
reference explains when the stage may run injected scripts, while the
stage-specific constraint names the concrete script and source type. The
`source` must be a file path available during generation. The `dest` is the
script filename inside the generated skill.

```json
{
  "resources": {
    "shape": {
      "references": [
        {
          "source": "/absolute/path/to/adapter-reference.md",
          "dest": "adapter-reference.md"
        }
      ],
      "scripts": [
        {
          "source": "/absolute/path/to/adapter_tool.py",
          "dest": "adapter_tool.py"
        }
      ]
    }
  },
  "constraints": {
    "shape": [
      "When this source adapter is needed, load and follow `references/adapter-reference.md`, then run `python3 scripts/adapter_tool.py ...` and use its output as planning context."
    ]
  }
}
```

Use `resources.<stage>.files` only when the destination path must not live under
`references/` or `scripts/`. Prefer `scripts` for executable helper logic and
`references` for the stage instructions that explain when and how to run it.

## Prohibitions

- Do not place governance or root-doc reading requirements in
  `constraints.default`.
- Do not make routine `pour` or `flow` execution read broad docs, all run
  evidence, generated baselines, or an entire profile stack by default.
- Do not use `constraints.default` as a dumping ground for every user sentence.
- Do not treat network access, local CLI authentication, or access to a
  specific issue tracker or document system as a base capability of every
  generated Plan-First bundle.
- Do not copy user docs verbatim into references merely to satisfy the
  injection. Add only targeted local references when the generated bundle really
  needs them.
- Do not recommend promoting one-off generation-only constraints into a tracked
  profile.

## Classification Table

Before running `scripts/create.py`, output the temporary injection file path
and a short classification table with these columns:

| User constraint | Injection target | Rationale | Durable? | Track as profile? |
| --- | --- | --- | --- | --- |
| Original or summarized user constraint | `constraints.<stage>` or `conditional_overlays.<overlay>` | Why this location is the narrowest correct scope | yes/no | yes/no/later |

Use `Track as profile? = yes` only when the constraint is repeated behavior
that belongs in the owning repository's reviewed profile. Use `later` when the
user has not decided whether the behavior should become durable.
