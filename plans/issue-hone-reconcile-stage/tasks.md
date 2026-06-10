- [x] [agents-path-policy] Record tracked-file absolute path guard
Accept: Task Type=step; `AGENTS.md` states that tracked files must not contain non-temporary absolute filesystem paths, with temporary evidence paths limited to `/tmp`, `/private/tmp`, or `$TMPDIR`
Validate: git diff --check AGENTS.md
Depends: none
Constraint: do not edit README, docs, generated output, or unrelated repository instructions

- [x] [optional-stage-contract] Add optional `hone` stage contract to source and profile loading
Accept: Task Type=step; source compiler/profile code recognizes internal kind `hone` as default disabled, validates stage-specific profile keys, and preserves existing five-stage default generation
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py
Use-Check: diff-check
Depends: agents-path-policy
Constraint: default no-profile bundle/plugin output must not emit `hone` or `forma-reconcile`

- [x] [reconcile-methodology] Add stage-aware `forma-reconcile` methodology behavior
Accept: Task Type=step; `hone` stage source and `reconcile-rules.md` define read-only reconciliation, target resolution from explicit feedback/recent trigger/review cache/runs/diff, stage-local constraint evaluation, and `delivery-revision` routing for all-completed implementation feedback
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py
Use-Check: diff-check
Depends: optional-stage-contract
Constraint: task implementation rework must require `implement-notes.md`; plan-level feedback must not be recorded as implementation notes

- [x] [bundled-creator-verifier] Update bundled creator and verifier for optional `hone`
Accept: Task Type=step; bundled creator generation and verifier rules recognize optional `hone`/`forma-reconcile` mappings while still validating existing five-stage bundles and plugins
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator_builder.py tests/test_verifier.py tests/test_layer_1_dogfood.py
Validate: uv run --extra dev forma verify source/skill-creator/
Use-Check: diff-check
Depends: reconcile-methodology
Constraint: standalone creator logic must stay behaviorally aligned with developer CLI generation

- [x] [self-profile-validation] Enable and validate `forma-reconcile` only in Forma self profile
Accept: Task Type=step; `profiles/forma-self/forma-self-iteration.yaml` emits `forma-reconcile` for self-profile generation, while temporary no-profile generation still emits only the five existing stages
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_verifier.py
Validate: uv run --extra dev forma verify source/skill-creator/
Use-Check: creator-profile-tests
Use-Check: verifier-tests
Use-Check: diff-check
Depends: bundled-creator-verifier
Constraint: write temporary generated validation output only under `/tmp`, `/private/tmp`, or `$TMPDIR`; do not commit `dist/` or generated release surfaces
