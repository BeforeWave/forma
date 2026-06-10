# Usage

Chinese version: [usage.zh-CN.md](./usage.zh-CN.md)

This page is the command reference for Forma. For a first run, do not start by
memorizing commands; start with [Quick Start](./quick-start.md): install creator
for the agent, then use a natural-language request to extract rules and generate
a workflow.

Running `forma` with no subcommand is a successful discovery entrypoint. It exits
`0` and prints the same agent routing guide as `forma --help`, so a coding agent
can start there when it is unsure which command path to use.

## Agent Command Routing

| Goal | Command path | Next action |
|---|---|---|
| Install creator so an agent can customize a workflow from project facts | `forma build-creator --target <target> --output <dir>` | Use `target` as `codex` or `claude-code`; run `forma verify <dir>/<target>/forma-creator`, then `forma install --target <target> --scope <scope> <creator-path>` with scope `user` or `project`. |
| Build a skill bundle from a reviewed tracked profile | `forma create-bundle --target <target> --profile <profile.yaml> --output <dir>` | Use `target` as `codex` or `claude-code`; run `forma verify <dir>`, then `forma install --target <target> --scope <scope> <dir>` with scope `user` or `project`. |
| Build the default Plan-First skill bundle | `forma create-bundle --target <target> --output <dir>` | Use `target` as `codex` or `claude-code`; run `forma verify <dir>`, then `forma install --target <target> --scope <scope> <dir>` with scope `user` or `project`. |
| Build plugin source | `forma create-plugin --target codex|claude-code --profile <profile.yaml> --output <dir>` | `forma verify <dir>`; install Codex plugins through Codex, and install Claude Code plugin roots with `forma install --target claude-code`. |
| Diagnose a generated artifact before handoff | `forma doctor <dir>` or `forma doctor --json <dir>` | Use the result to identify artifact kind, target, verification status, Forma installability, install route, blockers, and next steps. |
| Give an agent authoring rules | `forma explain profile --target codex` or `forma explain temporary-injection --target codex` | Use the output as read-only guidance before drafting a profile or one-off creator injection. |

## Commands

### `forma` / `forma --help`

Prints the root command guide and command list. With no subcommand, `forma`
returns exit code `0` and shows the same routing guide as `forma --help`.

Use it as the first command when an agent needs to discover whether to build a
creator, create a skill bundle, create a plugin, install a verified local
output, verify an output, or print authoring guidance.

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

- `--target codex|claude-code`
- `--output <dir>`

Optional inputs:

- `--profile <file>`: top-level tracked profile. If omitted, Forma emits the
  generic skills `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`,
  and `forma-showhand`.

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

For a tracked profile, the Codex plugin id is the profile `bundle.name`. The
plugin display name is derived from the same value, and `plugin.json` points to
the nested `./skills/` directory. Nested skill names follow the emitted skill
names in `.forma-manifest.json`. If a profile renames skills with
`stages.<stage>.name`, the plugin exposes those renamed skills.

For Claude Code plugin output, `plugin.json` uses the profile `bundle.name` as
the plugin name. Plugin-local skill names strip the exact `<plugin-name>-`
prefix when present. For plugin `forma`, `forma-plan` becomes `plan`.
Codex plugin output keeps emitted skill names such as `forma-plan`; do not rely
on `plugin:skill` or `$plugin:skill` colon triggering for Codex.

Required options:

- `--target codex|claude-code`
- `--output <dir>`

Optional inputs:

- `--profile <file>`: top-level tracked profile. If omitted, the plugin exposes
  `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and
  `forma-showhand`.

Next action: run `forma verify <output-dir>`. Install Codex plugins through
Codex marketplace/plugin UI. Install Claude Code plugin roots with
`forma install --target claude-code --scope user|project <output-dir>`.

### `forma build-creator`

Builds a target-specific installable `forma-creator`. After installing it for
the agent, use one natural-language request to customize a project workflow:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

Required options:

- `--target codex|claude-code`
- `--output <dir>`

Optional development override:

- `--source <dir>`: use a source `forma-creator` directory instead of packaged runtime assets.

Each generated `forma-creator` has a fixed target contract. A Codex creator
generates Codex-shaped skill bundles and Codex plugin outputs. A Claude Code
creator generates Claude Code-shaped skill bundles and Claude Code plugin
outputs. See [Forma Creator](./forma-creator.md) for the on-the-spot
customization path.

Next action: run `forma verify <output-dir>/<target>/forma-creator`, then install
that verified creator path with `forma install`.

### `forma install`

Installs a verified local skill, skill bundle, or Claude Code plugin root:

```bash
forma install --target codex --scope project /tmp/forma-codex-bundle
forma install --target claude-code --scope user /tmp/forma-claude-code-bundle
forma install --target claude-code --scope project /tmp/forma-claude-code-plugin
```

Required arguments and options:

- `PATH`: local output path; URL download is intentionally not part of this command.
- `--target codex|claude-code`
- `--scope user|project`

Overwrite behavior:

- Without `--replace`, existing destination directories are rejected.
- With `--replace`, Forma replaces only the destination outputs selected by the verified source.
- Codex plugin install attempts report Codex marketplace guidance,
  `codex plugin add <plugin>@<marketplace-name>`, and the need to start a new thread after install.
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
command to give it the rules. In practice, you can simply say:

```text
Use Forma to extract engineering rules from this project's docs and code, and
draft a profile for me.
```

The agent uses `forma explain profile --target codex` to load the authoring
standard, then combines it with project facts to propose tracked profile YAML.
This path produces durable profile source, not a one-off workflow.

Next action: after the profile is reviewed, use `forma create-bundle` for a
skill bundle or `forma create-plugin` for plugin source.

## Install Targets

Forma emits target-specific skill bundles. `forma install` writes verified local
skill outputs into the matching target location:

| Target | Personal install | Project install |
|---|---|---|
| Codex skills | `$HOME/.agents/skills` | `.agents/skills` |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

OpenCode can read Codex direct skills from `.agents/skills`, so use
`--target codex` for that compatibility path. Forma does not provide
`--target opencode` or OpenCode JS/TS runtime plugin output.

Codex plugin outputs are local plugin sources. Forma does not install Codex
plugins. Follow the current Codex docs to add the generated plugin root to a
Codex marketplace, then run `codex plugin add <plugin>@<marketplace-name>` or
install it from the Codex plugin UI. Start a new Codex thread after installing
so the plugin skills are discovered.

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
- `name` and `directory` must be lower kebab-case.
- Semantic stage keys remain `shape`, `gauge`, `seal`, `pour`, and `flow`.
- When the same profile is used with `forma create-plugin`, the plugin id stays
  `bundle.name` and the nested plugin skills follow the renamed emitted skills.

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
- Internal injection maps use internal stage keys (`shape`, `gauge`, `seal`, `pour`, `flow`), not public skill ids such as `forma-plan` or `forma-showhand`.
- Names must be unique kebab-case strings and must not be bare stage names like `shape` or `flow`.
- Creator injections do not accept profile-style `stages.shape.name`. Durable names belong in profiles; one-off names belong in `rename`.
- For plugin output from `forma-creator`, `rename.prefix` also becomes the plugin id/name. Without a prefix, the plugin id/name remains `forma`.
- Claude Code plugin-local skill names strip that exact plugin-name prefix when present; Codex plugin skill names keep the emitted names.

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

This keeps pip or pipx installed CLI behavior independent of the source
checkout.

## Related Docs

- [Workflow Contract](./workflow-contract.md): stages, task contracts, gates, boundaries, and proof.
- [Skill Bundle](./skill-bundle.md): generated output layout and manifest.
- [Profile Schema](./profile-schema.md): durable engineering-rule source format.
- [Forma Creator](./forma-creator.md): let the agent customize a workflow on the spot.
- [Verifier](./verifier.md): verification checks and limits.
- [Targets](./targets.md): target install and metadata behavior.
