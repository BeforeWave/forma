# Forma

Build plan-first AI skill suites with a verified shape.

中文文档：[README.zh-CN.md](./README.zh-CN.md)

## What this is

Forma is a plan-first AI skill creator. It ships three architectural layers:

- **Layer 1 — Instruction**: a self-contained meta skill source at
  `source/skill-creator/`. It contains `SKILL.md`, bundled references, and the
  verifier scripts an agent uses after scaffolding a suite.
- **Layer 2 — Verification**: a stdlib-only verifier implemented inside Layer
  1 at `source/skill-creator/scripts/forma_verifier/`. The same package is also
  importable by the developer `forma verify` CLI.
- **Layer 3 — Generation**: a developer creator package under
  `src/forma/creator/` exposed as `forma create`. It composes
  `source/methodology/` with a tracked profile stack and emits a target-specific
  Mode-S skill suite.

The methodology that underpins all three layers is **plan-first**: an
executable plan converges Goal, Scope, Approach, Validation, and Plan Strategy
before any implementation begins; each task carries its own acceptance and
validation contract; evidence lives next to the plan it proves.

Layer 2 intentionally ships inside Layer 1's meta source. The creator builder
generates target-specific `forma-creator` install bundles from that source.
Each installed creator is single-target: the Codex creator emits Codex-format
`shape` / `gauge` / `seal` / `pour` / `flow` skills, while the Claude Code
creator emits Claude Code-format skills.

Layer 1 source does not duplicate the canonical plan-first methodology tree.
`source/methodology/` is the only checked-in methodology/resource source of
truth. Stage bodies live under `source/methodology/stages/`; fixed copied
resources live under `source/methodology/resources/`, with identical shared
resources kept once under `source/methodology/resources/shared/`. `forma
build-creator` copies the full tree into the generated creator bundle at
`resources/plan-first/methodology/` so the installed creator remains
self-contained.

Stage bodies may include source-only fragments from
`source/methodology/fragments/` for concepts such as Decision Gate, Plan
Strategy, task structure, and runner behavior. The developer composer expands
those fragments before emission. Short stage workflow guidance stays in the
generated `SKILL.md`; longer canonical requirement blocks are emitted as
stage-local generated references such as
`references/proposal-decision-gate.md`, `references/task-structure.md`, and
`references/task-runner.md`. The source fragment files themselves are not
copied into generated suites.

Generated suites keep each skill self-contained. Shared source resources are
copied into each generated skill that needs them using the same destination
names, such as `references/output-format.md` and
stage-specific `references/planning-rules.md` or
`references/execution-rules.md`. Generated requirement references also live
inside the same skill's own `references/` directory.

There are two authoring paths:

- **Installed creator path**: an installed `forma-creator` may accept one-off
  user constraints during an agent interaction, embed them into a generated
  five-skill bundle, run Layer 2 verification, and install or hand off the
  result. Those one-off constraints are not tracked by Forma unless promoted
  into a profile file. The creator supports either ordinary unconditional
  injection or optional `conditional_overlays`; Forma does not hardcode route
  names such as language, backend, or product categories.
- **Tracked profile path**: `forma create --target ... --profile ...` resolves
  a committed profile file and its includes, then produces a repeatable target
  bundle. Profiles may use the same `conditional_overlays` structure when a
  tracked, reproducible route decision is needed. Agents may help draft
  profiles, but profile files should be reviewed by a person before they become
  durable source.

Forma's own examples are sanitized. Real downstream profiles with
organization-specific workflow commands, private paths, credentials, or
business rules should live in the owning downstream repository, not in Forma's
example tree.

## Install

Recommended development path with uv:

```bash
uv run --extra dev forma --help
```

Equivalent editable install path:

```bash
pip install -e ".[dev]"
forma --help
```

`forma` exposes:

- `forma verify <path>` — run Layer 2 against a skill bundle or generated suite.
- `forma create --target <agent> --profile <file> --output <dir>` — generate a
  target-specific Mode-S plan-first suite from the canonical methodology plus a
  resolved profile stack.
- `forma build-creator --source <dir> --output <dir> --target <agent>` —
  generate target-fixed Codex and Claude Code `forma-creator` install bundles
  from the meta source, injecting the canonical methodology resources at build
  time.

## Verify

Verify Forma's Layer 1 meta skill source:

```bash
uv run --extra dev forma verify source/skill-creator/
```

Verify the committed generated backend example:

```bash
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-claude-code/
```

Run the test suite:

```bash
uv run --extra dev pytest -p no:cacheprovider tests/
```

## Generate

Generate sanitized sample backend suites:

```bash
uv run --extra dev forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go.yaml \
  --output /tmp/sample-backend-go-plan-first-codex
uv run --extra dev forma create \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go.yaml \
  --output /tmp/sample-backend-go-plan-first-claude-code
uv run --extra dev forma verify /tmp/sample-backend-go-plan-first-codex
uv run --extra dev forma verify /tmp/sample-backend-go-plan-first-claude-code
```

The committed drift baselines for those commands live at
`examples/generated/sample-backend-go-plan-first-codex/` and
`examples/generated/sample-backend-go-plan-first-claude-code/`.

Generate sanitized sample software suites:

```bash
uv run --extra dev forma create \
  --target codex \
  --profile examples/profiles/sample-software/sample-software-plan-first.yaml \
  --output /tmp/sample-software-plan-first-codex
uv run --extra dev forma create \
  --target claude-code \
  --profile examples/profiles/sample-software/sample-software-plan-first.yaml \
  --output /tmp/sample-software-plan-first-claude-code
uv run --extra dev forma verify /tmp/sample-software-plan-first-codex
uv run --extra dev forma verify /tmp/sample-software-plan-first-claude-code
```

`examples/profiles/sample-software/` is a profile-only sample. It demonstrates
a generic software plan-first workflow with Chinese collaboration wording,
Impact Profile / Impact Boundary decisions, read-only grounding, sealed
planning, review-gated implementation, and safe automatic execution. It does
not have committed generated drift baselines in this issue.

## Manage Forma Itself

Forma also keeps project-owned profiles for managing its own development
iterations:

```bash
uv run --extra dev forma create \
  --target codex \
  --profile profiles/forma-self/forma-self-iteration.yaml \
  --output /tmp/forma-iteration-codex
uv run --extra dev forma create \
  --target claude-code \
  --profile profiles/forma-self/forma-self-iteration.yaml \
  --output /tmp/forma-iteration-claude-code
uv run --extra dev forma verify /tmp/forma-iteration-codex
uv run --extra dev forma verify /tmp/forma-iteration-claude-code
```

`profiles/forma-self/` is not a public sample. It is Forma's own tracked
self-iteration profile stack, with conditional `Iteration Area` routes for
docs-only, methodology/verifier, creator/profile, generated-baseline, and
cross-layer work. It still emits the canonical `forma-shape`, `forma-gauge`,
`forma-seal`, `forma-pour`, and `forma-flow` skill names; self-iteration is a
profile behavior, not a generated skill-name prefix.

## Install Layer 1 Into An Agent

Generate target-specific `forma-creator` install bundles from the meta source:

```bash
uv run --extra dev forma build-creator \
  --source source/skill-creator \
  --output /tmp/forma-creator-dist \
  --target codex
uv run --extra dev forma build-creator \
  --source source/skill-creator \
  --output /tmp/forma-creator-dist \
  --target claude-code
```

Then install the generated creator for the target agent:

```bash
mkdir -p ~/.codex/skills ~/.claude/skills
cp -R /tmp/forma-creator-dist/codex/forma-creator ~/.codex/skills/
cp -R /tmp/forma-creator-dist/claude-code/forma-creator ~/.claude/skills/
```

After installation, the creator uses its injected
`references/agent-target.md` as the hard output contract for generated
plan-first skills, and its injected
`resources/plan-first/methodology/` tree as the fixed plan-first source. It
should run
`forma-creator/scripts/verify.py <generated-suite>` before reporting success.
No pip install is required for that agent-side verification path.

## License

MIT — see [LICENSE](./LICENSE).
