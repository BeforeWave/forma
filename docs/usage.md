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
| Choose the agent-facing Forma CLI route | `forma explain agent --format human|agent|json --target codex` | Start here when an agent needs to choose between profile authoring, stage guidance, temporary injection, doctor/init, build, verify, drift, install, creator, or profile adoption. |
| Read or hand off profile authoring rules | `forma explain profile --format human|agent|json --target codex` | Use only after `forma explain agent` routes the work to profile authoring. It does not inspect the repo or create a draft; the agent combines this guidance with project facts before proposing profile rules. |
| Compare candidate rules with stage methodology | `forma explain stage <stage> --format human|agent|json --target codex` | Use after candidate profile rules identify touched stages and before writing profile files. Omit rules already owned by base methodology, or propose a methodology change when the base contract is weak. |
| Build a skill bundle from a reviewed tracked profile | `forma build bundle --target <target> --profile <profile.yaml> --output <dir>` | Use generation `target` as `codex`, `claude-code`, or `opencode`; human output is a concise artifact result. Use `--format agent` or `--format json` when another agent or tool needs structured next actions. |
| Build the default Plan-First skill bundle | `forma build bundle --target <target> --output <dir>` | Use generation `target` as `codex`, `claude-code`, or `opencode`; run `forma verify <dir>`, then install with the matching target. |
| Build plugin source | `forma build plugin --target codex|claude-code --profile <profile.yaml> --output <dir>` | Human output is a concise artifact result. Use `--format agent` or `--format json` for install handoff; Codex plugins install through Codex, and Claude Code plugin roots install with `forma install --target claude-code`. |
| Diagnose repo agent-operability | `forma doctor [path] --format human|agent|json` | Read-only check for agent entrypoints, source boundaries, validation contracts, setup contracts, task state, human gates, noise control, and optional agent integrations. |
| Initialize deterministic Forma source from repo facts | `forma init [path] --from-report <report> --format human|agent|json` | Dry-run remediation by default; use `--apply` to create `.forma/` workflow source plus report-derived Agent handoff files. |
| Build optional creator for on-the-spot generation | `forma build creator --target <target> --output <dir>` | Use only for the creator path; run `forma verify <dir>/<target>/forma-creator`, then install with the matching target. |
| Give an agent temporary-injection rules | `forma explain temporary-injection --target codex` | Use only for optional creator/on-the-spot generation flows. |

When a reviewed profile is stored in a directory, check that profile directory.
If it contains `reinstall-workflow.sh`, run that profile-local
script before falling back to hand-composed `forma build`, `forma verify`,
`forma drift`, `forma install`, marketplace refresh, or Codex plugin commands.
Profile-backed `forma build bundle` and `forma build plugin` expose the
profile-local reinstall state and structured next actions through
`--format agent` and `--format json`. Default `human` output stays concise so it
can be used inside profile-local scripts without printing agent handoff text.
If the script is missing or still bootstrap-incomplete, the agent must settle
the install facts with the user and complete the script before reporting a
reusable reinstall flow. Fixed-fact reinstall scripts should encode artifact
kind, target, plugin id when relevant, marketplace source when relevant, install
selector, and visibility check.
See `forma explain agent` for the agent-side bootstrap and reuse rules for that
process.

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
- If the artifact install route is ambiguous, use the build command's
  `--format agent|json` handoff and the install boundary below; `doctor` is for
  repository agent-operability, not generated artifact inspection.

`forma verify` checks structure and methodology rules. It does not replace
profile review or product judgment. See [Verifier](./verifier.md) for the
verification boundary.

Use `--json` when another tool or agent needs structured output. The JSON report
keeps the same exit code contract and includes semantic failure classes for each
reported rule result.

Use `--format human|agent|json` on commands that emit structured handoff output,
such as `doctor`, `init`, selected `build` commands, and `explain`. The
`human` renderer stays concise and suppresses agent-only handoff details;
`agent` includes executable next actions, stop conditions, and forbidden
actions; `json` is for tools. The command shape is shared, but the content is
command-specific: `doctor` reports findings and evidence, while `explain`
reports authoring guidance and handoff rules.

### `forma doctor [path]`

Runs a read-only repository agent-operability check:

```bash
forma doctor
forma doctor --format json /path/to/repo
forma doctor --format agent /path/to/repo
```

It reports whether a new Agent can understand what to read, what can change,
what must not change, how to validate, when to ask a human, and where to hand
off task state and evidence. Core readiness is based on repository
agent-operability contracts. Forma profile presence is an optional integration
signal, not a readiness prerequisite.

The JSON renderer emits a repo-doctor schema with `facts`, `findings`,
`evidence`, `confidence`, `programmatic_actions`, `agent_handoffs`,
`human_decisions`, and `unsafe_blockers`. Adoption guidance inside `facts`
uses `owner_confirmations` for the approval points around profile refinement,
build/verify, install target/scope, and commit. Use the report as input to
`forma init --from-report`.

### `forma init [path]`

Plans deterministic remediation for a repository:

```bash
forma init
forma init --format agent
forma doctor --format json . > /tmp/forma-doctor.json
forma init --from-report /tmp/forma-doctor.json
forma init --apply
forma init --from-report /tmp/forma-doctor.json --apply
```

Default mode is a dry run. With `--apply`, Forma creates missing deterministic
workflow source files under a git-trackable `.forma/` directory:
`.forma/profile.yaml`, `.forma/reinstall-workflow.sh`, and `.forma/.gitignore`.
The `.gitignore` ignores only `/state/`, so profile source and reinstall
workflow stay trackable while runtime workflow state lives under `.forma/state/`.
When `--from-report` is provided, init also materializes
`.forma/agent-operability/doctor-report.json`,
`.forma/agent-operability/agent-handoff.md`, and
`.forma/agent-operability/human-decisions.md`.

These are draft project workflow source and handoff files. `forma init` does
not claim the profile has been reviewed, does not approve semantic repo rules,
and does not make the repo agent-friendly by itself. Agents can use the
report-derived handoff plus profile-authoring principles to propose remediation,
but owner confirmations remain separate for profile approval, build/verify,
install target/scope, and committing workflow source. The generated
`reinstall-workflow.sh` is bootstrap-incomplete until install facts are
confirmed and written into a fixed-fact script. If a review packet is generated
during profile authoring, ask the user whether to keep it; do not leave it in
the repo by default.

### `forma build bundle`

Composes the methodology and a resolved tracked profile into a target-specific
workflow bundle:

```bash
forma build bundle --target codex --output /tmp/forma-codex-bundle
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
bundle with `forma install`. For profile-backed output, default `human` output
stays concise; use `--format agent` when an agent needs the structured next
actions. If the profile directory contains `reinstall-workflow.sh`, run that
script before reconstructing build/install commands. If it is missing, that is a
bootstrap state, not a reusable manual install path.

Profile format is documented in [Profile Schema](./profile-schema.md).

### `forma build plugin`

Builds a local plugin output from a profile:

```bash
forma build plugin --target codex --output /tmp/forma-codex-plugin
forma build plugin --target claude-code --output /tmp/forma-claude-code-plugin
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
During bootstrap discovery or diagnostics, inspect configured marketplaces as
needed, ask the user to confirm the plugin id, marketplace name, marketplace
source, install selector, and visibility check, ensure the confirmed marketplace
catalog points to the generated plugin root, then install with a confirmed
`<plugin-id>@<marketplace>` selector. Stable profile-local reinstall scripts
should not list marketplaces or leave plugin id, marketplace, selector, or
source refresh decisions open at runtime.

Install Claude Code plugin roots with
`forma install --target claude-code --scope user|project <output-dir>`.

### `forma build creator`

Builds a target-specific installable `forma-creator`. This is the optional
on-the-spot path for generating a workflow without handling a profile file
first:

```bash
forma build creator --target codex --output /tmp/forma-creator-dist
forma build creator --target opencode --output /tmp/forma-creator-dist
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

Prints agent-facing command guidance and narrower authoring guidance without
requiring an external agent to read Forma source files:

```bash
forma explain agent --target codex
forma explain profile --target codex
forma explain stage shape --target codex
forma explain profile --format agent --target codex
forma explain temporary-injection --format json --target codex
```

`forma explain agent` is the agent-facing command guide for Forma CLI surfaces.
It is the first `explain` command an agent should read when it needs to choose
between profile authoring, workflow generation, plugin output, optional creator
output, profile adoption, drift, doctor, init, verify, or install.

`forma explain profile` is useful both for people and for agents, but the
renderer changes the handoff:

- `--format human` gives a concise reader-facing explanation of what belongs in
  a durable profile and what stays in the current task.
- `--format agent` gives an executable authoring contract: what project facts
  to gather, how to separate durable rules from task-specific work, what files
  may be proposed, and when to stop for user review.
- `--format json` gives tools the same guidance as structured data.

`forma explain profile` does not inspect the repository, create profile files,
or claim a profile has been reviewed. Use `forma init --apply` when
deterministic workflow source files are needed, then combine
`forma explain profile` with project facts to draft rules for human review.

Before writing profile files, run `forma explain stage <stage>` for every stage
touched by the candidate rules. Stage guidance lets the agent compare candidate
profile rules against the base methodology: omit rules already owned by the
base stage contract, keep only durable project adaptations in the profile, and
propose a methodology change when the base contract is weak or missing.

When another agent needs to draft a profile or temporary injection, use this
command family to give it the rules. For the normal profile-first path, you can
simply say:

```text
Use Forma to generate a Codex workflow for this project.
Show me the project rules you extracted first; after I approve them, generate and install it.
```

The agent starts with `forma explain agent --target codex`, then uses
`forma explain profile --target codex` to load the authoring standard. After it
combines that guidance with project facts, it uses `forma explain stage <stage>`
for each touched stage before proposing profile YAML. Commit that profile only
when the rules need long-term reuse.

Next action: after the profile is reviewed, use `forma build bundle` for a
skill bundle or `forma build plugin` for plugin source.

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
`forma build bundle --target opencode`, verify it, then install it with
`forma install --target opencode`. Forma does not emit OpenCode JS/TS runtime
plugin output.

Codex plugin outputs are local plugin sources. Forma does not install Codex
plugins. During bootstrap discovery or diagnostics, inspect configured
marketplaces as needed, confirm the plugin id, marketplace name, marketplace
source, install selector, and visibility check with the user, then run
`codex plugin add <confirmed-plugin-id>@<confirmed-marketplace>` or install it
from the Codex plugin UI. Start a new Codex thread after installing so the
plugin skills are discovered. Stable profile-local reinstall scripts should use
confirmed facts rather than marketplace discovery.

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
- When the same profile is used with `forma build plugin`, the plugin id stays
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
python -m pytest -p no:cacheprovider tests/
git diff --check
```

## Source Layout

- `source/methodology/`: methodology used to emit task-level workflow skills.
- `source/skill-creator/`: self-contained `forma-creator` source with bundled references, creator script, and verifier.
- `src/forma/`: Python CLI, profile compiler, runtime asset resolver, and target emitters.
- `.forma/`: Forma-owned profile stack for this repository.
- `examples/profiles/`: profile examples.
- Generated sample outputs are built locally when needed, not committed.
- `tests/`: verifier, creator, runtime asset, profile, and CLI behavior tests.

See [Repository Structure](../STRUCTURE.md) for the detailed tree map.

## Installed CLI Behavior

Packaged Forma commands use `forma.assets` runtime assets by default. Source
paths are development overrides only:

- `forma build bundle` and `forma build plugin` use packaged methodology unless `--methodology` is provided.
- `forma install` only installs verified local outputs; it does not download URLs.
- `forma build creator` uses packaged creator source unless `--source` is provided.
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
