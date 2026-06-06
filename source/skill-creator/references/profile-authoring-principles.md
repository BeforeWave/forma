# Profile Authoring Principles

Use this reference when an agent helps a user draft a durable Forma profile or
decide whether a one-off request should remain a temporary injection.

## Profile Purpose

- Profiles are durable workflow source. Treat reviewed profile files like code.
- A profile should capture repeated behavior for an owning repository or team,
  not every one-off instruction from a single generation request.
- Temporary injection JSON is the right place for generation-only constraints
  that should not become tracked source.
- When a user asks for durable behavior, put the profile in the owning
  repository that owns those workflow constraints. Keep Forma examples
  sanitized.

## Constraint Placement

- `constraints.default`: Keep this minimal. It applies to every
  `shape`, `gauge`, `seal`, `pour`, and `flow` stage, so use it only for
  lightweight bottom lines that are always true.
- `constraints.shape`: Planning, proposal convergence, and decisions the user
  must settle before finalization.
- `constraints.gauge`: Read-only grounding and repository inspection.
- `constraints.seal`: Final `plan.md`, `tasks.md`, validation, task boundary,
  and evidence-materialization rules.
- `constraints.pour`: Daily current-task execution.
- `constraints.flow`: Automated remaining-task execution.
- `conditional_overlays`: Heavy route-specific rules that should apply only
  after `shape` records the selected scenario in `plan.md`.

## Heavy Rule Routing

Use conditional overlays for rules that are expensive, scenario-specific, or
only valid after a plan decision. Typical overlay routes include docs-only,
generated-baseline, migration, governance, backend, frontend, and cross-layer
work.

Do not put broad root-doc reads, generated baseline reads, all-run evidence
reads, full profile-stack reads, or broad governance requirements in
`constraints.default`. Doing so makes routine `pour` and `flow` execution pay
the cost on every task.

## Durable Versus One-Off

Promote a constraint to a tracked profile when it is expected to repeat, has a
clear owning repository or team, and should be reviewed with source changes.

Keep a constraint in temporary injection when it is specific to the current
generation, uses local/private values that should not be committed, or has not
yet been accepted as durable workflow policy.

## Authoring Hygiene

- Do not copy README, AGENTS, governance docs, issue text, or other source
  documents verbatim into a profile or injection.
- Extract the durable workflow rule, shorten it, and place it at the narrowest
  effective target.
- Do not store private paths, credentials, business secrets, or
  organization-only commands in Forma's committed examples.
- Use generated baselines only when the issue makes them part of the review
  surface or drift guard.

## Required Classification Table

When producing a temporary injection or proposing profile changes from natural
language, show the user a short table before generation or commit:

| User constraint | Injection/profile target | Rationale | Durable? | Track as profile? |
| --- | --- | --- | --- | --- |
| Original or summarized user constraint | `constraints.<stage>` or `conditional_overlays.<overlay>` | Why this is the narrowest correct scope | yes/no | yes/no/later |

## Common Optimizations

- Keep daily execution defaults narrow so routine `pour` and `flow` read only
  the active plan, task checklist, current task, relevant source files, and
  necessary references.
- Move docs, generated-baseline, migration, governance, and cross-layer rules
  into conditional overlays.
- Use stage-specific constraints for planning and materialization rules instead
  of making execution stages rediscover broad context.
- Prefer a tracked profile only after repeated behavior is clear; otherwise use
  temporary injection and mark the constraint non-durable.
