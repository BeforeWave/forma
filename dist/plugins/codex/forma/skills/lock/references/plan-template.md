# Issue Plan

Use this template only after the issue is already discussed enough to execute.
If Goal, Scope, Approach, Validation, Plan Strategy, or any applicable Artifact/Evidence Boundary is still unclear, keep clarifying before writing this file.

## Goal

- Describe the outcome this issue should achieve.

## Plan Strategy

- Use `Plan Strategy: step-execution` for ordinary ordered implementation.
- Use `Plan Strategy: loop-exploration` when progress depends on bounded batches, artifacts, and metrics.
- Use `Plan Strategy: hybrid` when iterative batches and deterministic setup/gate/promote tasks are both needed.
- If omitted in a legacy plan, the default is `Plan Strategy: step-execution`.

## Scope

- State what is in scope for this issue.
- State important non-goals or out-of-scope work that should stay excluded.

## Approach

- Summarize the implementation strategy.
- Call out key files, interfaces, or systems that will change.

## Artifact/Evidence Boundary

Use this section for `loop-exploration`, `hybrid`, generated-artifact, import/export, migration, batch-processing, formal/destructive write, or evidence-producing plans. Omit it when the issue has no separate artifact, evidence, state, or write boundary beyond ordinary source edits and tests.

- Source-of-truth refs: when multiple requirement, design, contract, solution, grounding, or conversation inputs exist, name the actual refs and precedence. Do not enumerate absent source categories.
- Artifact paths: name generated/local/source-of-truth outputs and whether each is committed, gitignored, or transient.
- Evidence paths: name logs, reports, run records, or review artifacts and whether they are committed.
- State policy: state cleanliness, ignored-output, mutation, rollback, or environment requirements when relevant.
- Validation gates: state task-local checks, shared checks, required proof gates, final validation, and any post-commit/manual gates.
- Metadata/provenance: state required commit, baseline, schema, extractor, fixture, or source lineage fields.
- Batch/write boundary: for loop or hybrid plans, state batch selection/size, stop/skip/retry, no-full-rerun, destructive/formal write, and promotion rules.

## Constraints

- Keep changes minimal and scoped to this issue.
- Do not rewrite unrelated code.
- Preserve compatibility unless the issue explicitly requires a breaking change.

## Acceptance Criteria

- List concrete user-visible or system-visible outcomes.
- Keep criteria consistent with the scope above.
- For behavior-changing work, state the tests or regression coverage that will prove the change.

## Validation

List reusable issue-level shared checks below. Each block must use:
`Check: <id>`
`Command: <shell>`
Optional:
`Note: <text>`
Only include task-safe checks here: they must still be expected to pass before unrelated tasks are finished.
Leave this section empty if the issue does not need shared checks.

Example:

```text
Check: unit-fast
Command: <project-native validation command>
Note: shared by tasks that can safely reuse this check while the wider issue is still incomplete
```

## Final Validation

List one issue-level final validation command per line in the fenced `sh` block below.
`scripts/forma-workflow.sh review-ready <issue-id>` executes this block only when preparing the last remaining task for review, and `complete` reuses the reviewed staged snapshot and cached result without rerunning it.
These commands run through the same non-login, non-interactive shell path as task `Validate:` lines and shared `## Validation` checks. They inherit the invoking process environment but do not read user profile or rc files, and the runner clears `BASH_ENV` / `ENV`.
Each line is executed as an independent command, so it must be self-contained. Do not use standalone variable assignment, `cd`, or `export` lines; fold multi-step setup, execution, and cleanup into one command line.
When a command needs cleanup with a captured exit code, use portable variable names such as `exit_status`; avoid shell-reserved names such as zsh's read-only `status`.
For documentation-only or analysis-only issues, replace executable commands with exactly one marker comment:
`# no-programmatic-validation: <reason>`
Use this section for checks that are not task-safe, including whole-issue regression coverage.
When planning the last task, avoid copying the same command into both that task's `Validate:` lines and `## Final Validation` if a narrower task-local proof is available.

```sh
echo "replace me with project validation commands"
```

Completion requirements:

- `scripts/forma-workflow.sh review-ready <issue-id>` must pass the current task's `Validate:` lines, or that task must explicitly declare `Validate: # no-programmatic-validation: <reason>`.
- Every `Use-Check:` reference must resolve to a shared check in `## Validation`, and each referenced shared check must pass during `review-ready`.
- When preparing the last task for review, every `## Final Validation` command must pass, or the plan must explicitly declare `# no-programmatic-validation: <reason>`.
- `scripts/forma-workflow.sh review-ready <issue-id>` stages the reviewed task snapshot in Git for later completion.
- `scripts/forma-workflow.sh complete <issue-id>` must reuse the same reviewed staged snapshot and review cache for the same task instead of rerunning validation.
- `plan.md` remains unchanged during task execution.
- `tasks.md` is only updated by `scripts/forma-workflow.sh complete <issue-id>`.
- Evidence is recorded in `./plans/issue-<id>/runs/`.

## Risks / Notes

- Note any known risks, follow-ups, or assumptions.

## Loop-Exploration Example

Use this shape only when `Plan Strategy: loop-exploration` or `Plan Strategy: hybrid` is selected. Do not keep example text in the final plan.

````md
## Goal

- Increase reviewed derived-output coverage for selected input units.

## Plan Strategy

- Plan Strategy: loop-exploration

## Scope

- In scope: process the selected batch list and produce derived artifacts plus run reports.
- Out of scope: full-scope reruns, irreversible writes, and promotion of derived outputs without explicit evidence.

## Approach

- Baseline metric: current reviewed output count from `logs/<run-id>/baseline.json`.
- Target metric: at least N additional reviewed outputs, or stop when two consecutive batches produce no eligible outputs.
- Batch rule: process at most N selected input units per loop-batch task from the settled batch manifest.
- Artifact path: write batch reports under `logs/<run-id>/` and task evidence under `plans/issue-<id>/runs/`.
- Write boundary: derived outputs may be written only to the settled artifact directory; source-of-truth promotion requires a later `Task Type=promote` task.

## Artifact/Evidence Boundary

- Artifacts: derived outputs are written only to the settled artifact directory; reports are written under `logs/<run-id>/`.
- Evidence: task evidence is recorded under `plans/issue-<id>/runs/`.
- State policy: generated reports are local outputs and must not be treated as source-of-truth input.
- Gates: each batch validates its report; final validation summarizes the selected run id.
- Metadata: every report records source revision, selected batch manifest, and output counts.
- Batch/write boundary: batch size <= N input units; empty selection stops blocked; promotion requires a later `Task Type=promote` task.

## Validation

Check: batch-report-schema
Command: python3 tools/validate_batch_report.py logs/<run-id>

## Final Validation

```sh
python3 tools/summarize_batch_progress.py logs/<run-id>
```
````

Example loop task:

```text
- [ ] [batch-01] Run the first selected batch
Accept: Task Type=loop-batch; selected batch produces a report with output counts, skip reasons, and no unintended full-run fallback
Validate: python3 tools/validate_batch_report.py logs/<run-id>/batch-01.json
Use-Check: batch-report-schema
Constraint: batch size <= N input units; if selection is empty, stop blocked instead of running the full scope
```
