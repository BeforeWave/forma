- [x] [cli-structure-refactor] Split CLI orchestration from command domain output
Accept: Task Type=step; `src/forma/cli.py` delegates structured output, build handoff, doctor domains, and init remediation to focused modules while keeping Click parsing, format selection, and exit-code mapping in the CLI layer
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Depends: none
Constraint: do not add new repo doctor, init, or build/explain behavior before the module boundaries are in place
Constraint: keep artifact doctor separate from repo doctor and do not move Layer 2 verifier report internals into the developer CLI report model

- [x] [report-envelope-renderers] Add the typed report envelope and renderers
Accept: Task Type=step; `src/forma` has a shared actionable report envelope with command-specific typed sections and renderers for exactly `human`, `agent`, and `json`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Depends: cli-structure-refactor
Constraint: do not force all commands to include diagnostic facts/findings/evidence sections
Constraint: preserve the verifier's existing report model unless a later task explicitly wraps it for command output

- [x] [doctor-reporting] Add repo doctor and migrate artifact doctor output
Accept: Task Type=step; `forma doctor repo [path]` reports read-only repo agent-operability status and artifact doctor output uses the shared report rendering contract while preserving current artifact install-route facts
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Depends: report-envelope-renderers
Constraint: `forma doctor <path>` must continue to diagnose generated artifacts unless tests and docs explicitly introduce an additional `forma doctor artifact <path>` route
Constraint: repo doctor must not mutate files, create profiles, run installs, or claim profile review

- [x] [init-remediation] Add deterministic `forma init` remediation
Accept: Task Type=step; `forma init` consumes or recomputes repo doctor-style findings and renders planned or applied deterministic remediation for `.forma/config.yaml`, `.forma-profile/` profile skeletons, review packet skeletons, and agent handoff prompts
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Depends: doctor-reporting
Constraint: default behavior must be safe and must not claim a profile is reviewed
Constraint: when no profile output path is specified, profile-facing files go under the target project's `.forma-profile/`, the directory is created if missing, and accepted contents are presented as git-trackable source rather than ignored scratch output
Constraint: profile-local repeated automation should be represented as one `reinstall-workflow.sh` entrypoint that chains build, drift or verify, install or marketplace refresh, and visibility checks
Constraint: do not write local home-directory paths or downstream-specific marketplace paths into tracked examples or docs

- [x] [sample-profile-layout] Align sanitized sample profile layout with active-source/resource boundaries
Accept: Task Type=step; `examples/profiles` keeps sample profile YAML as active source and referenced markdown/script resources as resources, with the GitHub issue helper treated as a profile resource rather than an install workflow script
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_docs_links.py
Depends: init-remediation
Constraint: do not add sample review packets, `.forma-profile/AGENTS.md`, `build-workflow.sh`, `install-workflow.sh`, or `reinstall-workflow.sh` to sanitized examples
Constraint: keep sample content generic and avoid downstream private workflow commands or marketplace paths

- [x] [remove-generated-examples] Remove committed generated example baselines
Accept: Task Type=step; `examples/generated/` committed sample outputs are removed and docs/tests treat examples as profile sources that users can build locally instead of maintained generated baselines
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_docs_links.py
Depends: sample-profile-layout
Constraint: do not add replacement generated example outputs
Constraint: keep `dist/` release artifacts governed separately from profile-only examples

- [x] [handoff-next-actions] Route build and explain handoffs through report next actions
Accept: Task Type=step; profile-backed `forma build bundle/plugin` and `forma explain ...` emit human/agent/json output from structured sections for follow-up commands, stop conditions, and forbidden actions
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Depends: report-envelope-renderers
Constraint: profile-local `reinstall-workflow.sh` precedence, bootstrap-state handling, one-off reporting, Codex marketplace selector guidance, new-thread discovery, and postprocess ordering must be preserved in agent-facing next actions
Constraint: `explain` remains guidance/handoff output, not a diagnostic report

- [x] [docs-and-final-gates] Update docs, command help, and final validation
Accept: Task Type=gate; public docs, command help, and tests describe `human|agent|json`, `doctor repo`, artifact doctor, `init` remediation, and structured build/explain handoff without duplicating detailed agent policy into reader docs
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Use-Check: cli-report-focused
Use-Check: source-creator-verify
Depends: doctor-reporting
Depends: init-remediation
Depends: sample-profile-layout
Depends: remove-generated-examples
Depends: handoff-next-actions
Constraint: keep usage docs as command reference; detailed executable agent policy belongs in agent rendering or `forma explain agent`
Constraint: regenerate `dist/` only if implementation changes creator-visible packaged guidance, verifier behavior bundled into creator output, or release artifacts; do not regenerate `examples/generated/`

- [x] [rework-001-tighten-reconcile-quality-gate] Tighten reconcile aligned criteria
Accept: Task Type=step; reconcile source rules require both contract fit and best practical outcome before returning aligned, and route merely adequate but lower-quality outcomes to acceptable-deviation, delivery-revision, source-rework, or plan-rework as appropriate
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_cli.py
Use-Check: source-creator-verify
Depends: docs-and-final-gates
Constraint: do not implement source changes outside reconcile methodology/rules, generated profile-backed workflow output, and focused tests/docs needed to lock the stricter quality gate

- [x] [rework-002-remove-agent-handoff-init-skeleton] Remove default agent handoff skeleton from init
Accept: Task Type=step; `forma init` no longer creates a default agent handoff or agent review prompt file, the default `.forma-profile/` structure keeps profile source plus human review material and reinstall workflow only, and docs/tests describe review as a human durability decision after agent-authored draft profile generation
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "init_dry_run or init_apply or doctor_repo_reports_ready"
Depends: init-remediation
Depends: docs-and-final-gates
Constraint: do not remove profile-authoring guidance, profile source skeletons, human review packet material, or profile-local reinstall workflow behavior

- [x] [rework-003-move-default-profile-home-to-dot-forma] Move default profile home to .forma
Accept: Task Type=step; `forma init` uses `.forma/` as the default repo-local workflow home for generated profile source, human review material, reinstall workflow, and config pointers, and no longer creates `.forma-profile/` by default
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "init_dry_run or init_apply or doctor_repo_reports_ready"
Depends: rework-002-remove-agent-handoff-init-skeleton
Constraint: preserve the Rework 002 decision that default init output must not include an agent handoff or agent review prompt
Constraint: keep profile source structured under a profile section, keep review material human-facing, and keep reinstall workflow as the reusable profile-local entrypoint

- [x] [rework-004-move-workflow-state-under-dot-forma-state] Put workflow runtime state under .forma/state
Accept: Task Type=step; `forma init` creates `.forma/.gitignore` that ignores `/state/`, workflow runner transient review cache/state moves from `.forma-workflow/` to `.forma/state/workflow/`, and no compatibility path reads or writes legacy `.forma-workflow/`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_workflow_runner.py -k "init_dry_run or init_apply or workflow"
Depends: rework-003-move-default-profile-home-to-dot-forma
Constraint: keep `.forma/` itself git-trackable, keep profile/review/reinstall files tracked by default, and ignore only runtime state under `.forma/state/`
Constraint: do not migrate or read old `.forma-workflow/` cache; old transient cache may be deleted

- [x] [rework-005-validate-explain-profile-renderer-docs] Validate explain profile renderer docs in main thread
Accept: Task Type=step; usage docs and CLI behavior consistently describe `forma explain profile --format human|agent|json`, including that `human` is concise reader guidance, `agent` is an executable authoring contract, `json` is structured tool output, and `explain` emits guidance rather than diagnostic findings/evidence
Validate: uv run --extra dev forma explain profile --format human --target codex
Validate: uv run --extra dev forma explain profile --format agent --target codex
Validate: uv run --extra dev forma explain profile --format json --target codex
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Depends: handoff-next-actions
Depends: docs-and-final-gates
Constraint: main-thread validation owns the full implementation result; side-conversation `git diff --check` is only lightweight context and must not be reported as the final gate
Constraint: keep detailed executable agent policy in agent rendering or `forma explain agent`, and keep public usage docs concise

- [x] [rework-006-flatten-dot-forma-profile-source] Flatten `.forma` profile source and remove default review packet persistence
Accept: Task Type=step; Forma's self-profile source lives directly under `.forma/` as `profile.yaml`, supporting profile YAML files, `references/`, and `reinstall-workflow.sh`; `forma init` creates `.forma/profile.yaml`, `.forma/reinstall-workflow.sh`, and `.forma/.gitignore` without `.forma/config.yaml`, `.forma/profile/`, or a default persisted review packet
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_creator.py
Validate: uv run --extra dev forma build plugin --target codex --profile .forma/profile.yaml --output /private/tmp/forma-self-flat-plugin
Validate: uv run --extra dev forma drift /private/tmp/forma-self-flat-plugin --profile .forma/profile.yaml
Validate: uv run --extra dev forma verify /private/tmp/forma-self-flat-plugin
Validate: git diff --check
Depends: rework-003-move-default-profile-home-to-dot-forma
Depends: rework-004-move-workflow-state-under-dot-forma-state
Constraint: keep reference material under `.forma/references/`, not flattened into the profile root
Constraint: review packets may be produced during profile authoring, but `forma init` must ask whether to keep them rather than leaving a persisted review file by default
Constraint: prefer the minimum durable design surface that solves the issue; do not add config, indirection, or persistent files without a current need

- [x] [rework-007-profile-install-fact-bootstrap] Fix profile-backed install fact bootstrap and human build output boundaries
Accept: Task Type=step; `forma explain profile`, `forma explain agent`, and profile-backed `forma build bundle/plugin --format agent|json` require agents to continue with the user after build/install exploration to settle install facts and complete a profile-local `reinstall-workflow.sh` before reporting reusable reinstall success; default `human` build output remains concise and does not render profile-local reinstall handoff, Codex marketplace handoff, stop conditions, forbidden actions, or build next actions, so profile-local scripts can call build commands in human mode; `forma init` creates only a bootstrap-incomplete reinstall skeleton when install facts are unknown, and ready reinstall scripts are documented as fixed-fact scripts that do not list marketplaces or leave plugin id, marketplace, selector, or source refresh decisions open at runtime
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "build_plugin or build_bundle or explain_agent or explain_profile or init_apply"
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Validate: git diff --check
Depends: rework-006-flatten-dot-forma-profile-source
Depends: handoff-next-actions
Constraint: keep Codex plugin installation outside `forma install`; Codex marketplace listing belongs only to bootstrap discovery or diagnostics, not stable reinstall script execution
Constraint: do not add public output formats beyond `human`, `agent`, and `json`
Constraint: do not write downstream-specific marketplace paths, local home-directory paths, or organization-specific install selectors into Forma examples or public docs

- [x] [rework-008-contract-schema-check] Add read-only plan/tasks contract check before lock and rework commits
Accept: Task Type=step; the workflow runner exposes a read-only plan/tasks contract check for the active issue that catches structured task schema defects before execution, and lock/rework generated workflows require running and reporting this check before committing plan/task or rework contract files
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_runner.py -k "check or structured"
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_cli.py -k "workflow_adds or explain_profile or init_apply"
Validate: git diff --check
Depends: rework-007-profile-install-fact-bootstrap
Constraint: the check is read-only; it must not run task validation commands, stage files, write review cache, mark tasks complete, or create run evidence
Constraint: keep profile-specific lock/rework requirements injectable through profile workflow/output additions instead of changing shared methodology unless the user explicitly approves methodology changes
Constraint: do not disturb the existing review-ready staged implementation snapshot while materializing this rework contract
