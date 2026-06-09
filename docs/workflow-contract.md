# Workflow Contract

Chinese version: [workflow-contract.zh-CN.md](./workflow-contract.zh-CN.md)

A workflow contract is the plan contract produced when project rules are applied
to the current task. It answers: which facts this task relies on, what may
change, what must not change, how validation proves the result, where proof is
recorded, and when the agent must stop for review.

After a generated workflow is installed, it moves the agent from goal to
proposal, evidence, task contract, execution, and proof. The point is not only
"write a plan first"; the plan must expand according to the project's most
important rules.

## Practical Effect

Many generic workflows ask an agent to explain what it is about to do. A Forma
contract goes further: the plan becomes a task contract reviewers can inspect
against project rules.

| Generic planning flow | Forma workflow contract |
|---|---|
| The plan describes rough steps. | The contract states which project rules apply to this task. |
| Evidence gathering depends on the agent remembering. | The contract names authoritative sources and facts that must be confirmed. |
| Boundaries often stay vague. | The contract states what may be touched and what must stop. |
| Validation may be only a command list. | The contract explains why validation proves the current task. |
| Continuation depends on momentary judgment. | `forma-showhand` continues only when locked tasks and stop conditions allow it. |

Forma does not guarantee perfect agent behavior. It gives a clearer control
surface: contract, validation, and proof stay inspectable.

## Contract Flow

The default workflow uses four core skills to manage the contract lifecycle and
one continuous execution entrypoint:

```text
goal -> proposal -> evidence -> task contract -> accepted task -> proof
        plan        ground     lock             execute
```

| Public skill | Job | Handoff |
|---|---|---|
| `forma-plan` | Align the goal with project rules and produce a proposal. | A settled direction, or explicit blocked/clarifying state. |
| `forma-ground` | Gather evidence read-only according to the rules. | A grounding handoff with facts, risks, and unknowns. |
| `forma-lock` | Write the accepted approach as a task contract. | `plans/issue-<id>/plan.md` and `tasks.md`. |
| `forma-execute` | Execute one accepted task, run validation, and record proof. | Review-ready task result with validation evidence. |

`forma-showhand` is the autopilot entrypoint for `forma-execute`. After the
plan is locked, it continues remaining accepted tasks until blocked, validation
does not pass, or human input is needed.

These public skill names are defaults. Profiles or creator output can rename
them, but the stage semantics should stay the same.

## Skill Boundaries

The contract matters because each stage has different permissions.

| Public skill | Allowed | Not allowed |
|---|---|---|
| `forma-plan` | Clarify goal, scope, approach, validation, plan strategy, and boundaries. | Inspect the repository, write plan files, or implement. |
| `forma-ground` | Read files, inspect repository state, and produce grounding. | Write files, run mutating commands, or decide final execution tasks. |
| `forma-lock` | Write the accepted plan and task contract after decisions are settled. | Invent missing scope, skip grounding, or broaden acceptance criteria. |
| `forma-execute` | Implement the current accepted task and run its validation. | Execute unaccepted tasks, rewrite the plan, or continue past review gates. |
| `forma-showhand` | Resume the locked task list and apply `forma-execute` task by task. | Bypass missing plans, missing proof, unclear permissions, or blocked routes. |

## Reading A Task Contract

Request:

```text
Update the settings schema source and refresh the generated API docs.
```

If the project cares most about generated-file traceability and API contract
review, the task contract should apply those rules to the current task:

```text
Focus: confirm schema source and API contract impact before refreshing generated docs.
Evidence: settings schema source; generator entrypoint; API contract policy; nearby schema tests.
Tasks:
  1. impact-check: classify the contract change as none / additive / breaking.
  2. source-change: edit only schema source and required tests.
  3. generated-proof: run the generator and record the generated diff source.
Boundary: do not hand-edit generated docs; do not implement before breaking impact is reviewed.
Validate: schema test; generator command; generated diff check.
Proof: write command output and generated diff summary under `plans/issue-<id>/runs/`.
Stop if: contract impact requires API review;
         generated docs cannot be reproduced by the generator;
         shared schema infrastructure outside the task must change.
```

The commands, task order, and stop conditions here are current task contract
output. The profile or creator rules provide the review standard: evidence
source, generated-output traceability, API review, and proof requirements.

## Evidence Policy

A workflow contract should say what evidence the agent must use before acting.

Common evidence rules include:

- authoritative demand sources, such as PRDs, issues, specs, or briefs;
- repository files and current implementation facts;
- history, run evidence, or previous plans when relevant;
- validation commands and proof requirements;
- explicit unknowns when required evidence is missing.

Evidence rules belong in the stage that needs them. For example, source reading
usually belongs in `forma-ground`; final task validation belongs in
`forma-lock` and `forma-execute`.

## Execution Boundaries

Execution boundaries prevent convenient scope drift.

A useful contract names:

- which task is accepted;
- which files or subsystems are in scope;
- which work routes require extra approval;
- which exact commands or shared checks prove the result;
- where generated outputs, logs, or run evidence belong;
- what must stop automatic continuation.

Broad rules should not be copied into every skill. Put stable defaults in the
profile, stage-specific rules in stage constraints, and route-specific rules in
conditional overlays.

## Validation And Proof

Validation is not only a command list. It is the proof path for the task.

`forma-lock` should write validation expectations into the task contract.
`forma-execute` should run the narrowest relevant checks first, then any shared
gate required by the plan. `forma-showhand` repeats that accepted-task execution
loop.

If proof is missing, stale, or outside the accepted task, the contract should
make the agent stop or ask for correction.

## Showhand

`forma-showhand` is the continuous execution entrypoint for `forma-execute`.
After review is done and the approach is fixed, use it to let the agent continue
through the accepted task list.

It continues only when the existing contract covers the next step. It should
stop when:

- `plan.md` or `tasks.md` is missing, incomplete, or stale;
- the next task is not accepted;
- the current change needs a new decision boundary;
- validation does not pass or cannot run;
- required prerequisites or permissions are unavailable;
- the user interrupts or asks for review.

## How Profiles Shape The Contract

Profiles do not replace the contract. Profiles maintain durable rules; the
contract applies those rules to the current task.

Use profiles to add:

- durable source-of-truth rules;
- target skill names and display labels;
- stage-specific constraints;
- validation commands;
- references and scripts selected by stage;
- conditional overlays for routes such as docs-only, migration, generated-baseline, governance, backend, or cross-layer work.

Temporary injection is for on-the-spot rules that should affect only the current
generated output.

## Related Docs

- [Concepts](./concepts.md): compiler model and core terminology.
- [Profile Schema](./profile-schema.md): durable workflow source format.
- [Skill Bundle](./skill-bundle.md): generated output layout.
- [Examples](./examples.md): sample profiles, generated baselines, and real runs.
- [Usage](./usage.md): command reference.
