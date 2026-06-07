# Task Evidence

- Task: [plan-lock-sharpness-contract] Encode sharp planning gates into the default `forma-plan` and `forma-lock` workflow
- Completed At (UTC): 2026-06-07T13:36:35Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/.forma-manifest.json
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/backend-plan-first-finalize-plan/SKILL.md
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/backend-plan-first-finalize-plan/references/planning-rules.md
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/backend-plan-first-plan-issue/references/plan-issue-rules.md
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/.forma-manifest.json
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/backend-plan-first-finalize-plan/SKILL.md
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/backend-plan-first-finalize-plan/references/planning-rules.md
- examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/backend-plan-first-plan-issue/references/plan-issue-rules.md
- plans/issue-bundle-plugin-install-surface/implement-notes.md
- source/methodology/fragments/seal/entry-gate.md
- source/methodology/resources/shape/references/plan-issue-rules.md
- source/methodology/resources/shared/references/planning-rules.md

## Validation Results
- PASS [task]: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_layer_1_dogfood.py
- PASS [task]: rg -n "## Execution Contract Completeness" source/methodology/resources/shape/references/plan-issue-rules.md
- PASS [task]: rg -n "exact CLI command, API name, function name, skill id, plugin id" source/methodology/resources/shape/references/plan-issue-rules.md
- PASS [task]: rg -n "output paths and output layout" source/methodology/resources/shape/references/plan-issue-rules.md
- PASS [task]: rg -n "target support matrix" source/methodology/resources/shape/references/plan-issue-rules.md
- PASS [task]: rg -n "artifact state" source/methodology/resources/shape/references/plan-issue-rules.md
- PASS [task]: rg -n "negative proof" source/methodology/resources/shape/references/plan-issue-rules.md
- PASS [task]: rg -n "Treat any broad phrase such as" source/methodology/fragments/seal/entry-gate.md
- PASS [task]: rg -n "would need to choose a command name" source/methodology/fragments/seal/entry-gate.md
- PASS [task]: rg -n "plan.md.*preserve the execution contract" source/methodology/resources/shared/references/planning-rules.md
- PASS [task]: rg -n "Validate:.*could pass while the main promised behavior is absent" source/methodology/resources/shared/references/planning-rules.md
- PASS [task]: tmp_dir=$(mktemp -d); uv run --extra dev forma create-bundle --target codex --output "$tmp_dir/bundle"; rg -n "## Execution Contract Completeness" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "exact CLI command, API name" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "output paths and output layout" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "target support matrix" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "artifact state" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "negative proof" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "execution contract" "$tmp_dir/bundle/forma-lock/SKILL.md" "$tmp_dir/bundle/forma-lock/references/planning-rules.md"; rg -n "would need to choose a command name" "$tmp_dir/bundle/forma-lock/SKILL.md"; rm -rf "$tmp_dir"

## Risks / Unresolved Items
- None recorded.
