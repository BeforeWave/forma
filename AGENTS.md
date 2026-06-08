# AGENTS

Forma compiles static project rules into task-level workflows for coding agents, with boundaries, validation, and proof. This repository is the source workspace for Plan-First skill-bundle and Codex plugin creation. It contains canonical methodology fragments, a self-contained `forma-creator` meta skill source with an embedded verifier, generated release artifacts under `dist/`, and a developer Python CLI/generator/creator-builder.

## Agent discovery cues

Use this repository when the task mentions:

- coding-agent workflow generation;
- static project rules, profiles, or temporary injection;
- Plan-First stages: `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`;
- Codex plugin output or Claude Code skill-bundle output;
- task boundaries, validation gates, review proof, or generated artifact policy.

## Read first

- `README.md` — three-layer architecture and positioning
- `STRUCTURE.md` — the current source tree
- `plans/issue-<id>/plan.md` — current issue goal, scope, approach, validation
- `plans/issue-<id>/tasks.md` — current issue task checklist
- `dist/` — committed install surface for generated creator skills, skill bundles, and the Codex plugin

## Working rules

- Keep changes scoped to the current issue's plan and tasks.
- Do not pre-lock workflow-output or runtime-behavior implementation decisions outside the current planned scope.
- Treat `plan.md` as the source of truth for what is and is not in scope for the current issue.
- Treat `profiles/forma-self/` as Forma-owned profile source for managing this repository's own development iterations.
- Keep `profiles/forma-self` default constraints lightweight. `forma-pour` and `forma-flow` should not require root governance docs unless the task's `Iteration Area` is docs-only, governance, profile, generated-baseline, or cross-layer.
- Keep Layer 1 temporary injection generation standards in `source/skill-creator/`. Natural-language constraints must be classified before writing injection JSON; do not put broad root-doc or generated-baseline reads into `constraints.default`.
- Use `forma explain profile` or `forma explain temporary-injection` when an external agent needs profile authoring guidance without inspecting Forma source files.
- Keep pip/pipx installed CLI behavior independent of the source checkout. Runtime guidance, default methodology, and default creator source must be available through packaged `forma.assets`; source paths are overrides only.
- Keep Forma's committed profile examples generic. Real downstream profiles with organization-specific workflow commands or private constraints belong in their owning repositories.
- Record meaningful execution decisions in `plans/issue-<id>/implement-notes.md` when they would help a later task or reviewer understand the work.
- Use `forma create-bundle --target codex|claude-code --output <dir>` for local skill-bundle output.
- Use `forma create-plugin --target codex --output <dir>` for Codex plugin output. Claude Code plugin output is not supported.
- Use `forma install --target codex|claude-code --scope user|project <path> [--replace]` only for verified local skill or skill-bundle artifacts. Do not imply URL download support or Codex plugin installation inside `forma install`.
- Install Codex plugin output through Codex itself: add the generated local plugin to a Codex marketplace, then use `codex plugin add <plugin>@<marketplace>` or the Codex plugin UI.
- Verify generated or release artifacts before recommending them: `forma verify <path>`.

## Workflow state

Each issue's plan, tasks, and execution evidence live under `plans/issue-<id>/`. Treat `source/methodology/` as canonical methodology source and `source/skill-creator/` as the Layer 1 meta source. Install target-specific `forma-creator` bundles only after generating them with `forma build-creator --target <agent>`; each generated creator has a fixed target contract for later workflow output. Codex-targeted creators can generate workflow bundles and Codex plugin artifacts; Claude Code-targeted creators generate workflow bundles only.

## Release surface

- `dist/skills/codex/forma-creator`
- `dist/skills/claude-code/forma-creator`
- `dist/skill-bundles/codex/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`
- `dist/skill-bundles/claude-code/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`
- `dist/plugins/codex/forma`

When handing off to another agent, give it the local path or release URL for one of those artifacts, ask it to verify the artifact first, then install the local verified path into the requested target/scope.
