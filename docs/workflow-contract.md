# Workflow Contract

Chinese version: [workflow-contract.zh-CN.md](./workflow-contract.zh-CN.md)

A workflow contract defines how an agent is allowed to move from demand to
evidence, from evidence to plan, from plan to execution, and from execution to
continuation.

Forma compiles that contract into target-specific skills. The output is not a
better prompt. It is a staged work loop with gates, boundaries, and proof
requirements.

## Practical Effect

Forma does not guarantee perfect agent behavior. It gives the workflow a better
control surface.

| Prompt-only workflow | Forma workflow surface |
|---|---|
| Rules are re-explained in each conversation. | Durable rules live in profiles. |
| Planning, grounding, and execution can blur together. | Stages separate clarification, grounding, sealing, execution, and continuation. |
| Validation can be remembered late. | Proof expectations are written into task contracts. |
| Continuation depends on the agent's judgment in the moment. | `flow` has explicit stop conditions. |

## Contract Flow

The default Forma methodology uses five stages:

```text
demand -> proposal -> evidence -> plan -> task -> proof -> continuation
          shape       gauge      seal    pour    pour     flow
```

Each stage has one job:

| Stage | Job | Handoff |
|---|---|---|
| `shape` | Clarify the demand and bound the proposal. | A settled decision gate or explicit blocked/clarifying state. |
| `gauge` | Gather repository, spec, document, and history evidence read-only. | A grounding handoff with facts, risks, and unknowns. |
| `seal` | Turn the settled proposal and evidence into an execution contract. | `plans/issue-<id>/plan.md` and `tasks.md`. |
| `pour` | Execute one accepted task and record proof. | Review-ready task result with validation evidence. |
| `flow` | Continue through accepted tasks only while the sealed plan allows it. | Completed tasks or a stop condition. |

The stage names are defaults. Profiles can rename generated skills, but the
contract stages remain the same.

## Stage Permissions

The contract matters because each stage has different permissions.

| Stage | Allowed | Not allowed |
|---|---|---|
| `shape` | Clarify goal, scope, approach, validation, plan strategy, and boundaries. | Inspect the repository, write plan files, or implement. |
| `gauge` | Read files, inspect repository state, and produce grounding. | Write files, run mutating commands, or decide final execution tasks. |
| `seal` | Write the accepted plan and task contract after required decisions are settled. | Invent missing scope, skip grounding, or broaden acceptance criteria. |
| `pour` | Implement the current accepted task and run its validation. | Execute unaccepted tasks, rewrite the plan, or continue without review gates. |
| `flow` | Resume the sealed task list when continuation is allowed. | Bypass missing plans, missing proof, unclear permissions, or blocked routes. |

## Small Example

Request:

```text
Update the billing API behavior.
```

A Forma workflow should make that request move through the contract:

| Stage | What happens |
|---|---|
| `shape` | Decide whether this changes public API behavior, persistence, or compatibility expectations. |
| `gauge` | Read the current routes, API docs, tests, and relevant prior plan or issue evidence. |
| `seal` | Write accepted tasks with validation, such as API tests, compatibility checks, or contract review. |
| `pour` | Implement one accepted task and run the proof required by that task. |
| `flow` | Continue only if the sealed plan allows it; stop if a new API contract decision appears. |

## Evidence Policy

A workflow contract should say what evidence the agent must use before it acts.

Common evidence rules include:

- authoritative demand sources, such as PRDs, issues, specs, or briefs;
- repository files and current implementation facts;
- history, run evidence, or previous plans when relevant;
- validation commands and proof requirements;
- explicit unknowns when required evidence is missing.

Evidence rules belong in the stage that needs them. For example, source reading
usually belongs in `gauge`; final task validation belongs in `seal` and `pour`.

## Execution Boundaries

Execution boundaries prevent convenient scope drift.

A useful contract names:

- which task is accepted;
- which files or subsystems are in scope;
- which work routes require extra approval;
- which commands prove the result;
- what must stop automatic continuation.

Broad rules should not be copied into every skill. Put stable defaults in the
profile, stage-specific rules in stage constraints, and route-specific rules in
conditional overlays.

## Validation And Proof

Validation is not only a command list. It is the proof path for the task.

`seal` should turn validation expectations into the task contract. `pour` should
run the narrowest relevant checks first, then any shared gate required by the
plan. `flow` should continue only while accepted tasks and proof requirements
are still clear.

If proof is missing, stale, or outside the accepted task, the contract should
make the agent stop or ask for correction.

## Continuation Rules

`flow` is not "keep going no matter what." It is controlled continuation.

Continuation should stop when:

- `plan.md` or `tasks.md` is missing, incomplete, or stale;
- the next task is not accepted;
- the current change needs a new decision boundary;
- validation fails or cannot run;
- the plan did not allow automatic continuation for this route;
- the user interrupts or asks to review.

## How Profiles Shape The Contract

Profiles do not replace the contract. They specialize it.

Use profiles to add:

- durable source-of-truth rules;
- target skill names and display labels;
- stage-specific constraints;
- validation commands;
- references and scripts selected by stage;
- conditional overlays for routes such as docs-only, migration, generated-baseline, governance, backend, or cross-layer work.

Use temporary injection for one-off constraints that should affect only the
current generated bundle.

## Related Docs

- [Concepts](./concepts.md): compiler model and core terminology.
- [Profile Schema](./profile-schema.md): durable workflow source format.
- [Skill Bundle](./skill-bundle.md): generated artifact layout.
- [Examples](./examples.md): illustrative end-to-end walkthrough.
- [Usage](./usage.md): command reference.
