# AGENTS

Forma is a source workspace for plan-first skill-suite creation. It contains canonical methodology fragments, a self-contained `forma-creator` meta skill source with an embedded verifier, and a developer Python CLI/generator/creator-builder.

## Read first

- `README.md` — three-layer architecture and positioning
- `STRUCTURE.md` — the current source tree
- `plans/issue-<id>/plan.md` — current issue goal, scope, approach, validation
- `plans/issue-<id>/tasks.md` — current issue task checklist

## Working rules

- Keep changes scoped to the current issue's plan and tasks.
- Do not pre-lock Layer 2 or Layer 3 implementation decisions outside the current planned scope.
- Treat `plan.md` as the source of truth for what is and is not in scope for the current issue.
- Treat `profiles/forma-self/` as Forma-owned profile source for managing this repository's own development iterations.
- Keep `profiles/forma-self` default constraints lightweight. `forma-pour` and `forma-flow` should not require root governance docs unless the task's `Iteration Area` is docs-only, governance, profile, generated-baseline, or cross-layer.
- Keep Layer 1 temporary injection generation standards in `source/skill-creator/`. Natural-language constraints must be classified before writing injection JSON; do not put broad root-doc or generated-baseline reads into `constraints.default`.
- Use `forma explain profile` or `forma explain temporary-injection` when an external agent needs profile authoring guidance without inspecting Forma source files.
- Keep pip/pipx installed CLI behavior independent of the source checkout. Runtime guidance, default methodology, and default creator source must be available through packaged `forma.assets`; source paths are overrides only.
- Keep Forma's committed profile examples sanitized. Real downstream profiles with organization-specific workflow commands or private constraints belong in their owning repositories.
- Record meaningful execution decisions in `plans/issue-<id>/implement-notes.md` when they would help a later task or reviewer understand the work.

## Workflow state

Each issue's plan, tasks, and execution evidence live under `plans/issue-<id>/`. Treat `source/methodology/` as canonical methodology source and `source/skill-creator/` as the Layer 1 meta source. Install target-specific `forma-creator` bundles only after generating them with `forma build-creator --target <agent>`; each generated creator has a fixed target contract for its later `shape` / `gauge` / `seal` / `pour` / `flow` output.
