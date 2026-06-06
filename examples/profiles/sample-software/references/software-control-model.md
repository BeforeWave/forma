# Software Plan-First Control Model

This workflow is a controller for software engineering work, not a technology-stack knowledge base. It prevents agents from implementing before boundaries, evidence, and source-of-truth decisions are complete.

## Core Invariants

1. Converge before implementation: do not implement while Goal, Scope, Approach, Validation, Impact Profile, or Impact Boundary is incomplete.
2. Ground before writing a plan: when repository facts are needed, confirm project rules, paths, commands, contracts, and validation methods through read-only grounding.
3. Treat the plan files as the execution contract: once `plan.md` and `tasks.md` are sealed, implementation must not silently rewrite them. Stop and re-plan when assumptions fail.
4. Execute tasks sequentially through review gates: each run handles only the first incomplete task, produces review-ready evidence, and completes only the reviewed task.
5. Bind completion claims to evidence: record validation commands, review-only rationale, changed files, and evidence paths.
6. Keep workflow state inside the generated plan-first workflow: use the bundled `scripts/forma-workflow.sh` and `plans/issue-<id>/` artifacts instead of inventing alternate state directories.

## Failure Modes

- Starting implementation before the requirement is converged.
- Treating a path, framework, command, contract, design, or validation method as fact without source evidence.
- Inventing API fields, error semantics, UI states, data migrations, or deployment assumptions to make implementation easier.
- Validating only the happy path while missing failure, boundary, permission, asynchronous, regression, or system-visible behavior.
- Mixing unrelated user work, generated artifacts, or temporary prototypes into the task outcome.
- Letting automatic execution continue when source of truth, validation, safety, or review boundaries are incomplete.

## Control Surfaces

- Activation Control: trigger only for software work that needs plan-first control.
- State Control: use `plan.md`, `tasks.md`, run evidence, review snapshots, and validation logs.
- Trajectory Control: enforce plan convergence, grounding, finalization, implementation, review, and completion.
- Execution Control: execute tasks in order; do not skip tasks or silently change the plan.
- Completion Control: require evidence-backed completion summaries.
- Evolution Control: keep reusable workflow rules in profiles and project-specific rules in the target repository.
