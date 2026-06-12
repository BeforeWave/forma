# Profile Authoring Principles

Use this reference when an agent helps a user turn project facts into a Forma
profile, decide whether that profile should remain temporary, or decide whether
a one-off request belongs in temporary injection.

## Profile Purpose

- Profiles are structured project-rule input for workflow generation. They
  describe stage constraints, tool habits, validation, proof, and stop
  conditions.
- A profile may be temporary input for a trial workflow. Commit it as durable
  project source only when the rules should be reused by the owning repository
  or team.
- A profile should capture reusable behavior, not every one-off instruction
  from a single generation request.
- Temporary injection JSON is the right place for generation-only constraints
  that should not become tracked source.
- When a user asks to keep the rules for long-term reuse, put the profile in
  the owning repository that owns those workflow constraints. Keep Forma
  examples sanitized.

## Profile Proposal Review

When proposing a profile from repository rules, do not answer with only YAML.
Include both:

1. `Profile YAML Proposal`
2. `Profile Review Packet`

The review packet lets the user review source coverage, classification, and
placement decisions without rereading the whole repository.

### Write Boundary

Do not write or modify profile files during the proposal step unless the user
explicitly asks you to persist the profile. First return the `Profile YAML
Proposal` and `Profile Review Packet` for review.

After the user confirms the proposal, write the profile YAML to the requested
temporary path or owning repository profile path. If preserving the review
packet is requested, write it as a review artifact such as
`profiles/<profile-name>/REVIEW.md`; it is not compiled profile source.

### Profile Review Packet: Included Rules

For every meaningful profile rule, list:

- profile path, such as `constraints.shape` or
  `validation.shared_checks`;
- source file, section, and line number when available;
- source wording summary, not a long quote;
- strength: `MUST`, `SHOULD`, or `MAY`;
- why this profile section is the narrowest correct placement;
- durability: durable, task-specific, or uncertain.

### Profile Review Packet: Omitted Source Rules

List important repository instructions that were considered but not placed in
the profile, especially `MUST` and `SHOULD` rules from `AGENTS.md`, governance
docs, CI docs, or validation docs.

For each omitted rule, include:

- source file, section, and line number when available;
- source wording summary;
- reason omitted, such as task-specific, already covered by a broader rule,
  too local for this profile, needs user decision, or not workflow policy.

### Profile Review Packet: Validation Command Mapping

For every validation command candidate, explain whether it was kept, rewritten,
or omitted:

- source command;
- profile command or omitted;
- required working directory or target surface;
- reason for the mapping.

Do not invent profile rules without a source or an explicit user decision. If a
rule is useful but source support is weak, mark it as an open question instead
of silently promoting it into the profile.

## Stage Key Boundary

Profiles and temporary injection use internal stage keys as schema keys:
`shape`, `gauge`, `seal`, `pour`, and `flow`.

Generated output names, such as plugin-local `plan`/`showhand` names or direct
skill names using the `forma-*` pattern, are output names and trigger names.
Use them as `stages.<stage>.name`, `stages.<stage>.directory`, or
`rename.stages` values, not as profile or injection map keys.

For plugin output, keep `bundle.name` as the lower kebab-case plugin id. Use
`plugin.display_name` only when the plugin install surface needs display casing
or wording that should not change the plugin id, generated skill names, or
triggers.

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

## Source Context Adapters

Source-context adapters are optional integrations that load planning material
from a specific external source, such as an issue tracker, a document export
tool, or a private knowledge source. They are not base Forma capability.

Put durable source adapters in the owning repository's profile only when that
repository expects the adapter to be available for repeated work. Put one-off
source adapters in temporary injection and mark them non-durable in the
classification table.

Adapter rules belong in stage-specific constraints, usually `shape` for
planning-context loading and `seal` for final source confirmation. Adapter
references and scripts should be added as stage resources. Do not place source
adapter requirements in `constraints.default`.

When an adapter needs a helper script, model it as `resources.<stage>.scripts`
plus a matching `resources.<stage>.references` file that explains the generic
script-use boundary or adapter-specific invocation conditions. The generated
skill will receive the script under `scripts/<dest>`, so stage constraints
should cite that generated path and concrete source type, for example
`python3 scripts/adapter_tool.py ...`.

## Temporary Versus Long-Term

Commit a profile or promote a constraint into a tracked profile when it is
expected to repeat, has a clear owning repository or team, and should be
reviewed with source changes.

Keep a constraint in temporary injection when it is specific to the current
generation, uses local/private values that should not be committed, or has not
yet been accepted as durable workflow policy.

## Authoring Hygiene

- Do not copy README, AGENTS, governance docs, issue text, or other source
  documents verbatim into a profile or injection.
- Extract the workflow rule, shorten it, and place it at the narrowest
  effective target.
- Do not store private paths, credentials, business secrets, or
  organization-only commands in Forma's committed examples.
- Do not assume network access, local CLI authentication, or any issue tracker
  or document system is available unless a profile or temporary injection
  explicitly owns that adapter.
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
- Prefer committing a profile only after repeated behavior is clear. Otherwise
  keep the profile temporary or use temporary injection and mark the constraint
  non-durable.
