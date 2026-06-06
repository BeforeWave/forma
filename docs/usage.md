# Usage

Chinese version: [usage.zh-CN.md](./usage.zh-CN.md)

This page is the command and profile reference for Forma.

For a first run, start with [Quick Start](./quick-start.md).

---

## Commands

### `forma verify <path>`

Verifies a plan-first skill suite or `forma-creator` bundle:

```bash
forma verify /tmp/backend-plan-first-codex
```

Use it before installing, committing, or sharing generated bundles.

---

### `forma create`

Composes the canonical methodology and a resolved tracked profile into a target-specific workflow bundle:

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
```

Required options:

- `--target codex|claude-code`
- `--profile <file>`
- `--output <dir>`

Optional development override:

- `--methodology <dir>`: use a source methodology directory instead of packaged runtime assets.

---

### `forma build-creator`

Builds a target-specific installable `forma-creator`:

```bash
forma build-creator \
  --target codex \
  --output /tmp/forma-creator-dist
```

Required options:

- `--target codex|claude-code`
- `--output <dir>`

Optional development override:

- `--source <dir>`: use a source `forma-creator` directory instead of packaged runtime assets.

---

### `forma explain`

Prints canonical authoring guidance without requiring an agent to inspect Forma source files:

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

Use this when another agent needs guidance for drafting profiles or temporary injection.

---

## Install Targets

Forma emits target-specific bundles. Copy the generated skill directories into the matching target location:

| Target | Personal install | Project/team install |
|---|---|---|
| Codex | `$HOME/.agents/skills` | `.agents/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

For Codex, project skills can live under `.agents/skills` in the current working directory, parent directories, or repository root.

For Claude Code, project skills live under `.claude/skills`.

Review project skills before trusting them because skills can include scripts and target-specific tool behavior.

---

## Profile Schema

Tracked profiles are strict YAML source.

Unknown top-level or nested keys are rejected so a profile cannot silently bypass the workflow contract.

Allowed top-level keys:

| Key | Purpose |
|---|---|
| `profile` | Stable `id` and optional human description. |
| `includes` | Relative paths or profile ids resolved before the local file. |
| `bundle` | Review-facing bundle `name` and `description`. |
| `org` | Optional owning organization or team name. |
| `stages` | Per-stage installable names, directories, display labels, prompts, and `enabled` flags for `shape`, `gauge`, `seal`, `pour`, and `flow`. |
| `resources` | Stage resources copied into generated skills as `references`, `scripts`, or `files`. |
| `skills` | Per-stage trigger descriptions without changing stage semantics. |
| `terminology` | Project vocabulary emitted into generated skill guidance. |
| `validation_commands` | Default or stage-specific validation commands. |
| `decision_gate_extras` | Extra dimensions `shape` must settle. |
| `constraints` | Default or stage-specific workflow requirements. |
| `conditional_overlays` | Route-specific constraints, resources, and validation that activate only after the plan records the selected route. |

Keep `constraints.default` light.

Put rules where they belong:

| Stage | Use for |
|---|---|
| `constraints.shape` | planning strategy, demand clarification, route, scope, and unresolved decisions |
| `constraints.gauge` | grounding and evidence collection |
| `constraints.seal` | plan materialization, accepted tasks, validation contracts |
| `constraints.pour` | current-task execution and proof |
| `constraints.flow` | safe continuation boundaries |

---

## Generated Skill Quality

Forma should generate workflow skills, not one giant policy prompt copied five times.

Keep generated suites aligned with these expectations:

- each skill has one clear stage job;
- `description` explains when to use the skill without becoming a runbook;
- `SKILL.md` carries the standing instructions for that stage;
- larger stable guidance lives in `references/`;
- source readers and helper scripts appear only when selected by a profile or temporary injection;
- broad rules live in conditional overlays instead of `constraints.default`;
- every executable stage points to the relevant validation or proof path.

Run verification after renames, profile changes, temporary injection, or target changes:

```bash
forma verify <generated-suite-dir>
```

---

## Rename Generated Skills

Do not like `shape`, `gauge`, `seal`, `pour`, and `flow` as installable names?

Forma keeps those five stage semantics, but generated skill names can use project language.

There are two paths.

### Durable profile names

For durable tracked profiles, set `stages.<stage>`:

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
- Semantic stage keys remain `shape`, `gauge`, `seal`, `pour`, and `flow`; do not rename the keys themselves.

### One-off creator names

For agent-side generation through `forma-creator`, use `rename` in the one-off injection:

```json
{
  "rename": {
    "prefix": "backend-plan-first",
    "stages": {
      "shape": "backend-plan-first-plan-issue",
      "flow": "backend-plan-first-showhand"
    }
  }
}
```

Rules:

- `rename.prefix` produces `<prefix>-shape`, `<prefix>-gauge`, `<prefix>-seal`, `<prefix>-pour`, and `<prefix>-flow`.
- `rename.stages` overrides individual stage names.
- Names must be unique kebab-case strings and must not be bare stage names like `shape` or `flow`.
- Creator injections do not accept profile-style `stages.shape.name`. Durable names belong in profiles; one-off names belong in `rename`.

After renaming, verify the generated suite:

```bash
forma verify <generated-suite-dir>
```

The verifier checks that the manifest, directories, and `SKILL.md` frontmatter agree.

---

## Repository Checks

For Forma repository maintenance, run the main checks from the repository root after editable dev installation:

```bash
forma verify source/skill-creator/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
python -m pytest -p no:cacheprovider tests/
git diff --check
```

---

## Source Layout

- `source/methodology/`: canonical plan-first methodology used to emit `shape`, `gauge`, `seal`, `pour`, and `flow`.
- `source/skill-creator/`: self-contained `forma-creator` source with bundled references, creator script, and verifier.
- `src/forma/`: Python CLI, profile compiler, runtime asset resolver, and target emitters.
- `profiles/forma-self/`: Forma-owned profile stack for this repository.
- `examples/profiles/`: sanitized profile examples.
- `examples/generated/`: committed generated baselines for drift checks.
- `tests/`: verifier, creator, runtime asset, profile, and generated-baseline tests.

See [Repository Structure](../STRUCTURE.md) for the detailed tree map.

---

## Installed CLI Behavior

Packaged Forma commands use `forma.assets` runtime assets by default.

Source paths are development overrides only:

- `forma create` uses packaged methodology unless `--methodology` is provided.
- `forma build-creator` uses packaged creator source unless `--source` is provided.
- `forma explain` renders canonical guidance from packaged references.

This keeps pip or pipx installed CLI behavior independent of the source checkout.
