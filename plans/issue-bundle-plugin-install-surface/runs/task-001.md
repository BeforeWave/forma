# Task Evidence

- Task: [bundle-terminology-contract] Rename suite/create contracts to bundle contracts across Layer 3, Layer 1, Layer 2, manifests, and tests
- Completed At (UTC): 2026-06-07T13:19:55Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- STRUCTURE.md
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/.forma-manifest.json
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/.forma-manifest.json
- examples/profiles/sample-software/software.yaml
- plans/issue-bundle-plugin-install-surface/implement-notes.md
- source/skill-creator/scripts/create.py
- source/skill-creator/scripts/forma_verifier/__init__.py
- source/skill-creator/scripts/forma_verifier/report.py
- source/skill-creator/scripts/forma_verifier/rules.py
- source/skill-creator/scripts/forma_verifier/runner.py
- src/forma/cli.py
- src/forma/creator/__init__.py
- src/forma/creator/composer.py
- src/forma/creator/emitter.py
- src/forma/creator/manifest.py
- tests/fixtures/invalid-bundle/shape/SKILL.md
- tests/fixtures/valid-bundle/flow/SKILL.md
- tests/fixtures/valid-bundle/gauge/SKILL.md
- tests/fixtures/valid-bundle/pour/SKILL.md
- tests/fixtures/valid-bundle/seal/SKILL.md
- tests/fixtures/valid-bundle/shape/SKILL.md
- tests/fixtures/valid-bundle/shape/references/output-format.md
- tests/test_creator.py
- tests/test_creator_builder.py
- tests/test_verifier.py

## Validation Results
- PASS [task]: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_verifier.py tests/test_layer_1_dogfood.py
- PASS [task]: uv run --extra dev forma verify source/skill-creator/

## Risks / Unresolved Items
- None recorded.
