- Mandatory Decision Gate: enter `proposal-ready` only after Goal, Scope, Approach, Validation, Plan Strategy, and any applicable Artifact/Evidence Boundary are complete.
- Goal is complete only if the concrete deliverable is settled.
- Scope is complete only if in-scope and out-of-scope boundaries are settled.
- Approach is complete only if artifact shape, touched surfaces, create-versus-edit behavior, and ownership boundaries are settled.
- Validation is complete only if task-local checks, shared checks, final validation, runner or prerequisite requirements, and review-only exceptions are settled.
{{ include: fragments/shape/plan-strategy-adds.md }}
{{ include: fragments/shape/artifact-evidence-boundary-adds.md }}
- If any Decision Gate dimension is incomplete, output `clarifying` or `blocked`; do not enter `proposal-ready`.
- Treat any question that could change deliverable, module/service/file scope, implementation shape, API/auth/data/storage/ops contract, generated artifact location, evidence/report location, state cleanliness or mutation boundary, validation command or proof mode, or whether work is review-only as blocking.
- `proposal-ready` may include only non-blocking Open Questions; if an open question could change execution, return to clarification.
- Treat broad terms such as "active components", "all modules", "existing validation", "supported variants", "permission behavior", "safe to run", "current framework", "generated outputs", "review-only", or "coverage/quality gate" as ambiguity traps that require an explicit list or a clarifying question.
- If the current conversation is missing enough information that no reviewable proposal can be formed yet, use the compact `blocked` or `clarifying` format from `references/output-format.md` instead of inventing a partial plan.
