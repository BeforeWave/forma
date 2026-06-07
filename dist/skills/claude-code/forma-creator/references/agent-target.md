# Agent Target: Claude Code

This `forma-creator` bundle is fixed to `claude-code`. Its generated plan-first output must contain exactly five skill directories. Defaults are:

- `forma-plan/` - Use only in plan-oriented collaboration to clarify Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer, and any applicable Artifact/Evidence Boundary before plan finalization.
- `forma-ground/` - Inspect repository facts read-only and produce a grounding handoff before plan files are written.
- `forma-lock/` - Materialize an already-settled plan into plan.md and tasks.md without reopening planning decisions.
- `forma-execute/` - Execute the current workflow task through review-ready, wait for user approval, then complete and continue if another task remains.
- `forma-showhand/` - Execute all remaining tasks from an already-finalized issue plan automatically with preflight, validation, evidence, and safety gates.

## Output Contract

- Before generating a bundle, load `references/canonical-plan-first.md` and `references/profile-authoring-principles.md` and `references/temporary-injection-generation.md`; preserve the bundled canonical plan-first semantics and classify natural-language constraints before writing JSON.
- Convert current-session natural-language injection into a temporary JSON file and run `python scripts/create.py --artifact bundle --output <generated-bundle-path> --injection-json <temporary-injection.json>` for workflow-bundle output; do not use Layer 3 profiles from this installed creator.
- Copy fixed generated-skill resources from `resources/plan-first/methodology/resources/shared/` and any stage-local resource directory into each generated skill directory according to `references/canonical-plan-first.md`.
- Generate a Claude Code-ready workflow bundle root containing `forma-plan/`, `forma-ground/`, `forma-lock/`, `forma-execute/`, and `forma-showhand/` by default, or the exact `rename.stages` names confirmed by the user.
- Codex plugin output is unsupported by this Claude Code creator; present workflow-bundle generation only.
- Keep temporary injection JSON stage keys as `shape`, `gauge`, `seal`, `pour`, and `flow`; do not expose those bare stage keys as installable skill directory names.
- Do not use generated public skill ids such as `forma-plan` or `forma-showhand` as temporary injection JSON keys.
- Every generated skill directory must include `SKILL.md` with frontmatter containing only `name` and `description`.
- Keep bundled references inside each generated skill's own `references/` directory.
- Do not emit Codex `agents/openai.yaml` files from this Claude Code creator.
- `scripts/create.py` runs the verifier before reporting success.

## Interactive Constraint Handling

- The user may provide one-off special constraints for the generated five-skill bundle during this interaction.
- Before writing the temporary JSON, show the default installable skill names: `shape -> forma-plan`, `gauge -> forma-ground`, `seal -> forma-lock`, `pour -> forma-execute`, and `flow -> forma-showhand`.
- Ask whether the user wants to rename any final installable skill names. If yes, encode exact kebab-case names under `rename.stages`; if no, omit `rename` and use the defaults.
- Encode those constraints in a temporary injection JSON when they are compatible with the plan-first methodology and this target contract.
- Classify every natural-language constraint before writing JSON: `constraints.default` is only for minimal always-on bottom lines; planning rules go under `shape` / `gauge` / `seal`; daily execution rules go under `pour` / `flow`; broad docs, generated-baseline, migration, governance, or cross-layer rules belong in `conditional_overlays`.
- Treat issue tracker readers, document exporters, private source loaders, and similar source-context helper scripts as optional source adapters. Inject their stage-specific constraints and resources only when explicitly requested; do not treat them as base capability or place them in `constraints.default`.
- Output the temporary injection file path plus a short classification table with user constraint, injection target, rationale, durability, and whether it should later become a tracked Layer 3 profile.
- Do not copy user docs verbatim, do not put governance/root-doc reading requirements in `constraints.default`, and do not make routine `pour` / `flow` read broad docs, all runs, generated baselines, or full profile stacks by default.
- Do not put `profile`, `includes`, tracked profile ids, or stage `name` / `directory` overrides in that temporary injection JSON. Final installable names belong only under `rename.stages`.
- Run `python scripts/create.py --artifact bundle --output <generated-bundle-path> --injection-json <temporary-injection.json>` before handing off or reporting success.
- Do not install generated artifacts from this creator. Report the output path and install hint only.
- Do not represent one-off constraints as tracked source. If the user wants durable tracking, help them promote the constraints into a Layer 3 profile in the owning repository.
