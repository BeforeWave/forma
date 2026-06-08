<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

Team engineering practice should not stop at documentation.
**Forma generates a project-specific agent harness, so the agent declares how it will follow team rules before execution, then delivers against the task contract.**

This task contract is not a vague "I'll follow the rules", and it is not a generic execution plan. It is the team's engineering principles applied to the current task: which evidence grounds the work, which boundaries may be touched, which files must not change, which validations must run, where proof is recorded, and when the agent must stop.

In other words, Forma makes team principles more than something the agent has read. Before each execution, they become concrete obligations that can be reviewed, constrained, and traced.

---

## What Forma Produces

Forma's long-term input is a `profile`, the artifact handed to the agent is a harness, and each task starts with a task contract.

- `profile`: the source for team engineering principles, kept in version control.
- `skill bundle`: a skill directory installed into Codex or Claude Code.
- `Codex plugin`: the same harness packaged as a Codex plugin.
- `task contract`: the agent's commitment for one task, recorded under `plans/issue-<id>/`.

The default harness contains five skills:

| Skill | Purpose |
|---|---|
| `forma-plan` | Clarify goal, scope, constraints, and acceptance criteria in chat only; do not write plan files or execute work. |
| `forma-ground` | Read-only evidence collection from code, docs, issues, tests, and related sources; do not write files or decide tasks. |
| `forma-lock` | Materialize the settled approach into `plan.md` and `tasks.md`, locking the task contract. |
| `forma-execute` | Execute one accepted task, run validation, record proof, and stop when review is needed. |
| `forma-showhand` | Continue remaining tasks inside a locked plan until blocked, validation fails, or human input is needed. |

Profiles can rename skills, add constraints, add references, and define validation requirements. The generated bundle or plugin exposes the resulting skills.

---

## How To Use

Generate a Codex skill bundle from a tracked profile and verify it before installation:

```bash
forma create-bundle \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

After installing the verified bundle, start planning in an agent thread:

```text
Use forma-plan to plan this issue first.

Issue:
<your task or issue>
```

Continue through the task contract: use `forma-ground` when repository evidence is needed, `forma-lock` after the approach is accepted, `forma-execute` to run one task, and `forma-showhand` to continue through a stable plan.

If you do not have a profile yet, use `forma-creator` to draft one. If you need a Codex plugin, use `forma create-plugin`. Full installation and target details are in [Quick Start](./docs/quick-start.md) and [Usage](./docs/usage.md).

---

## Status

Forma is still early.

Forma gives agents a better control surface, not a behavioral guarantee. Whether an agent actually follows generated skills still depends on the model and host environment. Putting workflow into files, stages, and proof requirements is more reliable than relying on chat memory alone, but it is not magic.

Current focus:

- Make Plan-First agent workflows easier to install.
- Make project-specific workflow profiles easier to author.
- Improve generated bundle verification.
- Add examples that show real planning, execution, validation, and proof.

Committed generated examples are mainly drift baselines, not proof of runtime agent behavior.

Forma also uses its own Plan-First workflow for development; this repository's source profile lives in [`profiles/forma-self/`](./profiles/forma-self/).

---

## Documentation

- [Quick Start](./docs/quick-start.md)
- [Concepts](./docs/concepts.md)
- [Workflow Contract](./docs/workflow-contract.md)
- [Profile Schema](./docs/profile-schema.md)
- [Targets](./docs/targets.md)
- [Usage](./docs/usage.md)

Apache-2.0 - see [LICENSE](./LICENSE)
