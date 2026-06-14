- [x] [remove-artifact-doctor] Remove artifact doctor command routing and guidance
Accept: Task Type=step; `forma doctor` no longer routes bare paths or hidden artifact subcommands, while generated artifact validation/install boundaries remain available through `verify`, `install`, and build/plugin guidance
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "doctor_rejects_legacy_artifact_path or verify_json or install_rejects_codex_plugin_artifacts"
Depends: none
Constraint: do not remove or weaken `forma verify`, `forma install`, artifact classification used by install/drift/adopt, or Codex plugin install guidance outside the doctor path

- [x] [repo-doctor-report] Redesign `doctor repo` around repo agent-operability
Accept: Task Type=step; `forma doctor repo [path] --format human|agent|json` reports core repo agent-operability facts/findings/handoff with Forma as an optional integration instead of a readiness prerequisite
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "doctor_repo"
Depends: remove-artifact-doctor
Constraint: `pyproject.toml`, `package.json`, Makefiles, and CI config count as tooling signals only; `.forma/profile.yaml` must not make an otherwise unfriendly repo ready

- [x] [init-from-report] Add report-driven init glue
Accept: Task Type=step; `forma init --from-report <report>` validates the repo-doctor schema/subject and plans or applies deterministic `.forma` base configuration plus report-derived facts, file/checklists, Agent remediation handoff inputs, and human-decision lists
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "init"
Depends: repo-doctor-report
Constraint: init must not claim semantic rules are approved, must not claim the repo is now agent-friendly, and must not automatically modify AGENTS/docs/source-boundary/validation/setup files unless a future report action is fully deterministic

- [x] [docs-explain-sync] Sync docs, help, and agent command guidance
Accept: Task Type=step; CLI help, `forma explain agent`, usage docs, targets docs, and tests describe repo-only doctor behavior and route generated artifact checks through verify/install/build handoff surfaces
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "explain_agent or doctor"
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Depends: init-from-report
Constraint: do not refresh `dist/`, do not change Layer 1 verifier or Layer 3 creator emission, and keep reader-facing docs concise

- [x] [rework-001-reader-value-docs] Align Forma adoption value in reader-facing docs
Accept: Task Type=step; README, Chinese README, concepts docs, and quick-start docs preserve the existing first-screen/product structure while adding the direct user value of Forma: fewer repeated reminders, less drift, clearer review evidence, and more consistent validation through an agent workflow
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Validate: rg "repeated reminders|less drift|clearer review|more consistent validation" README.md docs
Validate: rg "反复提醒|跑偏|review|验证" README.zh-CN.md docs
Depends: docs-explain-sync
Constraint: do not replace the README opening wholesale, do not add a redundant top-level "Why Teams Use Forma" section in the first pass, and keep implementation concepts such as `.forma`, profile, build, verify, and install below the reader-value frame

- [x] [rework-001-cli-adoption-contract] Normalize Forma adoption wording and confirmations across CLI report surfaces
Accept: Task Type=step; repo doctor, init-from-report, and explain-agent user-facing text describe Forma as project-rule workflow management, avoid implementation-first "base configuration" wording where workflow source is meant, keep cleanup-by-explicit-request policy, and expose `owner_confirmations` consistently in rendered and JSON output
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "doctor or init or explain_agent"
Validate: git diff --check
Depends: rework-001-reader-value-docs
Constraint: do not actively clean `.forma`, do not ask whether to keep `.forma`, do not claim Forma guarantees rule compliance, and keep profile approval, build/verify, install target/scope, and commit as separate confirmations
