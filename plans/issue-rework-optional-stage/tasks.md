- [x] [optional-mend-stage-contract] Add optional `mend` stage plumbing
Accept: Task Type=step; profile loading, composer resources, manifest hashing, plugin localization, and stage ordering recognize internal kind `mend` as default disabled while preserving five-stage default generation
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py
Use-Check: diff-check
Depends: none
Constraint: do not add `mend` to default enabled stage kinds or standalone creator default generation

- [x] [rework-methodology] Add `forma-rework` methodology behavior
Accept: Task Type=step; `mend` stage source and `rework-rules.md` define direct human feedback intake, `forma-reconcile` output intake, same-issue classification, `rework.md` ledger format, flat `tasks.md` rework task appending, explicit rework contract confirmation, and execute/showhand handoff
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py
Use-Check: diff-check
Depends: optional-mend-stage-contract
Constraint: `tasks.md` must remain a flat structured task list with no rework heading or source prose

- [x] [verifier-and-creator-sync] Update verifier and packaged creator surfaces for `mend`
Accept: Task Type=step; Layer 2 verifier recognizes `mend`/`forma-rework`, enforces core rework markers, and packaged creator verification assets stay aligned with developer CLI behavior without changing five-stage temporary-injection defaults
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py tests/test_creator_builder.py
Validate: uv run --extra dev forma verify source/skill-creator/
Use-Check: source-creator-verify
Use-Check: diff-check
Depends: rework-methodology
Constraint: keep `source/methodology` as the methodology source of truth; do not duplicate rework behavior prose inside `source/skill-creator` except verifier requirements

- [x] [self-profile-rework-enable] Enable and verify `forma-rework` only in Forma self profile
Accept: Task Type=step; `profiles/forma-self/forma-self-iteration.yaml` emits `forma-rework`, Codex plugin output generated from the self-profile localizes it to `rework` with qualified trigger `forma:rework`, and default no-profile generation still omits rework
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_cli.py
Use-Check: creator-profile-tests
Use-Check: diff-check
Depends: verifier-and-creator-sync
Constraint: write self-profile generated validation output only under `/tmp`, `/private/tmp`, or `$TMPDIR`; do not commit self-profile output into `dist/`

- [x] [release-surface-drift-gate] Verify default release surfaces and update only required creator artifacts
Accept: Task Type=gate; release-surface drift is checked, default skill bundles/plugins remain five-stage without `forma-rework` or `rework`, and any committed `dist/skills/*/forma-creator` update is limited to packaged optional methodology/verifier asset drift required by the source change
Validate: uv run --extra dev forma drift --release-surface
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_verifier.py tests/test_cli.py
Use-Check: source-creator-verify
Use-Check: diff-check
Depends: self-profile-rework-enable
Constraint: do not add `forma-rework` to `dist/skill-bundles/*` or plugin-local `rework` to `dist/plugins/*`; if drift requires default release regeneration, regenerate from the default no-profile source only
