# Canonical Plan-First Builder Contract

Forma creator output must preserve the bundled canonical plan-first semantics
shipped with this creator package.

## Source Resources

Use these bundled files from this built or installed `forma-creator` package:

- `resources/plan-first/methodology/stages/shape.md`
- `resources/plan-first/methodology/stages/gauge.md`
- `resources/plan-first/methodology/stages/seal.md`
- `resources/plan-first/methodology/stages/pour.md`
- `resources/plan-first/methodology/stages/flow.md`
- `resources/plan-first/methodology/resources/<stage>/...`

Do not recreate the base workflow from memory. The installed creator should
run `scripts/create.py`, which reads the matching methodology stage source,
preserves its effective `## Adds` requirements, copies fixed stage resources
into the generated skill directory, and runs the bundled verifier.

Stage source files may contain source-only include directives:

```text
{{ include: fragments/<path>.md }}
```

Resolve each directive relative to `resources/plan-first/methodology/` before
emission. Keep concise stage workflow guidance in `SKILL.md`; emit long
canonical requirement blocks as generated stage-local references under the
same skill's `references/` directory, then cite them from `SKILL.md` with
explicit `Load and follow` requirements. Fragment source files are not copied
as-is into generated suites.

In Forma source form, these files are maintained only under sibling
`source/methodology/` and copied into this creator bundle by
`forma build-creator`. Do not maintain a second checked-in methodology copy
under `source/skill-creator/`.

## Stage Mapping

Installed `forma-creator` output uses stable stage keys internally. By
default, it emits installable skill directories and frontmatter names with the
`forma-` prefix: `forma-shape`, `forma-gauge`, `forma-seal`, `forma-pour`, and
`forma-flow`. During creation, the user may choose final installable skill names
through the temporary JSON field `rename.stages`; those names replace the
defaults without changing the internal stage keys or methodology mapping.

- `shape` maps to plan-issue: Plan-mode, chat-only convergence before plan files
  exist.
- `gauge` maps to ground-plan: read-only repository grounding before
  finalization.
- `seal` maps to finalize-plan: write and commit `plan.md` and `tasks.md` only
  after the decision gate passes.
- `pour` maps to implement-feature: execute the current task through
  `review-ready`, wait for user approval, then `complete`.
- `flow` maps to showhand: execute all remaining tasks from an already-finalized
  plan with preflight and safety stops.

## Generated Skill Shape

Each generated `SKILL.md` must use the same high-level section order as the
installed creator renderer:

1. frontmatter with only `name` and `description`;
2. H1 display title;
3. description paragraph;
4. `## Interaction Semantics`;
5. stage-specific gate sections when applicable;
6. `## Workflow`;
7. reference loading section;
8. `## Requirements`;
9. `## Output`.

## Fixed Resources

Copy fixed resources exactly from the creator bundle. Shared source files live
under `resources/plan-first/methodology/resources/shared/`; stage-specific
source files live under `resources/plan-first/methodology/resources/<stage>/`.
Generate them into the destination paths below so each emitted skill remains
self-contained:

- `shape`: `references/output-format.md` and
  `references/plan-issue-rules.md`.
- `gauge`: `references/output-format.md`.
- `seal`: `references/planning-rules.md`,
  `references/output-format.md`, `references/plan-template.md`,
  `references/tasks-template.md`, and `scripts/forma-workflow.sh`.
- `pour`: `references/execution-rules.md`,
  `references/output-format.md`, `references/implement-notes.md`,
  `references/plan-template.md`, `references/tasks-template.md`, and
  `scripts/forma-workflow.sh`.
- `flow`: `references/execution-rules.md`,
  `references/output-format.md`, `references/implement-notes.md`, and
  `scripts/forma-workflow.sh`.

Make copied `scripts/forma-workflow.sh` executable.

Optional source-context adapters may live in the methodology resource tree for
reuse, but they are not fixed resources. Copy adapter references or scripts
only when a temporary injection or tracked profile explicitly adds them.

## Generated Requirement References

Emit these expanded source fragments as generated references inside the
owning skill directory. The generated `SKILL.md` must cite each emitted file
with a `Load and follow` requirement so expanding those citations restores the
same effective requirement list as the validated canonical methodology source.

- `shape`: `fragments/shape/decision-gate-adds.md` to
  `references/proposal-decision-gate.md`, and
  `fragments/shape/handoff-adds.md` to `references/grounding-handoff.md`.
- `seal`: `fragments/seal/decision-gate-adds.md` to
  `references/finalization-decision-gate.md`,
  `fragments/seal/plan-materialization-adds.md` to
  `references/plan-materialization.md`, and
  `fragments/seal/task-structure-adds.md` to
  `references/task-structure.md`.
- `pour`: `fragments/pour/task-runner-adds.md` to
  `references/task-runner.md`.
- `flow`: `fragments/flow/automated-execution-adds.md` to
  `references/automated-execution.md`.

If a one-off injected constraint exactly duplicates a bullet already emitted
through one of these generated references, keep only one effective copy after
expansion.

## Injection Boundary

One-off user constraints are supplied to `scripts/create.py` through a
temporary injection JSON generated from the current conversation. That JSON is
not a Layer 3 profile and must not contain `profile`, `includes`, tracked
profile ids, or `stages.<kind>.name` / `stages.<kind>.directory` overrides. It
may add local requirements, stage display text, validation preferences,
additional references, and final installable skill names under
`rename.stages`. It must not replace fixed resources, remove gate rules, weaken
review-ready/complete semantics, or borrow resources from sibling generated
skills.

Before writing the temporary JSON, load
`references/temporary-injection-generation.md` and classify every
natural-language constraint by its narrowest injection target. Keep
`constraints.default` limited to light always-on bottom lines. Put planning,
grounding, plan-materialization, execution, and automated-execution rules under
their matching stage keys. Put heavy scenario-specific requirements, including
root-doc reading, generated-baseline inspection, migration rules, governance
rules, or cross-layer work, behind `conditional_overlays`.

The agent must output the temporary injection file path plus a classification
table that shows the original user constraint, structured injection target,
rationale, durability, and whether the constraint should later be promoted into
a tracked profile. Do not put that classification metadata into the injection
JSON unless the JSON schema explicitly supports it.

Forma has one optional conditional injection mechanism, not built-in business
classification. If the current user asks for conditional behavior, the
temporary JSON may include `conditional_overlays`: `shape` settles the named
decision, `seal` records it into `plan.md`, and `pour` / `flow` read the
recorded value from the finalized plan. Overlay references must stay out of
unconditional `Always Load`, `Read After Gate`, and `Load As Needed` sections
and appear only under `## Conditional References` for the routes supplied by
the injection.
