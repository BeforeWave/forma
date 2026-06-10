# AGENTS

Forma turns project engineering rules into installable agent workflows. Those
workflows make an agent produce a task contract before implementation: evidence,
boundaries, validation, proof, and stop conditions for the current task.

This repository is the source workspace for Forma's CLI, compiler, verifier,
`forma-creator`, generated skill bundles, and Codex / Claude Code plugin output.

## When This Repository Is Relevant

Use this repository when the task involves:

- extracting or compiling project engineering rules for agents;
- profiles, temporary injection, or `forma-creator`;
- workflow outputs for Codex or Claude Code;
- Codex and Claude Code plugin generation;
- task contracts, boundaries, validation gates, proof, or stop conditions;
- verifier behavior or generated-output drift;
- Forma's own self-iteration profile and workflow.

## Read First

- `README.md` - product positioning and the main project-rule workflow model.
- `docs/quick-start.md` - fastest creator-first usage path.
- `docs/concepts.md` - project rules, workflow output, and task contract.
- `STRUCTURE.md` - current source tree.
- `plans/issue-<id>/plan.md` - active issue goal, scope, approach, and validation when present.
- `plans/issue-<id>/tasks.md` - accepted task checklist when present.
- `dist/` - committed install surface when release, install, plugin, or generated-output behavior is in scope.

## Source Boundaries

| Path | Role | Writable? |
|---|---|---|
| `source/methodology/` | Canonical workflow methodology source used to generate stage skills. | Only within current issue scope. |
| `source/skill-creator/` | Self-contained `forma-creator` source with bundled creator references and verifier. | Only within current issue scope. |
| `src/forma/` | Python CLI, profile compiler, runtime asset resolver, target emitters, and installer. | Only within current issue scope. |
| `profiles/forma-self/` | Forma-owned profile stack for this repository's own development workflow. | Only for self-iteration tasks. |
| `examples/` | Public example profile source and committed generated drift baselines. | Keep generic; no private downstream rules. |
| `dist/` | Committed release artifacts: creator skills, skill bundles, and Codex plugin. | Only after generation and verification. |
| `plans/issue-<id>/` | Per-issue planning and execution evidence. | Yes, for the active issue. |

## Working Rules

- Keep edits scoped to the current issue's plan and tasks when an issue plan exists. For direct maintenance requests without a plan, keep edits narrowly scoped to the requested surface.
- Treat `plan.md` as the source of truth for what is and is not in scope when present.
- Preserve the distinction between long-term profile rules and current-task contract output. Profiles define review standards; `plan.md`, `tasks.md`, and run proof resolve the current task.
- Keep `profiles/forma-self/` as Forma-owned profile source for this repository.
- Keep `profiles/forma-self` default constraints lightweight. Heavy root-doc or generated-baseline reads should be conditional, not default.
- Keep `source/methodology/` and `source/skill-creator/` separate. `forma build-creator` injects the methodology tree into built creator bundles at generation time.
- Use `forma explain profile` or `forma explain temporary-injection` when an external agent needs authoring guidance without reading Forma source files.
- Keep `forma-cli` installed CLI behavior independent of the source checkout. Runtime guidance, default methodology, and default creator source must be available through packaged `forma.assets`; source paths are development overrides only.
- Keep committed examples generic. Real downstream profiles with organization-specific commands, private paths, credentials, or business rules belong in their owning repositories.
- Do not write non-temporary absolute filesystem paths into tracked files. Only temporary paths under `/tmp`, `/private/tmp`, or `$TMPDIR` may appear when they are necessary evidence; use relative paths or placeholders instead of local home, workspace, private, credential, or organization-sensitive paths.
- Record meaningful execution decisions in `plans/issue-<id>/implement-notes.md` when they would help a later task or reviewer understand the work.
- Verify generated or release artifacts before recommending them: `forma verify <path>`.

## CLI Quick Reference

```bash
# Build and install a forma-creator for agent-side workflow generation.
forma build-creator --target codex|claude-code --output <dir>
forma install --target codex|claude-code --scope user|project <path>

# Generate a skill bundle or plugin from a tracked profile.
forma create-bundle --target codex|claude-code --profile <profile.yaml> --output <dir>
forma create-plugin --target codex|claude-code --profile <profile.yaml> --output <dir>

# Generate default workflow output when no profile is provided.
forma create-bundle --target codex|claude-code --output <dir>
forma create-plugin --target codex|claude-code --output <dir>

# Verify generated artifacts before using them.
forma verify <path>

# Print profile or temporary-injection authoring guidance.
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

## Install And Target Rules

- Use `forma create-bundle --target codex|claude-code --output <dir>` for local skill-bundle output.
- Use `forma create-plugin --target codex|claude-code --output <dir>` for plugin output.
- Use `forma install --target codex|claude-code --scope user|project <path> [--replace]` only for verified local skill, skill-bundle, or Claude Code plugin artifacts.
- Do not imply URL download support or Codex plugin installation inside `forma install`.
- Install Codex plugin output through Codex itself: add the generated local plugin to a Codex marketplace, then use `codex plugin add <plugin>@<marketplace>` or the Codex plugin UI.
- Install Claude Code plugin output through Forma into `.claude/skills/<plugin-name>` or `~/.claude/skills/<plugin-name>`.
- Codex direct skills install into `.agents/skills` / `~/.agents/skills`; OpenCode compatibility uses that direct-skill path. Do not add `--target opencode` unless a future plan explicitly introduces OpenCode-native output.

## Workflow State

Each issue's plan, tasks, and execution evidence live under
`plans/issue-<id>/`. Install target-specific `forma-creator` bundles only after
generating them with `forma build-creator --target <target>`; each generated
creator has a fixed target contract. Codex-targeted creators can generate skill
bundles and Codex plugin artifacts. Claude Code-targeted creators can generate
skill bundles and Claude Code plugin artifacts.

## Release Surface

- `dist/skills/codex/forma-creator`
- `dist/skills/claude-code/forma-creator`
- `dist/skill-bundles/codex/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`
- `dist/skill-bundles/claude-code/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`
- `dist/plugins/codex/forma`
- `dist/plugins/claude-code/forma`

When handing off to another agent, give it the local path or release URL for one
of those artifacts, ask it to verify the artifact first, then install the local
verified path into the requested target and scope.
