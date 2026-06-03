# AGENTS

Forma is in bootstrap. The source tree is intentionally empty at this stage; there is no implementation code to navigate yet.

## Read first

- `README.md` — three-layer architecture and positioning
- `STRUCTURE.md` — the planned source tree
- `plans/issue-<id>/plan.md` — current issue goal, scope, approach, validation
- `plans/issue-<id>/tasks.md` — current issue task checklist

## Working rules

- Keep changes scoped to the current issue's plan and tasks.
- Do not pre-lock Layer 2 or Layer 3 implementation decisions outside the current planned scope.
- Treat `plan.md` as the source of truth for what is and is not in scope for the current issue.
- Record meaningful execution decisions in `plans/issue-<id>/implement_notes.md` when they would help a later task or reviewer understand the work.

## Workflow state

Each issue's plan, tasks, and execution evidence live under `plans/issue-<id>/`. There is no `source/` tree to navigate yet; subsequent issues will introduce it.
