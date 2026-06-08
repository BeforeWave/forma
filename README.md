# Forma

**Start with one sentence, then compile static project rules into custom task workflows.**

Forma compiles project rules into custom task workflows. For each task, the generated workflow turns rules into concrete boundaries, validation steps, and proof.

AI coding is the first target because code has clear sources, tests, diffs, and review proof. The same model can fit other repeatable work with sources, boundaries, validation, and proof.

Unlike a fixed workflow tool, Forma generates the workflow from project or task rules instead of installing one preset process.

It works in three layers:

```text
Layer 0 — Project Profile
With Forma, the agent helps turn repository evidence and human input into a project profile:
rules, boundaries, validation requirements, review expectations, risky areas, and evidence sources.

        ↓ compiled by Forma

Layer 1 — Workflow Harness
Forma compiles these rules into a project-specific skill bundle or plugin.
The harness guides the agent:
plan → ground → lock → execute → record proof

        ↓ executed by the agent

Layer 2 — Task Execution
For each development task, the rules become concrete, repository-specific obligations:
- this task is grounded on `File A`, `File B`, and `Issue C`
- it may touch `Module X`, but must not touch `Generated File Y`
- it is complete only when behavior `Z` works through path `P`
- it must be verified with `Command M` and `Test N`
- `Proof R` must be recorded before proceeding
```

**Use Forma when you need static project rules to become reviewable files, boundaries, commands, tests, and proof alongside the final patch.**

[中文文档](./README.zh-CN.md)

---

## Why Forma Exists

Coding agents can generate code quickly.

The harder problem is making them work by the rules of a specific project.

Most projects already have rules:

```text
Read relevant implementation before planning.
Behavior changes require nearby tests.
Keep public APIs compatible.
Risky changes require review.
Record validation proof before finishing.
```

These rules are valuable, but they are usually principle-level rules.

Project docs, architecture notes, `AGENTS.md`, and review guidelines mostly describe “what this project is like” and “which principles work should follow.” They can give an agent the right direction, but they do not automatically translate a concrete change into:

```text
Which file should be read first.
Where this plan item may change code, and where it must not.
Which test validates the behavior change.
Which source should regenerate the generated file.
Which output counts as proof.
Which uncertainty must stop execution and go back to the user.
```

The result: the agent has read the principles, but when it starts changing code, it still improvises under those principles.

Forma exists to close that gap.

It compiles project rules into a Plan-First workflow harness, then lets that harness turn the principles into concrete boundaries, validation steps, and proof requirements for each development task.

For example, a static rule like this:

```text
Do not edit generated files directly.
After changing source, regenerate outputs and run the relevant validation.
```

needs to become a task-level contract:

```text
Task 002 — Update the generated schema source
- Evidence: read `schema/source.yaml`, the generator entrypoint, and nearby schema tests first.
- Boundary: this task may edit `schema/source.yaml` and its tests; it must not hand-edit `schema/generated.json`.
- Command: run `make generate-schema` and the schema validation command recorded in `tasks.md`.
- Validation gate: generated output must come only from the source change, and schema validation must pass.
- Proof: record the generation command, validation output, and generated diff in `plans/issue-<id>/runs/task-002.md`.
```

That is the level Forma pushes static rules down to: concrete evidence, concrete boundaries, concrete commands, validation gates, and proof.

---

## What Forma Installs

Forma installs four core Plan-First workflow skills, plus `forma-showhand` for continuous execution.

| Skill | Purpose |
|---|---|
| `forma-plan` | Clarify the development goal, scope, risks, acceptance criteria, strategy, and unresolved decisions. |
| `forma-ground` | Gather repository evidence from code, docs, issues, tests, fixtures, and project references. |
| `forma-lock` | Lock the execution contract: concrete boundaries, task order, validation, and review expectations. |
| `forma-execute` | Execute one accepted task at a time, record proof, and surface drift or blockers. |

`forma-showhand` is the continuous `forma-execute` candy skill, not a separate stage. Once review is done, the plan is locked, and the harness constraints are solid, show hand and let the agent enter autopilot, keep moving along the locked plan, and leave proof all the way.

Not into the names? Rename them. They are defaults.

The important part is the generated workflow: project principles live inside the skills the agent invokes while working on development goals.

---

## Quick Try

The fastest way to feel Forma is to make an agent produce a plan and proof for a real development goal before it writes the patch.

### 1. Try the default Plan-First workflow

Install the CLI:

```bash
pipx install git+https://github.com/BeforeWave/forma.git
```

Create the Codex plugin:

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
```

Then add that local plugin to a Codex marketplace and install it with
`codex plugin add <plugin>@<marketplace>`, or install it from the Codex plugin
UI.

Send the current issue or task context to the agent and ask it to use `forma-plan` first:

```text
Use forma-plan to plan this issue first.

Issue:
<paste the current issue, problem context, or task goal here>
```

The first result should be a chat-level proposal or handoff, not a patch and not plan files. It should settle the goal, scope, approach, validation model, and whether repository grounding is needed.

If repository evidence is needed, ask the agent to use `forma-ground`.

After the proposal and any grounding are accepted, lock the plan:

```text
Use forma-lock to write the plan and task contract.
```

You should then see a task-specific plan:

```text
plans/issue-<id>/plan.md
plans/issue-<id>/tasks.md
```

The Forma workflow should sort out, ask for, or lock down the necessary details: which files ground the task, what is in or out of bounds, how each task is accepted, which command or test validates it, and what proof must be recorded before execution continues.

Then execute the next accepted task:

```text
Use forma-execute to execute the next accepted task.
```

The run should leave proof under:

```text
plans/issue-<id>/runs/<task-id>.md
```

The first thing to check is whether the agent leaves a plan, boundaries, validation, and proof instead of only a patch.

### 2. Shape a project-specific harness conversationally with forma-creator

To quickly create a project-specific harness, install the creator skill:

```bash
forma build-creator --target codex --output /tmp/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

Then talk to Codex like you would talk to a collaborator:

```text
Customize a workflow for this repo.

First inspect the repository structure, validation paths, generated outputs, and project conventions.

I care about:
- generated outputs must come from source;
- docs-only changes should use lightweight checks;
- behavior changes should look for nearby tests first;
- risky judgments should stop for my confirmation.
```

The creator skill classifies that conversation into temporary injection, then generates and verifies a one-off harness.

Rules that need reuse belong in a tracked profile. `forma explain profile --target codex` gives an agent the profile authoring standard; after the profile is versioned and reviewed, it can regenerate the harness consistently.

---

## When To Use Forma

Good fits:

- repositories with frequent agent-assisted coding;
- projects with generated files, fixtures, migrations, public APIs, or sensitive data paths;
- teams that need agents to produce reviewable plans and proof;
- workflows where validation differs by task type;
- situations where the agent must stop when scope, evidence, or permission is unclear.

Probably too much for:

- typo fixes;
- one-off summaries;
- tiny edits with obvious scope;
- repositories that only need a few static instructions.

---

## Documentation

- [Usage](./docs/usage.md): commands, install locations, verification, targets, and custom generation.
- [Quick Start](./docs/quick-start.md): first-run walkthrough.
- [Concepts](./docs/concepts.md): mental model and fit.
- [Forma Creator](./docs/forma-creator.md): custom project-specific workflow generation.
- [Profile Schema](./docs/profile-schema.md): durable profile source format.
- [Targets](./docs/targets.md): Codex and Claude Code behavior.
- [Project Structure](./STRUCTURE.md): source tree and ownership boundaries.

---

## Status

Forma is early.

Forma gives agents a better control surface, not a behavioral guarantee. Whether an agent follows generated skills still depends on the model and host. Putting workflow into files, stages, and proof requirements is more reliable than relying on chat memory alone, but it is not a magic guarantee.

The current focus is:

- making Plan-First agent workflows easier to install;
- making project-specific workflow profiles easier to author;
- improving generated bundle verification;
- improving examples that show real planning, execution, validation, and review proof.

Committed generated examples are useful as drift baselines, not proof of runtime agent behavior.

BTW, Forma also uses its own Plan-First workflow for development; this repository’s source profile lives in `profiles/forma-self/`.

---

## License

Apache-2.0. See [LICENSE](./LICENSE).
