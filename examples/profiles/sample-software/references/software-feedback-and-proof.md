# Feedback And Proof Model

Plan-first work is not "write code"; it is "prove the target behavior with appropriate evidence."

## Feedback Loop First

Before implementation, identify the fastest trustworthy pass/fail signal:

- bug/regression: establish a reproducible signal and root-cause sentence before patching.
- UI/visual: lock the real rendered surface, viewport/state, and defect before editing.
- backend contract: lock the source of truth and system-visible semantics before implementation.
- fullstack: lock frontend/backend contract mapping and integration validation before changing both sides.
- tooling/config: lock affected commands and repeatable execution paths before editing.

## Evidence Types

- behavior proof: user- or system-visible behavior is proven by tests, manual validation, or screenshots.
- contract proof: API/RPC/event/schema/request/response/error/auth semantics match source of truth.
- data/state proof: data writes, migrations, state transitions, cache behavior, idempotency, and rollback are verified.
- runtime proof: browser, device, SSR/hydration, process, deployment, task, performance, and observability impact are verified.
- visual proof: screenshot, visual diff, story, design comparison, viewport, or state evidence.
- manual/review-only proof: when programmatic validation is unavailable, state why and name the review target and evidence path.

## Test Public Behavior

Prefer public interface or public behavior:

- frontend: visible UI, component contracts, route behavior, form interaction, state transition, and service/client boundaries.
- backend: API/service contracts, data state, permissions, errors, integration paths, and background job visible results.
- tooling: command input/output, generated artifacts, failure modes, and CI/local consistency.

Do not add tests only to preserve private implementation shape.

## Vertical Slices

Move by one behavior slice plus one proof signal. Avoid splitting implementation and validation into separate tasks that do not close a feedback loop.

## Prototype Boundary

A prototype answers one explicit question. It is not a shortcut into production implementation.

Plans must state:

- the one question the prototype answers.
- prototype location, run entrypoint, or viewing method.
- visible states, variants, or inputs.
- deletion, absorption, or promotion rules.

## Bug/Regression Root-Cause Gate

Debugging tasks should write a root-cause sentence before patching:

```text
Root cause: <file/function/condition/path> under <specific input or state> causes <observed symptom>.
```

If the root cause cannot be established, keep the task blocked or convert it into an exploration/diagnosis gate instead of guessing a patch.
