# Quick Start

This page shows the shortest path from an existing profile to a verified,
installed workflow bundle.

Chinese version: [quick-start.zh-CN.md](./quick-start.zh-CN.md)

## Install Forma

For editable local installation from the repository checkout:

```bash
pip install -e ".[dev]"
forma --help
```

After installation, use the `forma` command directly. The examples below assume
`forma` is available on `PATH`.

If Forma is already installed, check that the CLI is available:

```bash
forma --help
```

## Install Locations

Generated bundles can be installed for one user or checked into a project:

| Target | Personal install | Project/team install |
|---|---|---|
| Codex | `$HOME/.agents/skills` | `.agents/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

Review project or team skills before trusting them. A skill can include scripts
and target-specific permissions.

## First Successful Run

Do this once before designing a large profile:

1. Generate from a small sample profile.
2. Verify the generated bundle.
3. Install it into one target agent.
4. Trigger one plan-first task in that agent.
5. Inspect the plan, task contract, validation result, and run evidence.
6. Only then adjust the profile.

## Ask An Agent To Draft A Profile

Inside a downstream project with Forma installed, tell the agent:

```text
Run:
  forma explain profile --target codex

Use that output as the profile authoring standard.
Inspect this repository and propose a tracked Forma profile.
Show the profile structure before writing files.
Explain each constraint placement and mark unknowns explicitly.
```

## Path 1: Generate From A Tracked Profile

Use this path for durable team or project rules that live in a reviewed profile.

Generate a Codex workflow:

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

Install it into Codex:

```bash
mkdir -p ~/.agents/skills
cp -R /tmp/backend-plan-first-codex/* ~/.agents/skills/
```

Then start Codex in a repository and ask for a planned task using the generated
workflow names. For the sample backend profile, a natural first test is:

```text
Use backend-plan-first-plan-issue to turn this change request into a bounded plan:
add one narrow validation check for the current repository's docs.
Do not implement yet.
```

Generate a Claude Code workflow from the same profile:

```bash
forma create \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-claude-code

forma verify /tmp/backend-plan-first-claude-code
```

Install it into Claude Code:

```bash
mkdir -p ~/.claude/skills
cp -R /tmp/backend-plan-first-claude-code/* ~/.claude/skills/
```

In Claude Code, invoke the corresponding generated skill directly or ask a
matching natural-language request. Project skills require trusting the workspace
before skill-owned tool permissions can apply.

## Path 2: Generate With `forma-creator`

Use this path for reviewed one-off natural-language constraints. The installed
creator classifies those constraints into temporary injection JSON, generates a
target-specific workflow bundle, and verifies the output before handoff.

Build a Codex creator:

```bash
forma build-creator \
  --target codex \
  --output /tmp/forma-creator-dist

forma verify /tmp/forma-creator-dist/codex/forma-creator
```

Install it into Codex:

```bash
mkdir -p ~/.agents/skills
cp -R /tmp/forma-creator-dist/codex/forma-creator ~/.agents/skills/
```

Build a Claude Code creator:

```bash
forma build-creator \
  --target claude-code \
  --output /tmp/forma-creator-dist

forma verify /tmp/forma-creator-dist/claude-code/forma-creator
```

Install it into Claude Code:

```bash
mkdir -p ~/.claude/skills
cp -R /tmp/forma-creator-dist/claude-code/forma-creator ~/.claude/skills/
```

Each generated `forma-creator` has a fixed target contract. A Codex creator
generates Codex-shaped plan-first workflow bundles. A Claude Code creator
generates Claude Code-shaped bundles.

After installation, you can quickly try workflow constraints inside the agent:

```text
Use forma-creator to generate a Plan-First workflow bundle from these workflow constraints:
- shape must identify source of truth and unresolved decisions;
- gauge must read only evidence needed for the selected scope;
- seal must put acceptance and validation into every executable task;
- pour must execute one accepted task at a time and record proof;
- flow must stop on cross-layer work unless the sealed plan allows continuation.
Show how these constraints are classified before generation.
Verify the generated bundle before reporting success.
```

## Profile And Injection Guidance

Ask Forma for agent-readable authoring guidance:

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

Use tracked profiles for stable rules. Use temporary injection for one-off
rules that should not become durable project source.
