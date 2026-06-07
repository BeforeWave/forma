# Forma

**Compile project-specific principles into runtime harnesses for coding agents.**

Forma works in three layers:

- **Layer 0: Build the profile.** Use a profile to define the project's
  long-lived engineering principles and the boundaries agents should
  consistently follow.
- **Layer 1: Generate the workflow.** Forma compiles the profile into a
  project-specific Plan-First workflow skill bundle that carries those
  principles.
- **Layer 2: Runtime harness.** When a concrete development goal appears, the
  agent runs under that workflow: clarify the goal, gather evidence, lock the
  execution contract, execute ordered tasks, record proof, wait for human
  review, and stop when boundaries change.

The skill bundle is the installed output; the runtime harness is how it shapes
the agent's work on a concrete development goal.

Chinese documentation: [README.zh-CN.md](./README.zh-CN.md)

## What Gets Installed

Forma installs a project-specific workflow harness as coordinated skills:

| Skill | Harness job |
|---|---|
| `forma-plan` | Clarify the development goal under the project's principles: scope, risks, acceptance criteria, strategy, and unresolved decisions. |
| `forma-ground` | Gather the evidence this goal needs from the repository, docs, specs, issues, and other project sources. |
| `forma-lock` | Lock the current execution contract: accepted boundaries, ordered tasks, validation, and review expectations. |
| `forma-execute` | Execute one accepted task at a time, record proof, and surface drift or blockers. |

`forma-showhand` is the candy skill for continuous `forma-execute`, not a
separate stage: confident in your harness constraints? Review done, plan fixed,
then show hand and let the agent drive you to the destination.

Not into the names? Rename them. They are defaults. The important part is the
generated workflow: project principles live inside the skills the agent invokes
while working on development goals.

In Codex, the same workflow can also be packaged as a plugin for one-step
installation.

## Try It

Install the Forma CLI first:

```bash
pipx install git+https://github.com/BeforeWave/forma.git
```

Using Codex as the example, generate and install the default Plan-First plugin:

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma install --target codex --scope project /tmp/forma-codex-plugin
```

After installation, start with the planning skill:

> Use `forma-plan` to plan this issue first.

That gives you the default harness. Codex should not jump from goal to patch. It
should clarify the goal, gather evidence, lock the execution contract, then
execute tasks with proof.

## Reviewable Output

For each development goal, the runtime harness should leave reviewable output:

- `plans/issue-<id>/plan.md`: the clarified goal, scope, approach, validation,
  strategy, and output and proof boundary.
- `plans/issue-<id>/tasks.md`: ordered accepted tasks with delivery targets,
  proof obligations, dependencies, and constraints.
- `plans/issue-<id>/runs/`: execution proof recorded as tasks complete.

Actual Forma plans are in [`plans/`](./plans/).

That is the difference between "the agent followed instructions" and a workflow
reviewers can inspect: what was clarified, what was locked, what ran, and what
proof exists.

## Shape The Harness

The default harness is only the baseline. The point of Forma is to shape it with
the engineering principles this project cares about.

Project principles can cover different kinds of concerns:

- evidence sources the agent should prefer before planning;
- mutation boundaries such as generated outputs, public APIs, or data paths;
- risk checkpoints for permission, billing, deletion, migration, or compatibility work;
- validation expectations for different kinds of tasks;
- review and stop conditions when the plan drifts or evidence is thin.

For a quick project-specific harness, install the creator skill:

```bash
forma build-creator --target codex --output /tmp/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

Then talk to Codex like you would to a collaborator:

> Use `forma-creator` to customize a workflow for this repo. First look at the
> repository structure and common validation paths. I care about generated
> outputs coming from source, lightweight checks for docs-only changes, nearby
> tests before code changes, and surfacing uncertain calls for me to decide.

For durable rules, write a profile and generate the workflow from source. For
Claude Code, verification, install locations, profile authoring, and full
command details, see [Usage](./docs/usage.md).

## When To Use It

Use Forma when a project's standing principles should shape how agents handle
development goals at runtime. Good fits include projects where planning,
evidence, task boundaries, validation, review proof, or stop conditions should
be more than background instructions.

Forma is usually too much for typo fixes, short summaries, or a few simple repo
reminders. For those, a direct prompt, a single custom skill, or local project
instructions may be enough.

## Forma On Forma

Forma uses Forma-managed Plan-First skills for its own development. The source
profile for this repository lives in [`profiles/forma-self/`](./profiles/forma-self/).
It defines how this repo's agents handle docs, governance, generated baselines,
profile work, validation, and proof. Forma self-iterations use the same
`plans/issue-<id>/` plan, task, and proof trail described above.

## Documentation

- [Usage](./docs/usage.md): commands, install locations, verification, targets, and custom generation.
- [Quick Start](./docs/quick-start.md): a longer first-run walkthrough.
- [Concepts](./docs/concepts.md): mental model and fit.
- [Forma Creator](./docs/forma-creator.md): custom project-specific skill generation.
- [Profile Schema](./docs/profile-schema.md): durable profile source format.
- [Targets](./docs/targets.md): Codex and Claude Code behavior.
- [STRUCTURE.md](./STRUCTURE.md): source tree and ownership boundaries.

## License

Apache-2.0 - see [LICENSE](./LICENSE).
