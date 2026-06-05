# Artifact And Evidence Boundary

Ordinary source edits can usually rely on `plan.md`, `tasks.md`, and validation commands. The following work needs an explicit Artifact/Evidence Boundary:

- loop-exploration or hybrid plans.
- Generated code, import/export, batch processing, migrations, or data writes.
- Screenshots, traces, reports, baselines, benchmarks, or browser evidence.
- Design prototypes, throwaway prototypes, or visual comparisons.
- Formal/destructive writes, real environment changes, or external system side effects.
- Tasks where evidence is itself a deliverable.

## Required Fields

- Source-of-truth refs: real issues, specs, contracts, designs, PRDs, conversations, or grounding handoffs. Do not list sources that do not exist.
- Artifact paths: every artifact location and whether it is committed, local, gitignored, transient, prototype-only, or production source.
- Evidence paths: screenshot, log, report, trace, run record, baseline, or review artifact locations and whether they are committed.
- State policy: cache, browser storage, database state, temporary directories, environment variables, cleanup, and rollback.
- Validation gates: task-local, shared, final, manual, and review-only boundaries.
- Metadata/provenance: commit, baseline, schema, fixture, design source, viewport, browser, environment, and batch information.
- Batch/write boundary: selection, batch size, stop/skip/retry behavior, no-full-rerun policy, promotion criteria, and destructive/formal write rules.

## Workflow Artifacts

The generated Forma workflow keeps process state under `plans/issue-<id>/`. Treat `plan.md`, `tasks.md`, `runs/`, review snapshots, and validation logs as workflow evidence. Project-specific commit or publication rules belong in the target repository plan, not in the reusable sample profile.
