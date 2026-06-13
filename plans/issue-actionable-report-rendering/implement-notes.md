# Implement Notes

## Execution Decisions

- Process backfill: the side conversation found that committed `dist/` output started as product-default profile-backed output in `649154d`, but `bdb9e6c` rebuilt the public release surface from the Forma self-iteration profile. That made the public release artifacts carry repo-management behavior (`hone`/`mend`, self overlays, and self-profile references) instead of the product default profile.
- The corrective rebuild uses the normal `forma build bundle/plugin --target ... --output ...` path with no `--profile`. In this repository that means the packaged product default profile, not no rules and not `.forma/profile.yaml`.
- Added `scripts/build-dist.sh` so future dist refreshes use a fixed command sequence instead of asking agents to infer the five release paths and target commands each time.
- `scripts/build-dist.sh` intentionally does not rebuild `dist/skills/*/forma-creator` by default; creator artifacts remain deferred unless a creator-specific issue opts in.
- `scripts/build-dist.sh` does not use `forma drift --release-surface` as a gate because the current drift release-surface map does not model the packaged default profile as the source and reports `unknown-source` for this valid rebuild path. The script gates on per-artifact `forma verify` instead.
- The Forma self-profile reinstall workflow now reads local install facts from ignored `.forma/reinstall-workflow.env` instead of requiring command-line environment variables every time. The tracked script remains reusable while local marketplace paths and selectors stay out of open-source tracked files.
- `forma doctor` became a Click group with a compatibility router so `forma doctor <path>` still diagnoses artifacts while `forma doctor repo [path]` is available for read-only repository operability diagnosis. This keeps existing artifact handoff behavior while separating repo diagnosis from artifact diagnosis.
- Artifact doctor output is wrapped in the shared actionable report envelope, but the existing artifact diagnosis data remains available in report metadata. This avoids replacing the verifier or artifact diagnosis internals with the new CLI report model.
- `forma init` defaults to dry-run planning. File creation requires `--apply`, and generated profile-facing files go under `.forma-profile/` by default as draft, git-trackable project source. The command does not claim the profile is reviewed.
- Profile-local repeated automation uses one `reinstall-workflow.sh` entrypoint instead of separate build and install scripts. Build and explain handoffs now treat a missing script as bootstrap state and preserve one-off manual flow as an explicit exception.
- `examples/generated/` was removed instead of regenerated. Sample profiles remain source examples; users who want to inspect generated output should run build commands locally.
- `drift --release-surface` now checks committed `dist/` release artifacts, not removed sample generated baselines.
- `forma explain ... --format json` now returns the actionable report envelope. The previous markdown guidance remains available in `metadata.markdown` so tools can render or inspect the original guidance body.
- The source methodology now treats command/API shape, output schema, default behavior, generated/install boundaries, reinstall handoff automation, and validation model changes as mandatory `implement-notes.md` triggers. This fixes the missing-notes failure at generated-skill source level rather than relying on a one-off reminder.
- The workflow runner's pre-staged-index failure now explains that the runner owns review staging, names `git add` and `git rm` as index-mutating commands, and points agents to `git restore --staged <path>` while preserving working-tree changes. This addresses the `git rm` stop at the runner guidance source instead of documenting only the incident.
- Because these rules are part of generated skill behavior, profile-backed committed release artifacts were regenerated from `profiles/forma-self/forma-self-iteration.yaml` instead of leaving source and installed/plugin surfaces divergent. Product-level `dist/skills/*/forma-creator` artifacts were left deferred until a dedicated creator isolation/refactor issue resumes that path.

## Process Notes

- These decisions should have been recorded during the relevant tasks because they affect later review and future maintenance. The run evidence captured validation and changed files, but it did not explain the non-trivial implementation choices above.
- During `remove-generated-examples`, using `git rm -r examples/generated` staged deletions and caused the workflow runner to reject `review-ready` with a dirty index. The correct workflow-compatible sequence is to remove files without leaving staged changes before invoking the runner, or immediately unstage with `git restore --staged <path>` while preserving the working-tree deletion.

## Task 9: rework-001-tighten-reconcile-quality-gate

Outcome:
- Tightened reconcile methodology so `aligned` requires both contract fit and the best practical outcome within the confirmed scope.

Decision Notes:
- Chose to encode the stricter gate in the canonical hone stage and `reconcile-rules.md` rather than in CLI output or docs, because the issue is about how generated reconcile skills classify delivery quality.
- Kept product-level `forma-creator` deferred and limited generated output refresh to profile-backed workflow artifacts.

Plan Gaps Found:
- The original reconcile rules allowed `aligned` for deliveries that matched the stage frame but were merely adequate rather than the best practical outcome.

Classifications:
- delivery-revision: user feedback requested same-issue correction of the completed workflow-quality gate.

Deviations From Plan:
- None

Follow-ups:
- None

## Task 16: rework-008-contract-schema-check

Outcome:
- Added a read-only workflow runner command, `check <issue-id>`, that parses the active issue's `plan.md`, `tasks.md`, and `rework.md` when rework tasks exist; it validates required plan sections, plan strategy, validation section shape, structured task schema, dependency references, shared-check references, and rework ledger task linkage.
- Kept `check` independent from review state: it does not stage files, create review cache, mark tasks complete, create run evidence, or require clean plan/task files.
- Added Forma self-profile `workflow_adds` and `output_adds` for lock and rework stages so generated Forma lock/rework workflows require the contract check result before asking for plan/rework commit permission.
- Added focused workflow runner tests for dirty contract checks, duplicate structured task fields, unknown shared-check references, missing plan contract sections, and missing rework ledger task linkage.

Decision Notes:
- Implemented the reusable check in the shared runner because the parser already lives there and the command is a generic read-only safety gate.
- Kept lock/rework stage requirements in `.forma/project.yaml` profile additions instead of changing shared seal/mend methodology text.
- Used wording that references the bundled workflow runner rather than a literal `scripts/forma-workflow.sh` file path in profile additions, because seal and mend skills do not bundle that script resource.

Plan Gaps Found:
- Structured task and plan/rework contract defects were previously caught during review-ready or later manual inspection, which is too late for lock and rework contract authors who need to verify plan/task/rework files before committing them.

Classifications:
- task-rework: committed rework contract `f614529` requested a pre-commit plan/tasks contract check.

Deviations From Plan:
- None

Follow-ups:
- None

## Task 15: rework-007-profile-install-fact-bootstrap

Outcome:
- Split profile-local reinstall status into missing, bootstrap-incomplete, and reusable. Profile-backed build agent/json output now treats missing or bootstrap-incomplete scripts as a stop condition until install facts are confirmed and the completed script has run.
- Kept default human build output concise by hiding build next actions and agent-only reinstall/Codex handoff sections, so profile-local scripts can call build commands in human mode.
- Changed `forma init` to create a bootstrap-incomplete `reinstall-workflow.sh` skeleton that exits before doing work until artifact kind, target, plugin id when relevant, marketplace facts when relevant, install selector, and visibility check are written into a fixed-fact script.
- Updated `forma explain agent`, `forma explain profile`, Codex plugin handoff text, usage docs, and focused CLI tests to state that marketplace listing is bootstrap discovery or diagnostics, not a stable reinstall-script step.
- Quoted a dirty self-profile rework constraint in `.forma/project.yaml` so the profile remains valid YAML for profile-backed build validation.

Decision Notes:
- Presence of `reinstall-workflow.sh` is no longer enough to call a profile reusable. The script must be complete rather than the init skeleton marked with `FORMA_REINSTALL_WORKFLOW_BOOTSTRAP_INCOMPLETE=1`.
- Agent/json output carries install facts, stop conditions, forbidden actions, and Codex handoff details. Human output reports the produced artifact only.
- Stable profile-local reinstall scripts should encode fixed facts and use a confirmed Codex selector; `codex plugin marketplace list` belongs to bootstrap discovery or diagnostics before those facts are written.
- Added `workflow_adds` and `output_adds` to the profile schema instead of changing canonical `mend` methodology, because project-specific completion gates and output fields should be injectable through profile source rather than promoted into every rework skill.

Plan Gaps Found:
- Earlier behavior treated any present reinstall script as reusable and made the init skeleton look runnable through environment-variable choices, which could let agents report reusable success before local install facts were confirmed.
- Existing build JSON exposed `codex plugin marketplace list` as a regular next action, which blurred bootstrap discovery with the stable reinstall path.

Classifications:
- delivery-revision: committed rework contract `29da380` requested profile-backed install fact bootstrap and human build output boundary corrections.

Deviations From Plan:
- Included a minimal `.forma/project.yaml` YAML quoting repair because the current dirty self-profile source blocked the required profile-backed build test path.

Follow-ups:
- None

## Task 12: rework-004-move-workflow-state-under-dot-forma-state

Outcome:
- Moved canonical workflow runner review cache/state from `.forma-workflow/` to `.forma/state/workflow/` and added `.forma/.gitignore` init output that ignores only `/state/`.

Decision Notes:
- Chose `.forma/state/workflow/issue-<id>/` as the runner state root so tracked workflow source and runtime state excluded from Git share the `.forma/` repo-local home while keeping Git policy separated.
- Legacy `.forma-workflow/` review cache remains transient deletion-safe state outside the new runner state contract.
- Kept Rework 003's default `.forma/` profile home and Rework 002's no-agent-handoff default output.

Plan Gaps Found:
- The prior `.forma/` default home did not distinguish tracked source from runtime state, and the runner still wrote cache outside the repo-local Forma home.

Classifications:
- task-rework: committed rework contract `3750530` requested the workflow runtime state correction.

Deviations From Plan:
- None

Follow-ups:
- Regenerate and reinstall workflow artifacts in a separate task if the installed local Forma plugin should immediately use the new runner cache path.

## Task 13: rework-005-validate-explain-profile-renderer-docs

Outcome:
- Aligned `forma explain profile` usage docs, CLI behavior, and tests for the `human`, `agent`, and `json` renderer boundary.

Decision Notes:
- Made the human renderer concise for profile explanation while keeping the full executable authoring contract in the agent renderer and structured tool output in JSON.
- Kept `explain profile` sections as guidance and sources rather than diagnostic findings or evidence.
- Treated the side-thread docs edit as input, then validated the main-thread implementation through the task commands.

Plan Gaps Found:
- The previous docs could describe renderer intent, but the human renderer still emitted the full canonical guidance body.

Classifications:
- task-rework: committed rework contract `971d6d8` requested main-thread validation of explain profile renderer docs.

Deviations From Plan:
- None

Follow-ups:
- None

## Task 14: rework-006-flatten-dot-forma-profile-source

Outcome:
- Moved Forma's self-profile source from `profiles/forma-self/` into `.forma/` with `profile.yaml`, supporting profile YAML files, `references/`, and `reinstall-workflow.sh` directly under the repo-local profile directory.
- Removed `.forma/config.yaml` from `forma init` and from the self-profile migration. `forma init` now creates `.forma/profile.yaml`, `.forma/reinstall-workflow.sh`, and `.forma/.gitignore`.
- Removed default persistent review packet creation from `forma init`; profile authoring may still produce review packet text for the user, but keeping it in the repo is a user decision.
- Tightened self-profile references so examples are profile source by default, generated example output is not committed by default, and validation guidance avoids treating full test suites or `source/skill-creator` verification as universal gates.

Decision Notes:
- Chose `.forma/` itself as the profile directory because adding `.forma/config.yaml` and a nested `.forma/profile/` layer created unnecessary indirection for the current need.
- Kept `.forma/references/` as a subdirectory because those files are referenced material, not profile unit files.
- Kept `.forma/reinstall-workflow.sh` beside `.forma/profile.yaml` so profile-backed build output can point agents to a stable reusable reinstall flow without reconstructing commands.
- Added a default self-profile constraint that agent-friendly structure is allowed when it reduces repeated work, but extra config, indirection, or persistent files require a current need.

Plan Gaps Found:
- Earlier rework entries still described `.forma/config.yaml`, `.forma/profile/`, and human review material as default persistent init output. The final product direction is flatter and avoids persisting review packets by default.

Classifications:
- task-rework: direct user feedback requested flattening `.forma`, removing config overdesign, preserving references as references, and making review packet persistence optional.

Deviations From Plan:
- Removed default review packet file creation from `forma init`, superseding the earlier rework-002/rework-003 assumption that human review material should be a default persisted skeleton.
- Removed config pointer creation from `forma init`, superseding the earlier rework-003 assumption that `.forma/config.yaml` should exist.

Follow-ups:
- None

## Task 11: rework-003-move-default-profile-home-to-dot-forma

Outcome:
- Moved the default `forma init` repo-local workflow home from `.forma-profile/` to `.forma/`.

Decision Notes:
- Chose `.forma/` as the single default workflow home for config pointers, structured profile source, human review material, and profile-local reinstall automation.
- Kept the Rework 002 boundary: default init output still does not create an agent handoff or agent review prompt.
- Preserved legacy `.forma-profile/` recognition in repo doctor as a compatibility signal, while default init no longer creates it.

Plan Gaps Found:
- Rework 002 corrected the handoff boundary but still kept a separate `.forma-profile/` home; this rework collapses the default repo-local workflow source under `.forma/`.

Classifications:
- task-rework: committed rework contract `28cd2a5` requested the default workflow home correction.

Deviations From Plan:
- None

Follow-ups:
- None

## Task 10: rework-002-remove-agent-handoff-init-skeleton

Outcome:
- Removed the default agent handoff prompt skeleton from `forma init` while keeping profile source, human review material, and the profile-local reinstall workflow.

Decision Notes:
- Chose to remove the handoff skeleton instead of renaming it, because init should create deterministic profile source and human review material, not another agent prompt surface.
- Kept `.forma-profile/profile/profile.yaml`, `.forma-profile/review/review-packet.md`, and `.forma-profile/reinstall-workflow.sh` as the default git-trackable `.forma-profile/` structure.
- Clarified that agents may draft candidate profile rules from profile-authoring principles, but review is a human durability decision before rules become long-term project workflow source.

Plan Gaps Found:
- The previous init structure made an agent handoff/review prompt part of the default source layout, which blurred the human review boundary.

Classifications:
- task-rework: committed rework contract `b8ef191` requested this default init surface correction.

Deviations From Plan:
- None

Follow-ups:
- None
