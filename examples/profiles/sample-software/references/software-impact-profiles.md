# Software Impact Profiles

Use `Impact Profile` to name the main surface of the task, and `Impact Boundary` to state the limits the implementation must respect.

## Impact Profile

`Primary` must choose one:

- `frontend`: changes user-visible UI, interaction, client state, visual presentation, content, or browser runtime behavior.
- `backend`: changes server behavior, API/RPC/event contracts, data, permissions, validation, storage, background jobs, or operational behavior.
- `fullstack`: changes frontend surface and backend/system contract in the same work item, or needs integration validation across those surfaces.
- `generic`: changes tooling, scripts, documentation, configuration, build/test infrastructure, or internal library behavior that is not clearly frontend or backend.

Use `Secondary` only when it materially changes execution boundaries.

## General Impact Boundary

Plan entries should cover relevant boundaries. Irrelevant boundaries may say "not applicable"; relevant unknowns must not be omitted.

- Target surfaces: app, site, package, service, module, route, page, component, API, job, script, or artifact.
- User/system-visible behavior: behavior that users or other systems can observe.
- Contract/data/state boundary: API, schema, data, state, permissions, error semantics, cache, mock, or fixture source of truth.
- Composition/ownership boundary: module, layer, component, service, shared abstraction, ownership, and reuse boundaries.
- Runtime/operational boundary: browser, device, SSR/hydration, process, deployment, migration, rollback, environment, performance, and observability impact.
- Content/design boundary: copy, visual design, design system, brand, content, localization, screenshot, or specification source.
- Feedback/evidence boundary: fastest trustworthy feedback loop, validation command, test layer, manual review, screenshot, trace, log, or report.
- Artifact/evidence boundary: whether plans, task records, evidence, generated artifacts, prototypes, import/export files, or batch results are committed, local, gitignored, or transient.

## Frontend Risks

- Editing the wrong rendered surface.
- Missing loading, empty, error, disabled, permission, retry, focus, navigation, validation, async, optimistic, or cache states.
- Inventing API fields, error codes, permissions, business rules, or data truth in the UI layer.
- Letting mocks, demos, or fixtures become production facts.
- Breaking shared components, routes, state, styles, design systems, or accessibility.
- Claiming user-visible behavior is correct without rendered, browser, story, screenshot, or manual evidence when that evidence is needed.

## Backend Risks

- Silently changing API/RPC/stream/event contracts.
- Writing incorrect data, migrating schema incorrectly, or changing state machines.
- Ignoring permissions, validation, error semantics, idempotency, concurrency, retries, or side effects.
- Missing background job, queue, cache, transaction, external integration, deployment, or rollback risk.
- Replacing necessary contract, integration, or regression proof with a unit happy path.

## Fullstack Risks

- UI assumes an API field or error semantic the backend does not provide.
- Frontend mocks or fixtures drift from real API timing, errors, permissions, or caching.
- Backend compatibility strategy and frontend rollout order conflict.
- Cross-layer integration lacks reproducible validation.

Fullstack plans must name the contract source of truth, change order, request/response/error/auth/permission mapping, mock lifecycle, integration validation, compatibility, deployment, and rollback boundaries.

## Generic Risks

- Scripts or configuration change CI, local development, release, or cache behavior.
- Documentation and actual commands drift.
- Toolchain upgrades change lockfiles, build outputs, or lint/test results.
- Generated artifacts are confused with source of truth.
- New abstractions lack real use sites or maintenance boundaries.

Generic plans must state affected commands, artifacts, compatibility, rollback path, and validation signal.
