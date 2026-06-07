# Examples

Chinese version: [examples.zh-CN.md](./examples.zh-CN.md)

This page shows what a Forma runtime harness should make visible during an
end-to-end development goal.

The walkthrough is illustrative. It is not a transcript of a live agent run.
Use [Quick Start](./quick-start.md) to generate and run the real sample bundle.

## Real Sample Source

Start from the committed backend sample profile:

```text
examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml
```

It emits committed generated baselines for both supported targets:

```text
examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
```

## Generate The Bundle

```bash
forma create-bundle \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

Install the generated stage skills into the matching target location. See
[Targets](./targets.md).

## Example Request

```text
Update the issue-tracked backend behavior described by issue 123.
```

A Forma-generated workflow should move the request through the runtime harness
instead of jumping straight to implementation.

## Skill Walkthrough

| Skill | Expected movement |
|---|---|
| `forma-plan` | Clarify goal, scope, approach, validation, plan strategy, and whether the issue source adapter should be used. |
| `forma-ground` | Inspect only the repository and source material needed for the accepted scope. Separate facts, risks, unknowns, and recommendations. |
| `forma-lock` | Write `plans/issue-<id>/plan.md` and `tasks.md` with accepted tasks, validation, and continuation boundaries. |
| `forma-execute` | Execute one accepted task, run its validation, and record proof for review. |
| `forma-showhand` | After review is done and the plan is fixed, continue accepted tasks with continuous `forma-execute`. |

## What To Inspect

After a real run, inspect:

- the generated skill bundle and `.forma-manifest.json`;
- the plan under `plans/issue-<id>/plan.md`;
- executable tasks under `plans/issue-<id>/tasks.md`;
- run evidence under `plans/issue-<id>/runs/` when the workflow records it;
- validation commands and results;
- any blocker if `forma-showhand` could not continue.

## What Good Looks Like

A good run should make these things visible:

- which demand source was treated as authoritative;
- what evidence the agent read before planning;
- what scope was accepted;
- which task was executed;
- what validation proved the result;
- why continuous execution was allowed or blocked.

## Common Bad Patterns

- `forma-execute` starts implementation before `forma-lock` writes accepted tasks.
- `forma-ground` writes files or makes final task decisions.
- Every skill repeats every rule instead of using stage constraints and
  references.
- `forma-showhand` continues when validation failed, proof is missing, or the
  next accepted task cannot be executed under the current plan.
- The generated bundle verifies structurally, but the profile was never
  reviewed by the owning project.

## Related Docs

- [Workflow Contract](./workflow-contract.md): stage gates and proof.
- [Skill Bundle](./skill-bundle.md): generated output layout.
- [Profile Schema](./profile-schema.md): source format for the sample profile.
- [Verifier](./verifier.md): verification boundary.
