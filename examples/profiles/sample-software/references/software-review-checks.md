# Software Review Checks

Select checks according to the Impact Profile; do not mechanically apply every item.

## General

- Goal, Scope, Approach, and the current task are still aligned.
- The implementation only touched the surface allowed by the current task.
- Existing user worktree changes were preserved.
- Project rules and source-of-truth documents were followed.
- Validation results or review-only rationale are clear.
- Scope, contracts, designs, and data were not silently expanded or invented.

## Frontend

- The target rendered surface is correct.
- Relevant UI states and interactions are covered.
- API, data, mock, and fixture boundaries are clear.
- Accessibility, focus, keyboard, semantics, responsive behavior, browser behavior, and hydration impact are validated when relevant.
- Visual, copy, and design inputs come from project sources or user confirmation.
- Evidence proves the user-visible behavior when that proof is required.

## Backend

- Contract, permissions, validation, errors, idempotency, and side effects are clear.
- Data state, migrations, transactions, cache, background jobs, and external integrations are validated when relevant.
- Compatibility, rollback, deployment, observability, and operational impact are included in the plan.
- Tests cover system-visible semantics, not only internal implementation shape.

## Fullstack

- Frontend and backend contract sources of truth agree.
- Request, response, error, auth, and permission mappings are explicit.
- Mock or fixture behavior matches the real backend or has a clear lifecycle.
- Cross-layer integration validation is sufficient.
- Rollout, compatibility, and rollback order are clear.

## Generic

- Tooling, configuration, scripts, documentation, and CI/local commands agree.
- Generated artifacts are separated from source of truth.
- Lockfile, cache, build output, and release impact are validated when relevant.
