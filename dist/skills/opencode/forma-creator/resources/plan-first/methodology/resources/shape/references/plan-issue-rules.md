# Dev Plan-Issue Rules

Use these rules only for `plan-issue`, the chat-only convergence step before `finalize-plan`.

- Resolve bundled `references/*` relative to the current triggered skill package. Never substitute a same-named resource from a sibling skill directory.
- Do not execute any bundled script from this skill. `forma-workflow.sh` is not part of plan-issue operation.
- Do not write `plan.md`, do not write `tasks.md`, do not initialize issue state, and do not start execution work.

## Mode And Boundary

- Use only in Plan mode. If the current agent is not in Plan mode, stop with `blocked` and ask the user to switch modes.
- Stay chat-only until the user confirms a proposal is ready to hand off.
- Before the user confirms that the context is sufficient, do not inspect the repository.

## Decision-Complete Gate

- Confirm from the current user-agent conversation alone that Goal, Scope, Approach, Validation, Plan Strategy, selected grounding producer, and any applicable Artifact/Evidence Boundary are complete before `proposal-ready`.
- Goal is complete only if the concrete deliverable is settled.
- Scope is complete only if in-scope and out-of-scope boundaries are settled.
- Approach is complete only if artifact shape, touched surfaces, create-versus-edit behavior, and ownership boundaries are settled.
- Validation is complete only if task-local checks, shared checks, final validation, runner or prerequisite requirements, and review-only exceptions are settled.
- Plan Strategy is complete only if it is classified as `step-execution`, `loop-exploration`, or `hybrid`; old context without an explicit strategy defaults to `step-execution`, but new proposals should state the strategy explicitly.
- Use `loop-exploration` when the goal is fixed but progress depends on bounded batches, produced artifacts, metrics, stop/skip/retry rules, and feedback from prior runs.
- Use `hybrid` when a loop-exploration objective also needs deterministic setup, gate, or promote tasks.
- For `loop-exploration` or `hybrid`, settle baseline metric, target metric or convergence threshold, batch selection, batch size, artifact path/type, stop/skip/retry rules, no-full-rerun guard, formal/destructive write boundary, and final validation.
- The Artifact/Evidence Boundary is complete only if the proposal states the exact artifact paths, evidence paths, committed/gitignored/transient output policy, source-of-truth status, relevant state or environment cleanliness assumptions, validation gates that must run before `review-ready`, gates that are intentionally post-commit or manual, and what metadata proves the artifact or evidence came from the intended source revision.
- When multiple requirement or design inputs are present, `Source-of-truth refs` must state precedence only for the sources actually present. Examples include a concrete GitHub issue URL, OpenSpec change, formal contract handoff, PRD, reviewed solution package, grounding brief, or current user conversation; do not list absent source categories just to cover every scenario.
- If any validation command depends on generated output, repository state, local credentials, external services, sibling repositories, a clean source tree, or other external prerequisites, settle that prerequisite explicitly before `proposal-ready`; do not leave it as an implementation-time decision.
- If any gate dimension is incomplete, output `clarifying` or `blocked`; do not enter `proposal-ready`.
- Do not infer that a task is documentation-only, analysis-only, or review-only unless the conversation explicitly settles that no code behavior, code-owned definitions, runtime logic, or executable validation needs to change.

## Execution Contract Completeness

Before `proposal-ready`, the plan must be concrete enough that the executor can implement without choosing product or release semantics during execution.

- Block `proposal-ready` if the executor would still need to decide any exact CLI command, API name, function name, skill id, plugin id, file name, directory name, manifest field, argument, default, unsupported value, error behavior, output paths and output layout, install destination, scope, overwrite behavior, mutation boundary, target support matrix, artifact state, compatibility policy, validation proof, or important negative proof.
- For CLI or API work, name the concrete command or API shape, input flags or parameters, default behavior, output location, unsupported cases, and at least one direct behavior check.
- For generated outputs, name every generated path and classify it as committed, transient, ignored, evidence-only, or source-of-truth; if an output must not be produced as a side effect, name the forbidden path explicitly.
- For multi-target work, provide a target support matrix where each target is supported, unsupported with a clear failure, or explicitly out of scope.
- For installation or other filesystem mutation, name the source artifact shape, destination path, user/project scope behavior, overwrite policy, verification-before-write rule, and rollback or partial-write expectation when relevant.
- For validation, require direct create/install/verify commands or file assertions for the primary success path and the most important negative path when direct behavior can be checked.

## Blocking Open Questions

Treat any open question as blocking if it could change:

- deliverable
- module, service, or file scope
- implementation shape
- API, auth, data, storage, or ops contract
- generated artifact location
- evidence or report location
- state cleanliness, ignored-output, or mutation boundary
- validation command or validation mode
- required proof mode
- whether the work is review-only

`proposal-ready` may include only non-blocking Open Questions. If an open question could change execution, return to clarification.

## Ambiguity Traps

When the user or issue context contains any of these terms, convert it into an explicit list or ask a clarifying question:

- active components
- all modules
- existing validation
- supported variants
- permission behavior
- safe to run
- current framework
- generated outputs
- review-only
- coverage or quality gate

Do not use repository exploration to decide these terms on the user's behalf.

## Grounding Producer Selection

- `plan-issue` chooses the needed producer; it does not perform repository grounding itself.
- Use generic `ground-plan` when the plan intent is settled but repository facts, path landing, validation surfaces, or option tradeoffs still need read-only grounding.
- Use a specialized grounding producer instead of generic `ground-plan` when one owns the domain: direct activity requirement-to-solution for activity solution packages, direct Go refactor planning for Go refactor briefs, or another explicitly named producer.
- Use direct contract work only as a contract/source producer for API or stream-visible contract facts; do not treat it as a generic repository-grounding producer.
- If the current conversation already contains a reviewed solution package, refactor brief, contract handoff, or other confirmed grounding handoff, cite that handoff as source material and do not require another grounding pass unless gaps remain.
- If repository facts are needed, state which producer must confirm them and block or hand off instead of exploring the repository from `plan-issue`.

## Validation Reality Check

- Before `proposal-ready`, identify the validation runner, exact command or review-only marker, and prerequisites.
- If validation depends on environment setup, name the setup requirement, such as `.venv` activation, `uv run`, tox environment, service dependency, or dry-run-only scope.
- If the issue requires proof beyond ordinary unit/static checks, state whether that proof is task-local, a shared check, a final gate, or explicitly post-commit/manual; do not replace it with a weaker surrogate unless the user has accepted that boundary.
- If the issue produces derived outputs, state whether they are committed, gitignored, transient, or source of truth, and name where reviewable evidence will be recorded.
- Do not propose commands that look plausible but have no confirmed executable path or prerequisites.

## Proposal-Ready

- State that blocking decisions are resolved.
- Present the settled Goal, Scope, Approach, Validation model, Plan Strategy, and any required Artifact/Evidence Boundary.
- Include an `Artifact/Evidence Boundary` section for `loop-exploration`, `hybrid`, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans.
- Include `Source-of-truth refs` when more than one source is present or when a downstream agent could confuse a plan, handoff, or evidence artifact with the authoritative requirement source.
- Include the selected grounding producer and the exact facts or handoff it must supply before `finalize-plan`, or state that existing confirmed source material is already sufficient.
- Keep the proposal in chat. Do not write files.

The `Artifact/Evidence Boundary` section must be specific enough for `finalize-plan` to copy into `plan.md` / `tasks.md` without inventing:

- artifact and evidence paths, including which paths are committed, gitignored, transient, or source of truth;
- task-local checks, shared checks, final validation, required proof gates, and review-only exceptions;
- state cleanliness, ignored-output, mutation, or rollback policy when relevant;
- metadata or provenance fields needed to prove source revision, baseline, incrementality, or generated-output lineage;
- batch selection, batch size, stop/skip/retry rules, and no-full-rerun guard for `loop-exploration` or `hybrid`;
- formal/destructive write boundary and promotion rules.
- source-of-truth refs and precedence when multiple requirement, design, contract, or evidence inputs exist.

## Handoff

- After the user reviews and confirms the proposal, stop and hand off to `finalize-plan`.
- The handoff should tell the user that the selected grounding producer supplies repository or domain facts when needed, and `finalize-plan` is responsible only for writing confirmed facts into `plan.md` and `tasks.md`.
