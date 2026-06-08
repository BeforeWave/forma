# Workflow Contract

Chinese version: [workflow-contract.zh-CN.md](./workflow-contract.zh-CN.md)

A workflow contract is the task-execution shape of a generated Forma workflow.
It defines how an agent moves from a concrete development goal to evidence,
plan, ordered tasks, validation gates, proof, and review.

Forma compiles static project rules into target-specific skills. When those
skills run, the contract becomes the harness around the agent's work.

## Practical Effect

Forma does not guarantee perfect agent behavior. It gives the workflow a better
control surface.

| Prompt-only workflow | Forma workflow harness |
|---|---|
| Rules are re-explained in each conversation. | Durable rules live in profiles. |
| Planning, grounding, and execution can blur together. | Stages separate clarification, grounding, sealing, execution, and continuation. |
| Validation can be remembered late. | Exact commands, shared checks, and proof expectations are written into task contracts. |
| Continuation depends on the agent's judgment in the moment. | `forma-showhand` automates accepted tasks under the locked plan. |

## Contract Flow

The default Forma methodology uses four core public workflow skills, plus
`forma-showhand` for continuous execution:

```text
goal -> proposal -> evidence -> execution contract -> ordered task -> proof
        plan        ground     lock                 execute
```

Each core stage has one job:

| Public skill | Job | Handoff |
|---|---|---|
| `forma-plan` | Clarify the demand and bound the proposal. | A settled decision gate or explicit blocked/clarifying state. |
| `forma-ground` | Gather repository, spec, document, and history evidence read-only. | A grounding handoff with facts, risks, and unknowns. |
| `forma-lock` | Turn the settled proposal and evidence into an execution contract. | `plans/issue-<id>/plan.md` and `tasks.md`. |
| `forma-execute` | Execute one accepted task and record proof. | Review-ready task result with validation evidence. |

`forma-showhand` is the continuous `forma-execute` candy skill, not a separate
stage. After review is done and the plan is fixed, it resumes the locked task
list until proof, validation, permission, or prerequisite state blocks safe
continuation.

The public skill names are defaults. Profiles can rename generated skills while
keeping the workflow semantics intact.

## Skill Permissions

The contract matters because each public skill has different permissions.

| Public skill | Allowed | Not allowed |
|---|---|---|
| `forma-plan` | Clarify goal, scope, approach, validation, plan strategy, and boundaries. | Inspect the repository, write plan files, or implement. |
| `forma-ground` | Read files, inspect repository state, and produce grounding. | Write files, run mutating commands, or decide final execution tasks. |
| `forma-lock` | Write the accepted plan and task contract after required decisions are settled. | Invent missing scope, skip grounding, or broaden acceptance criteria. |
| `forma-execute` | Implement the current accepted task and run its validation. | Execute unaccepted tasks, rewrite the plan, or continue without review gates. |
| `forma-showhand` | Resume the locked task list and keep applying `forma-execute` task by task. | Bypass missing plans, missing proof, unclear permissions, or blocked routes. |

## Small Example

Request:

```text
Update the source for a generated schema.
```

A Forma workflow should make that request move through the contract:

| Public skill | What happens |
|---|---|
| `forma-plan` | Decide whether the task may edit source only, whether generated files are out of bounds, and what proof must exist. |
| `forma-ground` | Read the source schema, generator entrypoint, nearby tests, and any existing generated output policy. |
| `forma-lock` | Write accepted tasks with exact boundaries and commands such as `make generate-schema` plus the schema validation gate. |
| `forma-execute` | Edit only the accepted source/test files, run the task's validation, and record generated diff plus command output as proof. |

After review is done and the plan is fixed, `forma-showhand` can continue the
accepted task list until proof, validation, permission, or prerequisite state
blocks progress.

## Evidence Policy

A workflow contract should say what evidence the agent must use before it acts.

Common evidence rules include:

- authoritative demand sources, such as PRDs, issues, specs, or briefs;
- repository files and current implementation facts;
- history, run evidence, or previous plans when relevant;
- validation commands and proof requirements;
- explicit unknowns when required evidence is missing.

Evidence rules belong in the skill that needs them. For example, source reading
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

`forma-lock` should turn validation expectations into the task contract.
`forma-execute` should run the narrowest relevant checks first, then any shared
gate required by the plan. `forma-showhand` repeats that accepted-task execution
loop without asking for review after every task.

If proof is missing, stale, or outside the accepted task, the contract should
make the agent stop or ask for correction.

## Showhand

`forma-showhand` is the candy skill for continuous `forma-execute`. Use it when
the plan has been reviewed, the approach is fixed, and you want the agent to
keep driving through the accepted task list.

It still stops when the next step cannot be executed under the existing harness:

- `plan.md` or `tasks.md` is missing, incomplete, or stale;
- the next task is not accepted;
- the current change needs a new decision boundary;
- validation fails or cannot run;
- required prerequisites or permissions are unavailable;
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
- [Skill Bundle](./skill-bundle.md): generated output layout.
- [Examples](./examples.md): illustrative end-to-end walkthrough.
- [Usage](./usage.md): command reference.
