<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**Customize a project workflow in one sentence, so agents plan, validate, and
deliver by your team's rules.**

Coding agents usually get into trouble in real projects not because they cannot
write code, but because they start implementation before the team's delivery
rules have been applied to the task.

Many teams already have agent-facing docs and generic "plan first, then
execute" workflows. Those can make an agent read rules and write a staged plan,
but fixed stages are not the same thing as team standards. The plan can still
miss task-level constraints the team can rely on and verify.

Forma closes that gap. You can tell the agent:

```text
Use Forma to customize a workflow for this project. Read the docs and code,
extract the engineering rules, and generate a workflow I can try.
```

Forma helps the team clarify the practices that matter most, then generates a
workflow that guards them. The workflow holds the agent to those rules across
planning, validation, proof, and stop conditions.

---

## How Forma Works

Forma has the agent derive rules from project facts: authoritative sources,
change boundaries, required tools, validation depth, proof, and stop conditions.

If you only want to try a workflow, those rules go into the generated output for
that run. If you want something maintained over time, they become a reviewable,
versioned `profile`.

Once installed, the workflow makes the agent produce a task contract and carry
those rules through evidence collection, implementation, validation, and proof.

---

## Same Goal, Different Acceptance Standards

For the same product goal, a generic workflow can send the agent through similar
stages: understand the goal, read evidence, write a plan, implement, validate.
Forma changes what makes that plan acceptable for the project.

Here is the same goal under different team rules. Before editing, the agent must
pin down different facts, boundaries, validation, and stop conditions.

```text
Product goal:
Ship rate limiting for the settings experience.
```

### API-contract-heavy Backend

The project cares most about API truth. Issue text alone is not enough; API
compatibility must be decided before implementation; generated output must trace
back to generator proof.

```text
Task contract excerpt:
  Focus: classify API impact before handler work.
  Evidence: GitHub issue comments / linked commits; contracts/api/v1/settings.yaml.
  Tasks:
    1. contract-impact: classify none / additive / breaking and decide whether to update the contract.
    2. implementation: add the limiter without changing the public response shape.
    3. generated-proof: if the contract changes, run the generator and record the generated diff source.
  Boundary: do not start handler changes until API impact is classified.
  Validate: contract compatibility check; generated output check; focused handler test.
  Stop if: issue comments conflict with the API contract;
           generated files changed without generator proof;
           compatibility needs API/product review.
```

### Runtime-behavior-heavy Backend

The project cares most about runtime control. The limiter must fit existing
configuration or rollout paths; local tests must cover the important behavior;
contract sync should not lead behavior stability.

```text
Task contract excerpt:
  Focus: place the limiter behind existing runtime controls before contract sync.
  Evidence: handler; service config; feature flags; recent settings commits.
  Tasks:
    1. route-selection: choose the existing config / rollout flag / limiter path.
    2. behavior-coverage: cover allowed, limited, disabled, and invalid-config cases.
    3. response-stability: keep the public response shape stable.
  Boundary: prefer existing runtime controls over new shared infrastructure.
  Validate: service behavior coverage; handler response coverage; config/schema check.
  Stop if: new shared infrastructure is required;
           local tests cannot cover the rollout path;
           the response shape must change.
```

Under API-contract rules, the task contract starts with API facts,
compatibility, and generated proof. Under runtime-behavior rules, it starts with
runtime control, behavior coverage, and response stability. If the plan misses
that entry point, implementation has not earned its start.

### Design-system-heavy Frontend

The project cares most about design-system semantics. The visible state must
come from existing component meaning; copy, state coverage, responsive behavior,
and accessibility must be provable.

```text
Task contract excerpt:
  Focus: map the rate-limit response to an existing design-system state.
  Evidence: source design context; API error metadata; design-system docs.
  Tasks:
    1. state-mapping: choose the existing component state, copy source, and retry affordance.
    2. ui-change: avoid new tokens, primitives, or visual patterns.
    3. proof: record mobile, desktop, and accessibility proof.
  Boundary: do not add tokens, primitives, or new visual patterns without review.
  Validate: component state coverage; browser flow coverage; accessibility check.
  Stop if: the design system has no matching state;
           the API lacks stable error or retry metadata;
           a new design-system variant is required.
```

### Ops-console-heavy Frontend

The project cares most about operator action. The signal must appear where an
operator can do something; table efficiency must not regress; telemetry, audit,
and runbook behavior must line up.

```text
Task contract excerpt:
  Focus: place the rate-limit signal where an operator can act.
  Evidence: support runbook; admin route; telemetry registry; table/filter behavior.
  Tasks:
    1. placement: choose row status / banner / audit log and bind the runbook action.
    2. admin-ui: preserve dense table layout, filters, and the existing operator flow.
    3. telemetry-proof: use a registered event and record audit trace plus state source.
  Boundary: preserve dense table layout, filters, and the existing operator flow.
  Validate: admin flow coverage; event registry check; table/filter regression coverage.
  Stop if: the runbook does not define the operator action;
           the telemetry event is not registered;
           the backend cannot distinguish rate limit from generic error.
```

Under design-system rules, the task contract starts with state semantics, copy
source, and experience proof. Under ops-console rules, it starts with operator
action, table efficiency, telemetry, and runbook alignment.

The same goal now produces different task contracts because the team rules
change what the agent must write down before editing.

---

## Outputs and Runtime Model

Forma puts team rules into three layers:

- `profile`: team-approved practices, kept in version control for review and maintenance.
- `workflow output`: the installed agent workflow, as a Codex / Claude Code skill bundle or a Codex plugin.
- `task contract`: the plan contract the agent creates for one task, recorded under `plans/issue-<id>/`.

The default workflow uses four core skills to manage the task contract:

| Skill | Purpose |
|---|---|
| `forma-plan` | Align the goal with project rules and produce a reviewable proposal; do not write files or execute work. |
| `forma-ground` | Collect the evidence required by the rules from code, docs, issues, tests, and related sources. |
| `forma-lock` | Write the accepted approach into `plan.md` and `tasks.md`, locking the task contract. |
| `forma-execute` | Execute one accepted task, run validation, record proof, and stop when review is needed. |

`forma-showhand` is the autopilot entrypoint for `forma-execute`: once a plan is
locked, it continues remaining tasks until blocked, validation does not pass, or
human input is needed.

When the team updates a profile, it updates which rules the workflow guards.
Regenerate the bundle or plugin, and the agent plans and executes against the
new constraints.

---

## Start Using Forma

The fastest path is to install `forma-creator` for the agent. Once it is
installed, say:

```text
Use forma-creator to customize a workflow for this project.
Read the docs and code, extract the engineering rules, show them to me first;
after I confirm, generate the workflow and install it from the hints.
```

This path is for on-the-spot customization. The creator extracts rules from the
project, waits for your confirmation, then generates and verifies a workflow you
can try. Rules that keep proving useful can later move into a tracked profile.

If you want a long-term profile from the start, you can say:

```text
Use Forma to extract engineering rules from this project's docs and code, and
draft a profile for me. After I approve the profile, create and install the
Codex workflow from it.
```

That path uses `forma explain profile --target codex` to load the authoring
standard. The agent drafts the profile first; after you approve it, the agent
generates, verifies, and installs the workflow from the hints.

After installation, start a new thread:

```text
Use forma-plan to plan this issue first.

Issue:
<your task or issue>
```

The first useful response should be a proposal, not a patch. If the agent edits
files immediately, the workflow was not loaded or was not triggered.

Codex skill bundle, Claude Code, and install-location details are in
[Quick Start](./docs/quick-start.md) and [Usage](./docs/usage.md).

---

## Status

Forma is still early.

Forma writes team rules into the workflow and task contract, but it does not make
the model perfectly obedient. Judge each run by the actual contract and proof
the agent leaves behind.

Current focus:

- Lower the cost of extracting project rules and generating profiles.
- Make workflow bundles and Codex plugins easier to install.
- Improve generated bundle verification.
- Add examples with real task contracts, execution, validation, and proof.

Committed generated examples are mainly drift checks. Runtime behavior should be
judged by the contract and proof left by the agent during a real run.

Forma also uses its own plan-first workflow for development; this repository's
source profile lives in [`profiles/forma-self/`](./profiles/forma-self/).

---

## Documentation

| | |
|---|---|
| [Quick Start](./docs/quick-start.md) | First run, creator path, and tracked-profile path. |
| [Concepts](./docs/concepts.md) | Layer model, compiler model, and stage boundaries. |
| [Workflow Contract](./docs/workflow-contract.md) | Stages, permissions, evidence, validation, and proof. |
| [Profile Schema](./docs/profile-schema.md) | YAML profile structure, constraints, resources, and overlays. |
| [Forma Creator](./docs/forma-creator.md) | Conversational workflow generation and temporary injection. |
| [Skill Bundle](./docs/skill-bundle.md) | Generated output layout. |
| [Verifier](./docs/verifier.md) | What verification checks and cannot prove. |
| [Targets](./docs/targets.md) | Codex and Claude Code target behavior. |
| [Examples](./docs/examples.md) | End-to-end workflow walkthrough. |
| [Usage](./docs/usage.md) | Command reference. |

Apache-2.0 - see [LICENSE](./LICENSE)
