# Usage

Chinese version: [usage.zh-CN.md](./usage.zh-CN.md)

This page is the command reference for Forma. For a first run, do not start by
memorizing commands; start with [Quick Start](./quick-start.md): ask the agent
to extract project rules, review them, then generate and install a workflow.

Running `forma` with no subcommand is a successful discovery entrypoint. It exits
`0` and prints the same agent routing guide as `forma --help`, so a coding agent
can start there when it is unsure which command path to use.

## Agent Command Routing

| Goal | Command path | Next action |
|---|---|---|
| Let an agent load profile authoring rules | `forma explain profile --target codex` | Agent-facing command; use the output as read-only guidance before drafting a profile from project facts. |
| Build a skill bundle from a reviewed tracked profile | `forma create-bundle --target <target> --profile <profile.yaml> --output <dir>` | Use generation `target` as `codex`, `claude-code`, or `opencode`; run `forma verify <dir>`, then install with the matching target. |
| Build the default Plan-First skill bundle | `forma create-bundle --target <target> --output <dir>` | Use generation `target` as `codex`, `claude-code`, or `opencode`; run `forma verify <dir>`, then install with the matching target. |
| Build plugin source | `forma create-plugin --target codex|claude-code --profile <profile.yaml> --output <dir>` | `forma verify <dir>`; install Codex plugins through Codex, and install Claude Code plugin roots with `forma install --target claude-code`. |
| Diagnose a generated artifact before handoff | `forma doctor <dir>` or `forma doctor --json <dir>` | Use the result to identify artifact kind, target, verification status, Forma installability, install route, blockers, and next steps. |
| Build optional creator for on-the-spot generation | `forma build-creator --target <target> --output <dir>` | Use only for the creator path; run `forma verify <dir>/<target>/forma-creator`, then install with the matching target. |
| Give an agent temporary-injection rules | `forma explain temporary-injection --target codex` | Use only for optional creator/on-the-spot generation flows. |

## Commands

### `forma` / `forma --help`

Prints the root command guide and command list. With no subcommand, `forma`
returns exit code `0` and shows the same routing guide as `forma --help`.

Use it as the first command when an agent needs to discover whether to print
authoring guidance, create a skill bundle, create a plugin, install a verified
local output, verify an output, or build an optional creator.

### `forma verify <path>`

Verifies a generated skill bundle, `forma-creator` bundle, Codex plugin, or
Claude Code plugin:

```bash
forma verify /tmp/settings-workflow-codex
forma verify --json /tmp/settings-workflow-codex
```

Use it before installing, committing, or sharing generated workflow outputs.

Next action:

- If a skill bundle or creator verifies, install the verified local path with
  `forma install`.
- If a Codex plugin verifies, install it through Codex, not `forma install`.
- If a Claude Code plugin verifies, install the plugin root with
  `forma install --target claude-code`.
- If the path is ambiguous, run `forma doctor <path>` to get the install route
  and next steps.

`forma verify` checks structure and methodology rules. It does not replace
profile review or product judgment. See [Verifier](./verifier.md) for the
verification boundary.

Use `--json` when another tool or agent needs structured output. The JSON report
keeps the same exit code contract and includes semantic failure classes for each
reported rule result.

### `forma doctor <path>`

Diagnoses a generated artifact before handoff or installation:

```bash
forma doctor /tmp/settings-workflow-codex
forma doctor --json /tmp/forma-codex-plugin
```

The doctor output identifies the artifact kind, target, verification status,
whether `forma install` supports the artifact, whether it is installable now,
the correct install route, blockers, and next steps.

Use it when a user or agent is unsure whether the current path is a skill, skill
bundle, Codex plugin, Claude Code plugin, broken artifact, or unsupported
directory.

### `forma create-bundle`

Composes the methodology and a resolved tracked profile into a target-specific
workflow bundle:

```bash
forma create-bundle --target codex --output /tmp/forma-codex-bundle
```

Required options:

- `--target codex|claude-code|opencode`
- `--output <dir>`

Optional inputs:

- `--profile <file>`: top-level tracked profile. If omitted, Forma emits the
  generic direct skills for the `plan`, `ground`, `lock`, `execute`, and
  `showhand` stages with the `forma-*` prefix.

Optional development override:

- `--methodology <dir>`: use a source methodology directory instead of packaged runtime assets.

Next action: run `forma verify <output-dir>`, then install the verified local
bundle with `forma install`.

Profile format is documented in [Profile Schema](./profile-schema.md).

### `forma create-plugin`

Builds a local plugin output from a profile:

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma create-plugin --target claude-code --output /tmp/forma-claude-code-plugin
```

Codex plugin output contains `.codex-plugin/plugin.json`, root
`.forma-manifest.json`, and `skills/<skill-id>/` directories. Claude Code
plugin output uses `.claude-plugin/plugin.json` with the same root manifest and
nested `skills/<skill-id>/` layout. Plugin output does not emit
`dist/skill-bundles` or any sibling bundle output.

For a tracked profile, the plugin id is the profile `bundle.name`. The Codex
plugin display name defaults to a title-cased version of the same value, or can
be set explicitly with `plugin.display_name`. `plugin.json` points to the
nested `./skills/` directory. Plugin-local skill names strip the exact
`<plugin-id>-` prefix when present. For plugin `forma`, the default local stages
are `plan`, `ground`, `lock`, `execute`, and `showhand`.

Codex plugin output also records qualified names such as `forma:plan` in the
manifest and in Codex metadata prompts. Use `forma:*` triggers for Codex plugin
skills. Direct skill bundles are the shape that uses standalone `forma-*` skill
names.

Required options:

- `--target codex|claude-code`
- `--output <dir>`

Optional inputs:

- `--profile <file>`: top-level tracked profile. If omitted, the plugin exposes
  plugin-local `plan`, `ground`, `lock`, `execute`, and `showhand` stages.

Next action: run `forma verify <output-dir>`. For profile-generated output, run
`forma drift <output-dir> --profile <profile.yaml>` before any postprocess. If
you intentionally postprocess the generated artifact, postprocess after drift
and use `forma verify <output-dir>` as the final gate.

Install Codex plugins through Codex marketplace/plugin UI, not `forma install`.
Run `codex plugin marketplace list`, ask the user which existing marketplace to
use or whether to create/register a new one, ensure that marketplace catalog
points to the generated plugin root, then install with
`codex plugin add <plugin-id>@<marketplace-name>`. If Codex CLI output or
marketplace behavior differs, consult current Codex docs or
`codex plugin marketplace --help`.

Install Claude Code plugin roots with
`forma install --target claude-code --scope user|project <output-dir>`.

### `forma build-creator`

Builds a target-specific installable `forma-creator`. This is the optional
on-the-spot path for generating a workflow without handling a profile file
first:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target opencode --output /tmp/forma-creator-dist
```

Required options:

- `--target codex|claude-code|opencode`
- `--output <dir>`

Optional development override:

- `--source <dir>`: use a source `forma-creator` directory instead of packaged runtime assets.

Each generated `forma-creator` has a fixed target contract. A Codex creator
generates Codex-shaped skill bundles and Codex plugin outputs. A Claude Code
creator generates Claude Code-shaped skill bundles and Claude Code plugin
outputs. An OpenCode creator generates OpenCode-native skill bundles and does
not generate OpenCode JS/TS runtime plugins. See
[Forma Creator](./forma-creator.md) for the on-the-spot customization path.

Next action: run `forma verify <output-dir>/<target>/forma-creator`, then install
that verified creator path with `forma install`.

### `forma install`

Installs a verified local skill, skill bundle, or Claude Code plugin root:

```bash
forma install --target codex --scope project /tmp/forma-codex-bundle
forma install --target opencode --scope project /tmp/forma-opencode-bundle
forma install --target claude-code --scope user /tmp/forma-claude-code-bundle
forma install --target claude-code --scope project /tmp/forma-claude-code-plugin
```

Required arguments and options:

- `PATH`: local output path; URL download is intentionally not part of this command.
- `--target codex|claude-code|opencode`
- `--scope user|project`

Overwrite behavior:

- Without `--replace`, existing destination directories are rejected.
- With `--replace`, Forma replaces only the destination outputs selected by the verified source.
- Codex plugin install attempts report Codex marketplace guidance, including
  `codex plugin marketplace list`, user marketplace selection, explicit
  `codex plugin add <plugin-id>@<marketplace-name>`, and the need to start a
  new thread after install.
- Claude Code plugin roots install under `.claude/skills/<plugin-name>` for
  project scope or `$HOME/.claude/skills/<plugin-name>` for user scope.

Next action: after installing a skill, skill bundle, or Claude Code plugin,
start a new agent thread so the installed skills are discovered.

### `forma explain`

Prints canonical authoring guidance without requiring an external agent to read
Forma source files:

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

When another agent needs to draft a profile or temporary injection, use this
command to give it the rules. For the normal profile-first path, you can simply
say:

```text
Use Forma to generate a Codex workflow for this project.
Show me the project rules you extracted first; after I approve them, generate and install it.
```

The agent uses `forma explain profile --target codex` to load the authoring
standard, then combines it with project facts to propose profile YAML. Commit
that profile only when the rules need long-term reuse.

Next action: after the profile is reviewed, use `forma create-bundle` for a
skill bundle or `forma create-plugin` for plugin source.

## Install Targets

Forma emits target-specific skill bundles. `forma install` writes verified local
skill outputs into the matching target location:

| Target | Personal install | Project install |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.agents/skills` |
| OpenCode skills | `$HOME/.config/opencode/skills` | `.opencode/skills` |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

OpenCode uses direct skill bundles. Generate an OpenCode bundle with
`forma create-bundle --target opencode`, verify it, then install it with
`forma install --target opencode`. Forma does not emit OpenCode JS/TS runtime
plugin output.

Codex plugin outputs are local plugin sources. Forma does not install Codex
plugins. Run `codex plugin marketplace list`, ask the user which existing
marketplace to use or whether to create/register a new one, make sure that
marketplace catalog points to the generated plugin root, then run
`codex plugin add <plugin-id>@<marketplace-name>` or install it from the Codex
plugin UI. Start a new Codex thread after installing so the plugin skills are
discovered. If Codex CLI output or marketplace behavior differs from this guide,
consult current Codex docs or `codex plugin marketplace --help`.

Claude Code plugin outputs are installable through Forma because Claude Code
loads skills-directory plugins from `.claude/skills/<plugin-name>`.

- [Install a local plugin manually](https://developers.openai.com/codex/plugins/build#install-a-local-plugin-manually)
- [Add a marketplace from the CLI](https://developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli)

For target-specific discovery, metadata, and trust details, see
[Targets](./targets.md).

## Rename Generated Skills

Forma keeps semantic stages `shape`, `gauge`, `seal`, `pour`, and `flow`, but
generated skill names can use project language.

### Durable Profile Names

For tracked profiles, set `stages.<stage>`:

```yaml
stages:
  shape:
    name: settings-workflow-plan
    directory: settings-workflow-plan
    display_name: Settings Workflow Plan
  gauge:
    name: settings-workflow-ground
    directory: settings-workflow-ground
    display_name: Settings Workflow Ground
```

Rules:

- `name` is the skill frontmatter name.
- `directory` is the installable skill directory.
- `display_name` is the target-surface display label.
- `plugin.display_name` sets the Codex plugin install-surface display label
  without changing the plugin id, skill names, or triggers.
- `name` and `directory` must be lower kebab-case.
- Semantic stage keys remain `shape`, `gauge`, `seal`, `pour`, and `flow`.
- When the same profile is used with `forma create-plugin`, the plugin id stays
  `bundle.name`; plugin-local skills strip that exact prefix when present. Codex
  plugin triggers use the resulting `<plugin-id>:<local-skill>` form, such as
  `forma:plan` for the default Forma plugin.

### One-Off Creator Names

For agent-side generation through `forma-creator`, users do not hand the agent a
JSON file. Tell the agent the naming intent in natural language; the creator
classifies that request and writes temporary injection internally.

Example prompt:

```text
Use forma-creator to generate this workflow with the prefix `settings-workflow`.
Show the proposed skill names before generation; after I confirm, generate and
verify the bundle.
```

Rules:

- The creator-generated injection should use `rename.prefix` to produce `<prefix>-plan`, `<prefix>-ground`, `<prefix>-lock`, `<prefix>-execute`, and `<prefix>-showhand`.
- The creator-generated injection should use `rename.stages` only when overriding individual stage names.
- Internal injection maps use internal stage keys (`shape`, `gauge`, `seal`, `pour`, `flow`), not final output names such as `plan`, `showhand`, or `forma-*` direct skill names.
- Names must be unique kebab-case strings and must not be bare stage names like `shape` or `flow`.
- Creator injections do not accept profile-style `stages.shape.name`. Durable names belong in profiles; one-off names belong in `rename`.
- For plugin output from `forma-creator`, `rename.prefix` also becomes the plugin id/name. Without a prefix, the plugin id/name remains `forma`.
- For plugin output from `forma-creator`, `plugin.display_name` sets the Codex plugin install-surface display label without changing the plugin id/name.
- Plugin-local skill names strip that exact plugin-name prefix when present. Codex plugin triggers use `<plugin-id>:<local-skill>`, with `forma:*` for the default Forma plugin; direct skill bundles use `forma-*`.

After renaming, verify the generated bundle:

```bash
forma verify <generated-bundle-dir>
```

## Repository Checks

For Forma repository maintenance, run the main checks from the repository root
after editable dev installation:

```bash
forma verify source/skill-creator/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
python -m pytest -p no:cacheprovider tests/
git diff --check
```

## Source Layout

- `source/methodology/`: methodology used to emit task-level workflow skills.
- `source/skill-creator/`: self-contained `forma-creator` source with bundled references, creator script, and verifier.
- `src/forma/`: Python CLI, profile compiler, runtime asset resolver, and target emitters.
- `profiles/forma-self/`: Forma-owned profile stack for this repository.
- `examples/profiles/`: profile examples.
- `examples/generated/`: committed generated baselines for drift checks.
- `tests/`: verifier, creator, runtime asset, profile, and generated-baseline tests.

See [Repository Structure](../STRUCTURE.md) for the detailed tree map.

## Installed CLI Behavior

Packaged Forma commands use `forma.assets` runtime assets by default. Source
paths are development overrides only:

- `forma create-bundle` and `forma create-plugin` use packaged methodology unless `--methodology` is provided.
- `forma install` only installs verified local outputs; it does not download URLs.
- `forma build-creator` uses packaged creator source unless `--source` is provided.
- `forma explain` renders canonical guidance from packaged references.

This keeps the `forma-cli` installed CLI behavior independent of the source
checkout.

## Related Docs

- [Workflow Contract](./workflow-contract.md): stages, task contracts, gates, boundaries, and proof.
- [Skill Bundle](./skill-bundle.md): generated output layout and manifest.
- [Profile Schema](./profile-schema.md): how profiles describe stage constraints, tool habits, validation, and proof.
- [Forma Creator](./forma-creator.md): optional on-the-spot workflow generation.
- [Verifier](./verifier.md): verification checks and limits.
- [Targets](./targets.md): target install and metadata behavior.
