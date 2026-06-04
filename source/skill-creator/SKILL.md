---
name: forma-creator
description: Create or update self-contained Forma plan-first skill suites. Use when Codex needs to generate an installable flat suite of forma-shape, forma-gauge, forma-seal, forma-pour, and forma-flow SKILL.md folders, adapt the plan-first methodology to an organization, or verify a generated suite with the bundled Forma verifier before reporting success.
---

# Forma Creator

Use this skill to create a Mode-S Forma suite: a flat, ready-to-install set of
five plan-first skills named `forma-shape`, `forma-gauge`, `forma-seal`,
`forma-pour`, and `forma-flow`.

Before generating any suite, load `references/canonical-plan-first.md`. If this
installed creator includes a fixed agent-target reference, load it too and treat
it as the fixed target contract.

## Workflow

1. Confirm the output directory and any business injection values: organization
   name, stage display text, validation-command preferences, local reference
   files, and extra Decision Gate dimensions.
2. Classify the injection shape before writing JSON:
   - Fixed scenario: use ordinary `constraints`, `resources`,
     `validation_commands`, and `decision_gate_extras`; every injected rule is
     unconditional.
   - Conditional scenario: if the user says if/when/only when, or describes
     deciding A to use X and B to use Y, use `conditional_overlays`.
   - Unclear scenario: do not invent conditional routing. Ask first whether the
     user wants a fixed injection or a conditional overlay decision.
3. Show the installable skill names before generating. Default:
   `shape -> forma-shape`, `gauge -> forma-gauge`, `seal -> forma-seal`,
   `pour -> forma-pour`, and `flow -> forma-flow`. Ask whether the user wants
   to rename any of those installable skill names. If they do, encode the
   final names under `rename.stages` in the temporary JSON. If they do not, use
   the defaults.
4. Read `references/canonical-plan-first.md` and preserve the canonical
   workflow shape. It is derived from the validated
   plan-first model: chat-only convergence, read-only grounding,
   finalization, review-gated task execution, and automated full-flow
   execution. Do not remove gate dimensions, rename on-disk artifacts such as
   `plan.md` / `tasks.md`, or make workflow stages optional.
5. Convert the current conversation's one-off injection into a temporary JSON
   file. This JSON is not a profile and must not be treated as tracked source.
6. Run the bundled deterministic creator script:

```bash
python scripts/create.py --output <generated-suite-path> --injection-json <temporary-injection.json>
```

By default, the script creates exactly `forma-shape/`, `forma-gauge/`,
`forma-seal/`, `forma-pour/`, and `forma-flow/`. If the user supplied
`rename.stages`, the script creates those final installable skill directories
instead. It copies bundled methodology resources, applies the temporary
injection, writes `.forma-manifest.json`, and runs the bundled verifier. Only
report success after it exits cleanly.

## Stage Rules

Every generated suite uses the same five stages. The temporary injection JSON
uses these stage keys, while installable skill directories and frontmatter names
use the matching `forma-` prefix:

- `shape` / `forma-shape` is chat-only convergence. It settles Goal, Scope, Approach,
  Validation, and Plan Strategy before `proposal-ready`.
- `gauge` / `forma-gauge` is read-only repository inspection. It produces a grounding handoff
  for `seal` and does not write files.
- `seal` / `forma-seal` materializes `plan.md` and `tasks.md` under `plans/issue-<id>/` using
  the project issue-workflow init step.
- `pour` / `forma-pour` executes one task at a time through `review-ready` and `complete`.
- `flow` / `forma-flow` executes all remaining tasks automatically after the plan is sealed,
  while still honoring validation, safety, and permission gates.

## Bundled Resources

Generated suites must keep the canonical resources stage-local. These paths
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

One-off business injection may add local references and constraints, but must
not replace the canonical runner, rename the flat `forma-shape` /
`forma-gauge` / `forma-seal` / `forma-pour` / `forma-flow` directories, or
borrow resources from sibling skill directories.
If injected constraints duplicate bullets already emitted through generated
requirement references, keep one effective copy.

## Injection JSON

The temporary injection JSON may contain only these top-level keys:

- `rename`: optional final installable skill names. Use `rename.stages` to map
  any of `shape`, `gauge`, `seal`, `pour`, or `flow` to a confirmed kebab-case
  skill name. Omit it to use the default `forma-*` names.
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

Do not put `profile`, `includes`, tracked profile ids, or stage `name` /
`directory` overrides under `stages`. Installable skill names may be customized
only under `rename.stages`, for example:

```json
{
  "rename": {
    "stages": {
      "shape": "backend-plan-first-plan-issue",
      "gauge": "backend-plan-first-ground-plan",
      "seal": "backend-plan-first-finalize-plan",
      "pour": "backend-plan-first-implement-feature",
      "flow": "backend-plan-first-showhand"
    }
  }
}
```

If the user wants durable tracked behavior, help them create or update a Layer
3 profile outside this installed creator.

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
Python package just to generate or verify an agent-generated suite.

## Output

When finished, report:

- generated suite path
- verifier command and result
- any intentionally injected terminology or validation-command overrides
- unresolved items only if they block installation or use
