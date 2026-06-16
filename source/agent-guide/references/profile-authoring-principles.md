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

## Candidate Draft From Project Facts

Use this guidance after `forma explain agent` routes the work to profile
authoring. The `forma explain profile` command does not inspect the repository
or produce a draft by itself. It tells the agent how to turn repository facts
into a candidate profile draft.

Read the repository's agent-facing and workflow-facing sources first:

- agent entrypoints, such as `AGENTS.md`, `CLAUDE.md`, Copilot instructions,
  Cursor rules, or OpenHands microagents;
- project structure, source/generated/docs/vendor boundaries, and local-state
  rules;
- setup, bootstrap, build, validation, release, and CI documentation;
- task-state, plan, issue, ADR, review-note, run-log, and evidence locations;
- human-gate rules for destructive operations, credentials, publishing,
  external writes, large refactors, or durable rule adoption;
- generated-artifact, deprecated-doc, example, fixture, and noise-control
  policy.

Extract candidate profile rules from those facts by workflow behavior, not by
the file that happened to contain the wording. Keep each candidate short,
source-backed, and marked as candidate until review.

## Project Purpose And Maintenance Semantics

Before proposing profile YAML, summarize the repository's purpose and
maintenance model from source-backed facts. Doctor `ready` means the repository
is operable by an agent; it does not mean a profile is complete or project-ready.

The summary must cover:

- repository kind and primary deliverables, described from the repo's own
  sources instead of a fixed technology template;
- runtime, artifact, package, publishing, or documentation model;
- source-of-truth, generated-output, release, and local-state boundaries;
- validation model for routine changes and higher-risk changes;
- compatibility, migration, data, security, privacy, API, contract, or user
  impact risks that are relevant to this repository;
- review, evidence, handoff, and owner-decision model.

Use those dimensions to find durable delivery semantics. Do not write a profile
that only preserves doctor findings such as entrypoints, task state, validation
presence, or human gates. If the candidate rules only cover those operability
contracts, label the draft `operability-only` and ask whether the user wants a
project-ready profile before promoting it.

For each candidate rule, record:

- source file, section, and line number when available;
- the workflow behavior it changes;
- the likely profile target, such as `constraints.<stage>`,
  `workflow_adds.<stage>`, `output_adds.<stage>`,
  `validation.shared_checks`, `resources.<stage>`, or
  `conditional_overlays.<overlay>`;
- durability: durable, task-specific, generation-only, or uncertain;
- whether the rule may already be owned by base methodology and therefore
  needs stage comparison before writing.

Group the candidate rules by touched stage before proposing YAML. The draft
should make it easy to run the later stage semantic check against only the
affected stages instead of rereading the whole repository.

## Existing Profile Incremental Review

Use this path when `forma doctor` reports an existing `.forma/profile.yaml` or
another tracked profile and asks for profile refinement or coverage review.
This is still profile authoring, but the task is incremental review rather than
starting from a blank profile.

Read the current profile and the doctor handoff's `read_first` sources. Compare
the existing profile against source-backed repository instructions. Do not
replace the profile wholesale, and do not run build, verify, or drift just to
prove the current profile artifact is fresh.

Return an incremental review with these exact section headings. Do not collapse
the review into generic prose headings such as "findings", "conclusion", or
"suggestions":

- `Covered`: durable repository rules already represented by the profile, with
  the profile path and source evidence.
- `Missing`: source-backed durable rules that should be proposed for profile
  addition, with the narrowest target such as `constraints.gauge`,
  `workflow_adds.seal`, or `output_adds.pour`.
- `Stale`: profile rules whose source evidence is gone, contradicted, or
  superseded.
- `Redundant`: profile rules that merely restate base methodology or duplicate
  another profile rule.
- `Stage Placement`: touched stages and why each candidate rule belongs there.
- `Profile YAML Proposal`: only the minimal YAML delta or replacement snippet
  needed for review.
- `Profile Review Packet`: source evidence, rule classification, omitted rules,
  open questions, and owner confirmations.
- `Recommended Next Step`: exactly one next action. Format it as two child
  lines: `Recommendation: <one concrete next action>` and `Offer: Should I
  <perform that action> now?`. The offer must be an explicit question, not a
  passive note such as "this needs confirmation" or a multi-part list of
  possible decisions.

After writing `Recommended Next Step`, request confirmation through the host's
structured interaction capability when one is available, such as a choice,
user-input, or command-approval UI. In Codex-like hosts, command approval UI is
for actual tool or shell actions that require permission; use a structured
choice/user-input capability for non-command decisions when the host exposes
one. If no structured interaction capability is available in the current
thread, end with `Required Confirmation: <yes/no question>` instead of only
leaving the offer as passive prose.

Stop after the incremental review unless the user explicitly asks to write the
profile, validate generated artifacts, or reinstall workflow output. Validation
commands such as `forma build`, `forma verify`, and `forma drift` belong after
approved profile edits or explicit artifact validation requests; they do not
answer whether the existing profile semantically covers the repository rules.

## Profile Proposal Review

When proposing a profile from repository rules, do not answer with only YAML.
Include both:

1. `Profile YAML Proposal`
2. `Profile Review Packet`

The review packet lets the user review source coverage, classification, and
placement decisions without rereading the whole repository.

### Profile Review Packet: Project Understanding

Start the review packet with a source-backed project understanding section:

- project purpose and primary deliverables;
- maintenance model: what makes changes correct, safe, and sustainable here;
- durable semantic layers included in the profile, such as base workflow,
  language/runtime, product/domain, validation/evidence, source/artifact
  boundary, release/deployment, security/privacy, or review/handoff;
- semantic layers intentionally omitted and why.

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
  already owned by base methodology, too local for this profile, needs user
  decision, or not workflow policy.

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

Profiles use internal stage keys as schema keys:
`shape`, `gauge`, `seal`, `pour`, `flow`, `hone`, and `mend`.

`hone` and `mend` are optional stages. Their constraints, workflow additions,
output additions, and resources affect generated output only when the profile
enables the stage with `stages.<stage>.enabled: true`.

Generated output names, such as plugin-local `plan`/`showhand` names or direct
skill names using the `forma-*` pattern, are output names and trigger names.
Use them as `stages.<stage>.name`, `stages.<stage>.directory`, or
`rename.stages` values, not as profile or injection map keys.

For plugin output, keep `bundle.name` as the lower kebab-case plugin id. Use
`plugin.display_name` only when the plugin install surface needs display casing
or wording that should not change the plugin id, generated skill names, or
triggers.

## Constraint Placement

- `constraints.default`: Keep this minimal. It applies to every enabled stage,
  so use it only for lightweight bottom lines that are always true.
- `constraints.shape`: Planning, proposal convergence, and decisions the user
  must settle before finalization.
- `constraints.gauge`: Read-only grounding and repository inspection.
- `constraints.seal`: Final `plan.md`, `tasks.md`, validation, task boundary,
  and evidence-materialization rules.
- `constraints.pour`: Daily current-task execution.
- `constraints.flow`: Automated remaining-task execution.
- `constraints.hone`: Read-only reconciliation of delivered work, feedback,
  evidence, and next-route recommendations.
- `constraints.mend`: Same-issue rework contract materialization without
  implementing the rework.
- `workflow_adds.<stage>`: Additional ordered workflow steps, completion
  gates, or stop conditions that must appear in the generated stage's
  `## Workflow` section instead of the weaker `## Requirements` section.
- `output_adds.<stage>`: Required final-response fields that must appear in
  the generated stage's `## Output` section.
- `conditional_overlays`: Heavy route-specific rules that should apply only
  after `shape` records the selected scenario in `plan.md`.

If a project rule changes when a stage is allowed to stop, where it must hand
off, or what field must appear in the final response, do not encode it as a
plain `constraints` item. Use `workflow_adds` or `output_adds` so the generated
skill carries the rule in the stage's execution path.

## Heavy Rule Routing

Use conditional overlays for rules that are expensive, scenario-specific, or
only valid after a plan decision. Typical overlay routes include docs-only,
generated-baseline, migration, governance, backend, frontend, and coordinated
multi-surface work.

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

When proposing profile changes from natural language or repository facts, show
the user a short table before writing or committing profile files:

| Candidate rule | Profile target or omitted route | Rationale | Durable? | Track as profile? |
| --- | --- | --- | --- | --- |
| Original or summarized rule | `constraints.<stage>`, `workflow_adds.<stage>`, `output_adds.<stage>`, `conditional_overlays.<overlay>`, base methodology, temporary injection, or omitted | Why this is the narrowest correct route | yes/no | yes/no/later |

## Common Optimizations

- Keep daily execution defaults narrow so routine `pour` and `flow` read only
  the active plan, task checklist, current task, relevant source files, and
  necessary references.
- Move docs, generated-baseline, migration, governance, and coordinated
  multi-surface rules into conditional overlays.
- Use stage-specific constraints for planning and materialization rules instead
  of making execution stages rediscover broad context.
- Prefer committing a profile only after repeated behavior is clear. Otherwise
  keep the profile temporary or use temporary injection and mark the constraint
  non-durable.
