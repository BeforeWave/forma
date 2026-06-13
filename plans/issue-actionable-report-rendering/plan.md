# Issue Plan

## Goal

- Introduce a typed actionable report envelope and `human` / `agent` / `json` rendering contract for Forma commands that need structured handoff, without forcing every command to emit diagnostic `facts` / `findings` / `evidence` sections.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- Iteration Area: cross-layer

## Scope

- In scope:
  - Add a shared report envelope for command results and handoffs, with command-specific typed sections and renderers for `human`, `agent`, and `json`.
  - Add `forma doctor repo [path]` as a read-only repo agent-operability diagnosis with `ready`, `needs-agent`, `needs-human`, and `unsafe` statuses.
  - Migrate artifact diagnosis behind the same rendering contract while preserving the current `forma doctor <path>` route and its install-route facts.
  - Add `forma init` as deterministic remediation, not diagnosis: it consumes or recomputes repo doctor findings and supports dry-run planning for `.forma/config.yaml`, profile skeletons, review packet skeletons, and agent handoff prompts.
  - Use the current project's `.forma-profile/` directory as the default profile generation home when no profile output path is specified. Create it when needed and treat it as git-trackable project source, not ignored scratch output.
  - Adjust Forma's sanitized sample profile directories to reflect the same active-source versus referenced-resource separation where useful, without adding sample install scripts, review packets, or `AGENTS.md`.
  - Remove committed sample generated outputs under `examples/generated/` and stop maintaining generated example baselines; users who like a sample profile should run the build command themselves.
  - Replace separate profile-local build/install workflow script guidance with a single profile-local `reinstall-workflow.sh` entrypoint that builds, verifies/drifts, installs, and checks visibility for repeated local use.
  - Route profile-backed `forma build bundle` / `forma build plugin` follow-up guidance through structured next actions.
  - Route `forma explain ...` guidance through structured handoff sections while preserving guidance as the command's core purpose.
  - Update command help, public docs, and tests for the new format contract and command boundaries.
- Out of scope:
  - Do not connect the CLI to an LLM or automatically extract long-term profile rules.
  - Do not make every command use `facts` / `findings` / `evidence`; those are diagnostic sections only.
  - Do not move Codex plugin installation into `forma install`.
  - Do not make `forma init` claim that a profile has been reviewed.
  - Do not commit downstream-specific marketplace paths, private install roots, or organization-specific workflow commands into Forma examples or release artifacts.

## Approach

- Add a developer CLI report layer under `src/forma/` with:
  - an envelope containing `schema`, `command`, `subject`, `status`, `summary`, optional typed sections, and `next_actions`;
  - renderer support for exactly `human`, `agent`, and `json`;
  - section types that commands opt into, such as diagnostic findings, artifact install route, produced artifacts, planned changes, applied changes, guidance, handoff, warnings, blockers, and stop conditions.
- Start with a narrow CLI structure refactor so later behavior does not keep growing inside `cli.py`:
  - keep `src/forma/cli.py` focused on Click argument parsing, domain calls, output format selection, and exit-code mapping;
  - add or split domain modules for the new surfaces, such as report rendering, repo doctor, init remediation, and build handoff;
  - keep artifact doctor separate from repo doctor;
  - keep guidance assembly in `explain.py` but make its command output compatible with the report/handoff layer;
  - avoid moving Layer 2 verifier report internals into the new developer CLI report model.
- Keep existing command semantics but move handoff-producing text into reports:
  - `doctor repo` builds a diagnostic report from repo files and static checks.
  - artifact doctor wraps existing verification and install-route facts in the report envelope.
  - `build bundle/plugin` still writes artifacts, then emits outcome and next action sections.
  - `init` emits planned or applied remediation sections and defaults to a safe dry-run unless the implementation explicitly requires an apply flag.
  - When `init` creates profile-facing files without an explicit output path, it writes them under `.forma-profile/` in the target project, creates the directory if missing, and reports that the directory should be tracked by Git when the generated profile assets are accepted.
  - `explain` emits guidance and handoff sections, not diagnostic findings.
- Keep sample profile cleanup narrow:
  - profile YAML files remain the active sample source;
  - sample `references/` files and profile-declared script resources are referenced resources, not active defaults unless the profile points to them;
  - the GitHub issue helper used by the sample backend profile remains a profile resource/script, not a reusable install workflow script;
  - do not add `.forma-profile/AGENTS.md`, review packet archives, or build/install workflow scripts to sanitized examples in this issue.
- Remove generated example baselines:
  - delete the committed `examples/generated/` sample backend generated outputs;
  - update docs/tests so examples are profile source plus instructions, not committed generated baselines;
  - do not add replacement generated example outputs.
- Standardize public output format naming on `--format human|agent|json`, defaulting to `human`. Existing `--json` routes may remain as compatibility shims only where already present, but new behavior should be expressed through `--format`.
- Preserve settled install and bootstrap rules in structured agent output:
  - If a profile directory contains `reinstall-workflow.sh`, agents must run that script from the profile directory before reconstructing build/install commands.
  - If `reinstall-workflow.sh` is missing, that is a bootstrap state; a manual one-off flow is allowed only when explicitly requested and must be reported as one-off.
  - `reinstall-workflow.sh` is the single reusable entrypoint for build plus install, including generation, drift when profile-backed, verify, target-specific install or marketplace refresh, and visibility checks.
  - Codex plugin output is a generated plugin root, not a marketplace root. Codex owns marketplace registration, install, enabled state, and new-thread discovery.
  - Profile-backed plugin postprocess order is build, drift against raw profile output, postprocess, final verify. After postprocess, drift is not the final gate.
  - Prefer profile fields such as `plugin.display_name` over postprocess when the profile can express the desired plugin metadata.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user conversation decisions take precedence; the `forma:ground` handoff supplies repository implementation facts.
- Committed artifact paths: source, tests, docs, sample profile source layout changes, deletion of committed sample generated outputs under `examples/generated/`, and planning files changed by this issue. For downstream projects using `forma init`, accepted profile assets under `.forma-profile/` are intended to be git-trackable project source. No generated release artifact is required by default for this Forma issue.
- Transient artifact paths: any smoke-generated workflow output must use `/tmp`, `/private/tmp`, or `$TMPDIR` and must not be committed. `.forma-profile/` is not transient scratch output.
- Evidence paths: execution proof is recorded under `plans/issue-actionable-report-rendering/runs/`; implementation decisions that affect later review should be recorded in `plans/issue-actionable-report-rendering/implement-notes.md`.
- State policy: preserve the current dirty worktree outside this issue's files; do not write local home-directory paths into tracked files.
- Validation gates: task-local tests should prove each command's behavior before review; final validation must run the shared full test, source creator verify, and whitespace gates.
- Generated-output policy: do not regenerate `examples/generated/`; remove it and keep samples profile-only. Regenerate `dist/` only if implementation changes creator-visible packaged guidance, verifier behavior bundled into creator output, or release artifacts.

## Constraints

- Keep Layer 1, Layer 2, Layer 3, CLI, docs, and generated-output responsibilities explicit.
- Keep `source/skill-creator/scripts/forma_verifier/` stdlib-only if any verifier-adjacent reporting is touched.
- Do a narrow structure refactor before adding repo doctor, init, or build/explain behavior; do not continue adding long handoff text directly in `cli.py`.
- Do not replace the verifier's rule report with a universal diagnostic model; wrap or reference it where needed.
- Keep reader-facing docs concise; detailed agent execution policy belongs in agent rendering or `forma explain agent`.
- Preserve current artifact doctor facts and exit-code behavior unless a task explicitly updates tests and docs for a changed contract.
- Do not add public formats beyond `human`, `agent`, and `json`.

## Acceptance Criteria

- Commands that support structured handoff can render `human`, `agent`, and `json` from one report envelope while using command-specific sections.
- `cli.py` delegates structured output and handoff construction to focused modules instead of owning long command-specific prose.
- `forma doctor repo [path]` read-only diagnosis reports repo agent-operability status and actionable next steps without mutating the repo.
- Artifact doctor still identifies artifact kind, target, verification status, Forma install support, install route, blockers, and next steps.
- `forma init` provides deterministic remediation plans or applied changes without claiming profile review.
- When no profile output path is provided, `forma init` plans or creates profile-facing files under `.forma-profile/`, creates the directory if needed, and communicates that accepted contents should be git-tracked.
- Sanitized sample profiles keep active sample YAML separate from referenced resources and do not grow review packets, `AGENTS.md`, or install workflow scripts.
- Committed generated example baselines are removed and are not replaced.
- Profile-local automation is presented as one `reinstall-workflow.sh` entrypoint, not separate build and install scripts.
- Profile-backed build output no longer relies on ad hoc stdout-only handoff for verify, drift, install, profile-local script bootstrap, or Codex plugin next actions.
- `forma explain ...` keeps guidance as guidance but can render agent-facing handoff and JSON from structured sections.
- Tests cover human, agent, and JSON render paths for the report layer and the migrated commands.

## Validation

Check: cli-report-focused
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Note: use for report rendering, doctor, init, build, and explain command behavior.

Check: layer1-layer2-if-touched
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py
Note: use only when verifier or creator-bundled reporting behavior changes.

Check: docs-links
Command: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Note: use when README, STRUCTURE, AGENTS, or docs pages change.

Check: source-creator-verify
Command: uv run --extra dev forma verify source/skill-creator/
Note: shared gate for creator-visible or verifier-adjacent changes.

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
git diff --check
```

## Risks / Notes

- Existing `verify`, `doctor`, and `explain` already expose different JSON shapes. Implementation should avoid a noisy breaking migration unless the task explicitly updates tests, docs, and command help.
- The current working tree has unrelated or prior-turn dirty changes. Execution must preserve them and scope commits to this issue's files.
