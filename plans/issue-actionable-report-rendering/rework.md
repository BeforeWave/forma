# Rework Ledger

## Rework 001: Tighten reconcile quality gate

Source:
- direct-human-feedback + forma-reconcile

Feedback:
- Reconcile should not act as a low-bar completion check. It should judge whether a delivery is worth accepting, including whether the result used the right source layer, reduced future agent error, avoided unnecessary product-surface expansion, and reached the best practical outcome within scope.

Classification:
- delivery-revision

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue introduced structured handoff, doctor/init/build/explain routing, workflow guidance, and generated workflow boundaries. The feedback targets the same workflow-quality gate that evaluates those deliveries, not a new product goal.
- The correction can be executed as ordinary task work by tightening reconcile methodology/rules and focused generated-output/tests without changing the issue plan's goal, scope, or task model.

User Confirmation:
- confirmed: user requested writing the rework contract in this side conversation.

Appended Tasks:
- rework-001-tighten-reconcile-quality-gate

## Rework 002: Remove default agent handoff skeleton from init

Source:
- direct-human-feedback

Feedback:
- `forma init` should not create an agent handoff or agent review prompt by default. The agent already uses profile-authoring principles to generate a draft profile; afterward the review decision is a human review of whether those rules should become durable project workflow source, not another agent reviewing the same principles again.

Classification:
- task-rework

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue introduced `forma init` remediation, profile-local reinstall workflow guidance, and the `.forma-profile/` source layout. The correction changes the initialized draft-source structure and docs/tests for that same product surface.
- The correction can be executed as ordinary task work by removing the default agent handoff skeleton from `forma init`, keeping profile source and human review packet structure, and updating focused docs/tests without changing the issue-level plan contract.

User Confirmation:
- confirmed: user explicitly requested using the rework skill to redefine this correction.

Appended Tasks:
- rework-002-remove-agent-handoff-init-skeleton

## Rework 003: Move default profile home to .forma

Source:
- direct-human-feedback

Feedback:
- The default generated profile home should be `.forma`, not `.forma-profile`. The profile source should be one structured section inside Forma's repo-local workflow home, while the prior rework direction still applies: do not generate a default agent handoff or agent review prompt.

Classification:
- task-rework

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue owns `forma init` remediation, repo-local profile skeleton layout, config pointers, docs, and focused tests for deterministic initialization.
- The correction can be executed as ordinary task work by changing the default init output path and docs/tests from `.forma-profile/` to `.forma/`, while preserving human review packet semantics and reinstall workflow behavior.

User Confirmation:
- confirmed: user explicitly requested using the rework skill and making `.forma` the default profile generation path.

Appended Tasks:
- rework-003-move-default-profile-home-to-dot-forma

## Rework 004: Put workflow runtime state under .forma/state

Source:
- direct-human-feedback

Feedback:
- Runtime workflow state should live under the `.forma` repo-local home, but it must be independently ignored. Generate `.forma/.gitignore` to ignore `/state/`, move the workflow runner cache from `.forma-workflow/` to `.forma/state/workflow/`, and do not preserve compatibility with the old `.forma-workflow/` cache path.

Classification:
- task-rework

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue owns `forma init` remediation, repo-local workflow home structure, runner handoff behavior, docs, and focused tests for deterministic workflow operation.
- The correction can be executed as ordinary task work by updating init skeleton output, workflow runner state path, docs/tests, and ignore policy without changing the issue-level plan contract.

User Confirmation:
- confirmed: user explicitly requested handing this `.forma/state` ignore and workflow-state decision to the rework skill.

Appended Tasks:
- rework-004-move-workflow-state-under-dot-forma-state

## Rework 005: Validate explain profile renderer docs in main thread

Source:
- direct-human-feedback

Feedback:
- `forma explain profile` already supports `human`, `agent`, and `json` output, and the side conversation added usage-document wording for those audience boundaries. The remaining work should be handled by the main thread: fold the documentation context into the active issue, verify CLI output and docs agree, and avoid treating side-thread lightweight validation as the full implementation gate.

Classification:
- task-rework

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue owns the `human` / `agent` / `json` rendering contract, `forma explain ...` handoff behavior, public usage docs, and final validation gates.
- The correction can be executed as ordinary task work by reconciling usage docs with current CLI behavior, running focused renderer checks, and recording verification without changing the issue-level plan contract.

User Confirmation:
- confirmed: user requested turning the current side-conversation context into a rework contract for the rework skill.

Appended Tasks:
- rework-005-validate-explain-profile-renderer-docs

## Rework 006: Flatten `.forma` profile source and remove default review packet persistence

Source:
- direct-human-feedback

Feedback:
- The self-profile source should not add extra config or a nested `.forma/profile/` layer when `.forma/` itself can be the profile directory. Profile YAML files can live directly under `.forma/`, reference material should remain under `.forma/references/`, and `reinstall-workflow.sh` should sit beside `profile.yaml`.
- Review packets are authoring/review handoff material, not something `forma init` should persist by default. If generated during profile authoring, the user should choose whether to keep them.
- Agent-friendly structure is allowed when it reduces repeated work, but extra config, indirection, or persistent files without a current need are overdesign.

Classification:
- task-rework

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue owns `forma init`, repo-local profile layout, profile-local reinstall handoff, docs/tests, and self-profile source location.
- The correction narrows the design surface created by rework-003 and rework-004 without changing the issue goal: keep `.forma/` as the repo-local home, but make the profile directory itself simple and durable.

User Confirmation:
- confirmed: user directly requested flattening the `.forma` profile layout, removing config overdesign, preserving references as references, and not leaving review packets by default.

Appended Tasks:
- rework-006-flatten-dot-forma-profile-source

## Rework 007: Settle install facts and reinstall script bootstrap boundary

Source:
- direct-human-feedback

Feedback:
- Profile-backed build/install must not make agents rediscover local install commands every time. During profile confirmation and the first build/install exploration, the agent should continue the conversation with the user to settle install facts such as artifact kind, target, plugin id, marketplace, marketplace source, install selector, and visibility check.
- Once those facts are confirmed, they should be written into the profile-local `reinstall-workflow.sh` as fixed facts. Stable reinstall scripts must not list marketplaces, keep runtime plugin id or marketplace choices open, or print agent handoff text.
- `human` build output should remain concise and safe for scripts; `agent` and `json` should carry the executable bootstrap/install handoff. Missing or incomplete reinstall scripts are bootstrap-incomplete, not reusable reinstall success.

Classification:
- delivery-revision

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue introduced the shared human/agent/json output model, profile-local reinstall workflow guidance, build next actions, `forma init`, and `forma explain` handoff behavior.
- The correction can be executed as ordinary task work by tightening report rendering, explain/build next actions, init reinstall skeleton behavior, docs, and focused tests without changing the issue-level goal or task model.

User Confirmation:
- confirmed: user confirmed the rework contract in this side conversation.

Appended Tasks:
- rework-007-profile-install-fact-bootstrap

## Rework 008: Add plan and task contract check before commit

Source:
- direct-human-feedback

Feedback:
- Plan/task contract generation and rework task appending have the same failure mode: structured task defects can be created during lock or rework, but the workflow currently catches them too late at review-ready. Contract authors should run a read-only plan/tasks check before asking the user to confirm and commit a plan or rework contract.

Classification:
- task-rework

Same-Issue Rationale:
- This remains inside the active actionable-report-rendering issue because the issue owns workflow runner behavior, structured task contracts, lock/rework handoff boundaries, and profile-injected workflow guidance.
- The correction can be executed as ordinary task work by adding a read-only contract check and requiring lock/rework generated workflows to report it before committing plan/task changes, without changing the issue-level goal or task model.

User Confirmation:
- confirmed: user explicitly requested handing this contract-check gap to the rework skill after reinstalling the strengthened profile workflow.

Appended Tasks:
- rework-008-contract-schema-check
