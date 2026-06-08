# Usage

Chinese version: [usage.zh-CN.md](./usage.zh-CN.md)

This page is the command reference for Forma. For a first run, start with
[Quick Start](./quick-start.md).

## Commands

### `forma verify <path>`

Verifies a generated skill bundle, `forma-creator` bundle, or Codex plugin:

```bash
forma verify /tmp/backend-plan-first-codex
```

Use it before installing, committing, or sharing generated workflow outputs.

`forma verify` checks structure and methodology rules. It does not replace
profile review or product judgment. See [Verifier](./verifier.md) for the
verification boundary.

### `forma create-bundle`

Composes the canonical methodology and a resolved tracked profile into a
target-specific workflow bundle:

```bash
forma create-bundle --target codex --output /tmp/forma-codex-bundle
```

Required options:

- `--target codex|claude-code`
- `--output <dir>`

Optional inputs:

- `--profile <file>`: top-level tracked profile. If omitted, Forma emits the
  generic Plan-First skills with `forma-plan`,
  `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand`.

Optional development override:

- `--methodology <dir>`: use a source methodology directory instead of packaged runtime assets.

Profile format is documented in [Profile Schema](./profile-schema.md).

### `forma create-plugin`

Builds a local plugin output from a profile. Currently plugin output is
Codex-only:

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
```

The output root contains `.codex-plugin/plugin.json`, root
`.forma-manifest.json`, and `skills/<skill-id>/` directories. It does not emit
`dist/skill-bundles` or any sibling bundle output.

For a tracked profile, the Codex plugin id is the profile `bundle.name`. The
plugin display name is derived from the same value, and `plugin.json` points to
the nested `./skills/` directory. Nested skill names follow the emitted skill
names in `.forma-manifest.json`. If a profile renames skills with
`stages.<stage>.name`, the plugin exposes those renamed skills.

Required options:

- `--target codex`
- `--output <dir>`

Optional inputs:

- `--profile <file>`: top-level tracked profile. If omitted, the plugin exposes
  `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and
  `forma-showhand`.

`--target claude-code` fails clearly because Claude Code plugin output is not
supported.

### `forma build-creator`

Builds a target-specific installable `forma-creator`:

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

Required options:

- `--target codex|claude-code`
- `--output <dir>`

Optional development override:

- `--source <dir>`: use a source `forma-creator` directory instead of packaged runtime assets.

Each generated `forma-creator` has a fixed target contract. A Codex creator
generates Codex-shaped skill bundles and can emit Codex plugin outputs when
the fixed target contract allows it. A Claude Code creator generates Claude
Code-shaped skill bundles only. See [Forma Creator](./forma-creator.md)
for the agent-side generation path.

### `forma install`

Installs a verified local skill or skill bundle:

```bash
forma install --target codex --scope project /tmp/forma-codex-bundle
forma install --target claude-code --scope user /tmp/forma-claude-code-bundle
```

Required arguments and options:

- `PATH`: local output path; URL download is intentionally not part of this
  command.
- `--target codex|claude-code`
- `--scope user|project`

Overwrite behavior:

- Without `--replace`, existing destination directories are rejected.
- With `--replace`, Forma replaces only the destination outputs selected by
  the verified source.
- Codex plugin install attempts fail with guidance for Codex marketplace setup,
  `codex plugin add <plugin>@<marketplace-name>`, and starting a new thread
  after install.

### `forma explain`

Prints canonical authoring guidance without requiring an agent to inspect Forma
source files:

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

Use this when another agent needs guidance for drafting profiles or temporary
injection. A lightweight profile-drafting flow is: run
`forma explain profile --target codex`, then ask the agent to inspect the
repository, incorporate human input, and propose tracked profile YAML. This
path produces profile source, not a one-off harness.

## Install Targets

Forma emits target-specific skill bundles. `forma install` writes verified
local skill outputs into the matching target location:

| Target | Personal install | Project install |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

Codex plugin outputs are local plugin sources. Add the generated plugin root to
a Codex marketplace first: use a repo marketplace at
`.agents/plugins/marketplace.json`, a personal marketplace at
`~/.agents/plugins/marketplace.json`, or register a separate local marketplace
root path with `codex plugin marketplace add <marketplace-root-path>`. Run
`codex plugin marketplace list` to see available marketplace names and roots.
Then run `codex plugin add <plugin>@<marketplace-name>`, or install it from the
Codex plugin UI. Start a new Codex thread after installing so the plugin skills
are discovered. `<marketplace-name>` is the top-level `name` in
`<marketplace-root-path>/.agents/plugins/marketplace.json`.

For target-specific discovery, metadata, and trust details, see
[Targets](./targets.md).

## Rename Generated Skills

Forma keeps the semantic stages `shape`, `gauge`, `seal`, `pour`, and `flow`,
but generated skill names can use project language.

### Durable profile names

For tracked profiles, set `stages.<stage>`:

```yaml
stages:
  shape:
    name: backend-plan-first-plan-issue
    directory: backend-plan-first-plan-issue
    display_name: Backend Plan-First Plan Issue
  gauge:
    name: backend-plan-first-ground-plan
    directory: backend-plan-first-ground-plan
    display_name: Backend Plan-First Ground Plan
```

Rules:

- `name` is the skill frontmatter name.
- `directory` is the installable skill directory.
- `display_name` is the target-surface display label.
- `name` and `directory` must be lower kebab-case.
- Semantic stage keys remain `shape`, `gauge`, `seal`, `pour`, and `flow`.
- When the same profile is used with `forma create-plugin`, the plugin id stays
  `bundle.name` and the nested plugin skills follow the renamed emitted skills.

### One-off creator names

For agent-side generation through `forma-creator`, do not hand the agent a JSON
file. Tell the agent the naming intent in natural language. The creator should
classify that request and write the temporary injection internally.

Example prompt:

```text
Use forma-creator to generate this workflow with the prefix `backend-plan-first`.
Name the planning skill `backend-plan-first-plan-issue` and the showhand skill
`backend-plan-first-showhand`. Derive the other skill names from the prefix.
Show the proposed names before generation, then verify the generated bundle.
```

Rules:

- The creator-generated injection should use `rename.prefix` to produce `<prefix>-plan`, `<prefix>-ground`, `<prefix>-lock`, `<prefix>-execute`, and `<prefix>-showhand`.
- The creator-generated injection should use `rename.stages` only when overriding individual stage names.
- Internal injection maps use internal stage keys (`shape`, `gauge`, `seal`, `pour`, `flow`), not public skill ids such as `forma-plan` or `forma-showhand`.
- Names must be unique kebab-case strings and must not be bare stage names like `shape` or `flow`.
- Creator injections do not accept profile-style `stages.shape.name`. Durable names belong in profiles; one-off names belong in `rename`.
- For Codex plugin output from `forma-creator`, `rename.prefix` also becomes
  the plugin id. Without a prefix, the plugin id remains `forma`.

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

- `source/methodology/`: canonical plan-first methodology used to emit task-level workflow skills.
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
- [Profile Schema](./profile-schema.md): durable workflow source format.
- [Forma Creator](./forma-creator.md): agent-side one-off generation.
- [Verifier](./verifier.md): verification checks and limits.
- [Targets](./targets.md): target install and metadata behavior.
