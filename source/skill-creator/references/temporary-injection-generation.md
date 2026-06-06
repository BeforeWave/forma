# Temporary Injection Generation Standard

Use this standard when converting user natural language into a temporary
injection JSON for `scripts/create.py`. The injection is a one-off generated
artifact, not a tracked Layer 3 profile.

## Extraction Rules

- Do not copy README, AGENTS, governance docs, issue text, or other user docs
  verbatim into the injection.
- Extract only workflow constraints, validation preferences, local references,
  display text, final installable skill names, and conditional route decisions
  that affect the generated five-skill bundle.
- Keep source-specific examples concise and sanitized. Do not include private
  paths, credentials, business secrets, or organization-only commands unless
  the current user explicitly wants those values in this one generated suite.
- If a constraint is one-off for this generation only, include it only in the
  temporary injection, mark it as non-durable in the classification table, and
  do not recommend committing it as a tracked profile.

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
- `conditional_overlays`: Heavy rules that should apply only after `shape`
  records a selected scenario in `plan.md`, such as docs-only,
  generated-baseline, migration, governance, backend, frontend, or cross-layer
  routes.

## Prohibitions

- Do not place governance or root-doc reading requirements in
  `constraints.default`.
- Do not make routine `pour` or `flow` execution read broad docs, all run
  evidence, generated baselines, or an entire profile stack by default.
- Do not use `constraints.default` as a dumping ground for every user sentence.
- Do not copy user docs verbatim into references merely to satisfy the
  injection. Add only targeted local references when the generated suite really
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
that belongs in the owning repository's reviewed Layer 3 profile. Use `later`
when the user has not decided whether the behavior should become durable.
