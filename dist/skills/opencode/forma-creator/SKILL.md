---
name: forma-creator
description: Create or update self-contained Forma Plan-First workflow outputs. Use when an agent needs to generate an installable workflow bundle, generate a Codex plugin when the fixed target contract allows it, adapt Plan-First methodology with temporary injection, or verify generated workflow outputs with the bundled Forma verifier before reporting success.
compatibility: opencode
metadata:
  forma.kind: "creator"
  forma.target: "opencode"
---

# Forma Creator

Use this skill to create Forma Plan-First workflow outputs. By default it
creates a workflow bundle: a flat, ready-to-install set of five plan-first
direct skills for the `plan`, `ground`, `lock`, `execute`, and `showhand`
stages using the `forma-*` naming pattern. If this installed creator includes a
fixed target reference, that reference is the hard contract for any additional
artifact type.

Before generating any bundle, load `references/canonical-plan-first.md`,
`references/profile-authoring-principles.md`, and
`references/temporary-injection-generation.md`. If this installed creator
includes a fixed agent-target reference, load it too and treat it as the fixed
target contract.

## Workflow

1. Confirm the output directory and any workflow customization values:
   organization name, stage display text, validation-command preferences,
   local reference files, final skill names, and extra Decision Gate dimensions.
2. Classify the injection shape before writing JSON:
   - Fixed scenario: use ordinary `constraints`, `resources`,
     `validation_commands`, and `decision_gate_extras`; every injected rule is
     unconditional.
   - Conditional scenario: if the user says if/when/only when, or describes
     deciding A to use X and B to use Y, use `conditional_overlays`.
   - Unclear scenario: do not invent conditional routing. Ask first whether the
     user wants a fixed injection or a conditional overlay decision.
   - Within either scenario, classify every natural-language constraint using
    `references/profile-authoring-principles.md` and
    `references/temporary-injection-generation.md`; keep
    `constraints.default` minimal and put broad or expensive execution
    requirements into stage-specific constraints or `conditional_overlays`.
   - If the user asks the generated bundle to fetch planning context from an
     external source through a helper script, treat that as a source-context
     adapter. Add stage-specific constraints and resources only when the
     adapter is explicitly requested; do not treat network access, local CLI
     authentication, or any source tool as base capability.
3. Show the installable skill names before generating. Default direct bundle
   names use the `forma-*` pattern for `shape -> plan`, `gauge -> ground`,
   `seal -> lock`, `pour -> execute`, and `flow -> showhand`. Ask whether the
   user wants to rename any of those installable skill names. If they do,
   encode the final names under `rename.stages` in the temporary JSON. If they
   do not, use the defaults.
4. Read `references/canonical-plan-first.md` and preserve the canonical
   workflow shape. It is derived from the validated plan-first model:
   chat-only convergence, read-only grounding, task-contract finalization,
   review-gated task execution, and automated full-flow execution. Do not
   remove gate dimensions, weaken task-level validation/proof requirements,
   rename on-disk files such as `plan.md` / `tasks.md`, or make workflow
   stages optional.
5. Convert the current conversation's one-off injection into a temporary JSON
   file. This JSON is not a profile and must not be treated as tracked source.
   Before generation, output the temporary injection path and a short
   classification table covering the original user constraint, injection
   target, rationale, durability, and whether to promote it into a tracked
   profile later.
6. Run the bundled deterministic creator script for workflow-bundle output:

```bash
python scripts/create.py --artifact bundle --output <generated-bundle-path> --injection-json <temporary-injection.json>
```

   If the installed creator's generated agent-target reference explicitly
   permits another artifact type, follow that target-specific command instead.
   Do not infer target-specific artifacts from this generic skill body.

The script creates the five default direct skill directories using the
`forma-*` form of the `plan`, `ground`, `lock`, `execute`, and `showhand`
stages for bundle output. If the user supplied `rename.stages`, the script
creates those final installable skill directories instead. The script copies
bundled methodology resources, applies the temporary injection, writes metadata,
and runs the bundled verifier. Only report success after it exits cleanly. Do
not install generated outputs from this creator; report the output path and
install hint only.

## Stage Rules

Every generated bundle uses the same five stages. The temporary injection JSON
uses these internal stage keys, while installable skill directories and
frontmatter names use target-specific output names:

- `shape` / `plan` is chat-only convergence. It settles Goal, Scope, Approach,
  Validation, Plan Strategy, and task-level artifact/evidence boundaries before `proposal-ready`.
- `gauge` / `ground` is read-only repository inspection. It produces a grounding handoff
  for `seal` and does not write files.
- `seal` / `lock` materializes `plan.md` and `tasks.md` under `plans/issue-<id>/`, including accepted files/surfaces, validation gates, proof requirements, dependencies, and constraints.
- `pour` / `execute` executes one accepted task contract at a time through `review-ready` and `complete`.
- `flow` / `showhand` executes all remaining tasks automatically after the plan is sealed,
  while still honoring validation, safety, and permission gates.

## Bundled Resources

Generated bundles must keep the canonical resources stage-local. These paths
exist inside a built or installed `forma-creator` bundle. In Forma source, the
same files are maintained only under `source/methodology/` and copied into the
creator bundle by `forma build-creator`.

- `shape`: resources under
  `resources/plan-first/methodology/resources/shape/`.
- `gauge`: resources under
  `resources/plan-first/methodology/resources/gauge/`.
- `seal`: resources under
  `resources/plan-first/methodology/resources/seal/`.
- `pour` and `flow`: resources under
  `resources/plan-first/methodology/resources/pour/` and
  `resources/plan-first/methodology/resources/flow/`.

One-off workflow injection may add local references and constraints, but must
not replace the canonical runner or change internal stage keys, and must not
manually rename generated directories outside `rename.stages` or borrow
resources from sibling skill directories.
If injected constraints duplicate bullets already emitted through generated
requirement references, keep one effective copy.

## Injection JSON

Temporary injection JSON always uses internal stage keys as addressing keys:
`shape`, `gauge`, `seal`, `pour`, and `flow`.

Do not use generated output names such as plugin-local `plan`/`showhand` names
or direct skill `forma-*` names as keys under `stages`, `skills`,
`constraints`, `validation_commands`, `resources`, `conditional_overlays`, or
`rename.stages`.

Generated output names are user-facing trigger names. Internal stage keys are
the stable addressing layer for profile and injection rules. To change
generated skill names, map internal keys to final output names under
`rename.stages`.

The temporary injection JSON may contain only these top-level keys:

- `rename`: optional final installable skill names. Use `rename.stages` to map
  any of `shape`, `gauge`, `seal`, `pour`, or `flow` to a confirmed kebab-case
  skill name. Omit it to use the default public names. Use `rename.prefix` only
  when the desired generated names are `<prefix>-plan`, `<prefix>-ground`,
  `<prefix>-lock`, `<prefix>-execute`, and `<prefix>-showhand`.
- `stages`: optional `display_name`, `short_description`, and `default_prompt`
  per stage.
- `skills`: optional `description` per stage.
- `constraints`: `default` or stage-specific requirement bullets.
- `validation_commands`: `default` or stage-specific validation commands.
- `decision_gate_extras`: extra dimensions that `shape` must settle.
- `resources`: stage-local `references`, `scripts`, or `files` copied from
  paths supplied in the current session.
- `conditional_overlays`: optional decision-routed overlays. This is a Forma
  mechanism only; route ids, overlay ids, and business constraints must come
  from the current user injection, not from hardcoded Forma defaults.

For a one-off source-context helper script, use `resources.<stage>.scripts`;
the generated skill receives the file under `scripts/<dest>`. Pair scripts
with a reference that explains the generic script-use boundary or
adapter-specific invocation conditions:

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
      "When this source adapter is needed, load the generated adapter reference, run the copied adapter script, and use its output as planning context."
    ]
  }
}
```

Do not put `profile`, `includes`, tracked profile ids, or stage `name` /
`directory` overrides under `stages`. Installable skill names may be customized
only under `rename.stages`, for example:

```json
{
  "rename": {
    "stages": {
      "shape": "renamed-shape",
      "gauge": "renamed-gauge",
      "seal": "renamed-seal",
      "pour": "renamed-pour",
      "flow": "renamed-flow"
    }
  }
}
```

If the user wants durable tracked behavior, help them create or update a Layer
3 profile outside this installed creator.

### Temporary Injection Classification

When converting user natural language into temporary injection JSON:

- Do not copy user docs verbatim.
- Extract only workflow constraints, validation preferences, local references,
  display text, final installable names, and conditional route decisions that
  affect this generated bundle.
- Classify every constraint by the narrowest injection target:
  - `constraints.default`: applies to all stages; keep it minimal and reserved
    for the lightest always-true bottom lines.
  - `constraints.shape`, `constraints.gauge`, and `constraints.seal`: planning,
    grounding, and plan materialization rules.
  - `constraints.pour` and `constraints.flow`: daily task execution rules.
  - `conditional_overlays`: heavy rules for selected scenarios such as docs,
    generated-baseline, migration, governance, or cross-layer work.
- If a constraint would make daily `pour` or `flow` read broad docs, all runs,
  generated outputs, or full profile stacks, do not place it in
  `constraints.default`.
- If a constraint is one-off for this generation only, include it in the
  temporary injection, mark it non-durable in the classification table, and do
  not recommend committing it as a tracked profile.
- Source-context helper scripts such as issue tracker readers, document
  exporters, or private source loaders are optional injection/profile behavior.
  Put their planning rules in `constraints.shape`, finalization confirmation in
  `constraints.seal`, and copy only the adapter reference or script resources
  that the user explicitly requested.
- Do not put source-context adapter behavior in `constraints.default` or make
  it part of every generated bundle.

### Conditional Overlay Schema

Use this only when the user explicitly describes conditional behavior. The
decision value must be settled during `shape`, recorded into `plan.md` by
`seal`, and read from the finalized `plan.md` by `pour` and `flow`. If execution
cannot find the recorded decision, it must stop for plan correction instead of
re-deciding the route.

```json
{
  "conditional_overlays": {
    "decision": {
      "name": "Plan Type",
      "must_record_in_plan": true,
      "missing_during_execution": "stop-for-plan-correction"
    },
    "routes": [
      {
        "id": "generic-dev",
        "description": "Generic development work.",
        "overlays": []
      },
      {
        "id": "backend-non-go",
        "description": "Backend work outside the Go stack.",
        "overlays": ["backend"]
      }
    ],
    "overlays": {
      "backend": {
        "description": "Backend-specific constraints.",
        "constraints": {
          "shape": [],
          "gauge": [],
          "seal": [],
          "pour": [],
          "flow": []
        },
        "resources": {
          "shape": {
            "references": []
          }
        },
        "validation_commands": {}
      }
    }
  }
}
```

Overlay references must not be emitted into unconditional `Always Load`, `Read
After Gate`, or `Load As Needed` sections. They must appear only under
`## Conditional References`, grouped by route and selected by the recorded
decision value.

## Verification Contract

The verifier in `scripts/forma_verifier/` is stdlib-only and ships inside this
skill. It checks:

- frontmatter exists and includes `name` and `description`
- skill names are kebab-case
- generated plan-first skill names match their parent skill directories
- each `SKILL.md` has at least one `##` section
- cited `references/*.md` files exist
- generated skills do not borrow sibling `references/` or `scripts/`
- `shape`, `gauge`, `seal`, and `pour` mention their required methodology
  markers

Use `scripts/create.py` for generation; it calls `scripts/verify.py` before
returning success. Do not require the user to install the developer `forma`
Python package just to generate or verify an agent-generated bundle.

## Output

When finished, report:

- generated bundle path
- temporary injection file path
- classification table for injected constraints
- verifier command and result
- any intentionally injected terminology or validation-command overrides
- unresolved items only if they block installation or use

## Fixed Agent Target

This installed creator is fixed to the OpenCode target. Before writing generated plan-first skills, load `references/agent-target.md` and follow it as a hard output contract.

Do not offer another agent format from this installed creator. If the user needs a different target, they need that target's `forma-creator` bundle installed instead.
