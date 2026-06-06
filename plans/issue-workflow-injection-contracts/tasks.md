- [x] [layer-1-injection-classification] Add the temporary injection classification contract
Accept: Task Type=step; `source/skill-creator` documents the temporary injection generation standard and canonical profile authoring principles; installed creator instructions require classifying natural-language constraints into minimal default, stage-specific, or conditional overlay targets; agents must output the temporary injection file path plus a classification table before generation
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_creator_builder.py
Validate: uv run --extra dev forma build-creator --output /tmp/forma-creator-dist --target codex
Validate: uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator/
Depends: none
Constraint: do not add unsupported metadata keys to temporary injection JSON

- [x] [profile-execution-classification] Apply the classification contract to profiles and generated bundles
Accept: Task Type=step; sample profiles and `profiles/forma-self` demonstrate light `constraints.default`, stage-specific planning/execution rules, and conditional overlays for heavy scenarios; `forma explain profile` and `forma explain temporary-injection` expose the same rules from canonical references for agents that cannot inspect Forma source; package runtime assets let pip/pipx installed CLI run explain, default create, and default build-creator from arbitrary cwd without a Forma source checkout; committed backend generated baselines are regenerated; generated and installed Codex `forma-pour` / `forma-flow` keep routine execution narrow
Validate: uv run --extra dev pytest -p no:cacheprovider tests/
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_runtime_assets.py
Validate: uv run --extra dev forma explain profile --target codex
Validate: uv run --extra dev forma explain temporary-injection --format json --target codex
Validate: uv run --extra dev forma build-creator --output /tmp/forma-creator-dist-default --target codex
Validate: uv run --extra dev forma create --target codex --profile examples/profiles/sample-backend/sample-backend-go.yaml --output /tmp/forma-create-default-methodology-codex
Validate: uv run --extra dev forma verify source/skill-creator/
Validate: uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-codex/
Validate: uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-claude-code/
Validate: uv run --extra dev forma verify /tmp/forma-self-iteration-codex/
Validate: uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator/
Validate: uv run --extra dev forma verify /tmp/forma-creator-dist-default/codex/forma-creator/
Validate: uv run --extra dev forma verify /tmp/forma-create-default-methodology-codex/
Validate: git diff --check
Depends: layer-1-injection-classification
Constraint: keep `constraints.default` light; put broad docs, generated-baseline, migration, governance, or cross-layer rules in conditional overlays
