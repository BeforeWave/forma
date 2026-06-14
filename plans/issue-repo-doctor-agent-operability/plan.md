# Issue Plan

## Goal

- Rework `forma doctor` into a repo-only agent-operability diagnostic and connect it to `forma init --from-report` as a deterministic handoff/configuration bridge for later Agent remediation.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- Iteration Area: cross-layer

## Scope

- In scope:
  - Remove artifact doctor behavior and the hidden `forma doctor <path>` compatibility route.
  - Redesign `forma doctor repo [path] --format human|agent|json` around repo agent-operability facts, findings, handoff, and human-decision routing.
  - Add `forma init --from-report <report>` so a repo doctor report can materialize deterministic `.forma` base configuration, confirmed facts, file/checklists, Agent remediation handoff inputs, and human-decision lists.
  - Update CLI help, `forma explain agent`, usage/targets docs, and focused CLI tests to match the new command boundary.
- Out of scope:
  - Do not keep `forma doctor artifact` or `forma doctor <artifact>`.
  - Do not treat `.forma/profile.yaml` presence as core repo readiness.
  - Do not make `init --from-report` perform semantic remediation, modify project docs automatically, or claim a repo is now agent-friendly.
  - Do not change `forma verify`, `forma install`, Layer 1 verifier behavior, Layer 3 creator emission, `dist/` release artifacts, or example generated baselines.

## Approach

- Delete the artifact doctor CLI surface from `src/forma/cli.py` and remove or orphan the artifact-diagnosis implementation in `src/forma/doctor.py`; generated artifact validation remains owned by `forma verify`, while install compatibility remains owned by `forma install` and build/plugin handoff text.
- Replace `src/forma/repo_doctor.py`'s static five-finding `ActionableReport` model with a repo-doctor report model whose JSON schema is dedicated to repo agent-operability:
  - top-level fields: `schema`, `command`, `subject`, `status`, `summary`, `facts`, `findings`, `evidence`, `confidence`, `programmatic_actions`, `agent_handoffs`, `human_decisions`, `unsafe_blockers`;
  - core domains: `entrypoint`, `task-state`, `source-boundaries`, `validation`, `setup-contract`, `human-gates`, `noise-control`, `instruction-quality`, `tooling-signals`;
  - optional integration domain: `agent-specific-integrations.forma`.
- Implement repo-doctor renderers so `human` is concise, `agent` is an executable semantic-remediation handoff, and `json` is the full tool schema.
- Extend `src/forma/init_remediation.py` and CLI options so `forma init --from-report <report> [--apply] [--format human|agent|json] [path]` validates the report schema/subject, creates or plans only deterministic `.forma` files, and writes report-derived facts/checklists/handoffs without approving semantic rules.
- Keep implementation source-owned under `src/forma/`; tests stay in `tests/test_cli.py`; docs changes stay in `docs/usage*.md`, `docs/targets*.md`, and `src/forma/explain.py` tests/guidance.

## Artifact/Evidence Boundary

- Source-of-truth refs: current user conversation and the `forma:ground` handoff are authoritative. Earlier plans that preserved artifact doctor behavior are historical context only and are superseded.
- Committed artifacts: source, tests, docs, and planning files changed by this issue. No committed generated workflow output is required.
- Transient artifacts: any generated or init smoke output must use pytest temp directories or `/tmp`, `/private/tmp`, or `$TMPDIR`; do not write self-profile output into `dist/`.
- Evidence paths: task execution evidence will be recorded under `plans/issue-repo-doctor-agent-operability/runs/`; implementation decisions that affect later review should be recorded in `plans/issue-repo-doctor-agent-operability/implement-notes.md`.
- State policy: preserve unrelated dirty `.forma/*` work already in the worktree; do not write local home/workspace absolute paths into tracked source, docs, profiles, tests, examples, or generated release artifacts.
- Write boundary: `init --from-report` may create deterministic `.forma` base configuration and report-derived lists/handoff inputs; it must not automatically edit `AGENTS.md`, source-boundary docs, validation docs, setup scripts, or other semantic remediation targets unless a future explicit task adds a fully deterministic action.

## Constraints

- Programmatic code is the glue layer: it collects facts, classifies findings, creates deterministic files/lists, and hands work off. Agent remediation is responsible for making a repo semantically agent-friendly.
- `needs-agent` means an Agent must review or propose semantic remediation. `needs-human` is reserved for owner decisions such as durable rule adoption, credentials, release/publish, destructive operations, or external writes.
- `pyproject.toml`, `package.json`, Makefiles, CI config, and similar files are tooling signals, not validation contracts by themselves.
- Missing `.forma/` is not a core readiness failure; it is an optional integration opportunity and possible programmatic action.
- Keep public docs reader-facing and concise; detailed remediation instructions belong in `agent` renderer output or `forma explain agent`.

## Acceptance Criteria

- `forma doctor <path>` and hidden `forma doctor artifact` are not accepted command paths.
- `forma doctor repo --format json` emits the dedicated repo-doctor schema and no longer uses `forma.actionable-report.v1`.
- Repo readiness is driven by core agent-operability contracts, not Forma profile presence or bare tool-config presence.
- `forma doctor repo --format agent` gives an Agent clear read-first files, semantic review questions, forbidden actions, return shape, and human-decision markers.
- `forma init --from-report <report>` validates report schema and subject, then plans or applies deterministic `.forma` base configuration plus report-derived facts, file/checklists, Agent handoff, and human-decision lists.
- `init --from-report` does not approve semantic rules, does not claim the repo became agent-friendly, and does not default-create review packets.
- Docs and `forma explain agent` no longer recommend artifact doctor; generated artifact checks route through `forma verify`, `forma install`, and build/plugin handoff guidance.

## Validation

## Final Validation

```sh
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "doctor or init or explain or verify or install"
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
uv run --extra dev python -m pytest -p no:cacheprovider tests/
git diff --check
```

## Risks / Notes

- This intentionally breaks old artifact doctor compatibility. The replacement path is explicit: use `forma verify` for generated artifact validity and `forma install` or build/plugin guidance for install boundaries.
