- [x] [bundle-terminology-contract] Rename suite/create contracts to bundle contracts across Layer 3, Layer 1, Layer 2, manifests, and tests
Accept: Task Type=step; public API names, manifest fields, verifier reports, test fixtures, and source creator output use bundle terminology with no old suite compatibility path
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_verifier.py tests/test_layer_1_dogfood.py
Validate: uv run --extra dev forma verify source/skill-creator/
Depends: none
Constraint: remove `forma create` and old suite names instead of keeping aliases or fallback manifest parsing.

- [ ] [cli-create-plugin-install] Implement `create-bundle`, Codex-only `create-plugin`, and local `install` CLI behavior
Accept: Task Type=step; `create-bundle` requires an explicit output path, `create-plugin --target codex` emits exactly one plugin layout, unsupported plugin targets fail clearly, `install` verifies local paths before writing with `--replace` overwrite protection, and CLI regressions are covered in new or updated tests including `tests/test_cli.py`
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_cli.py
Validate: tmp_dir=$(mktemp -d); uv run --extra dev forma create-plugin --target codex --output "$tmp_dir/plugin"; test -f "$tmp_dir/plugin/.codex-plugin/plugin.json"; test -d "$tmp_dir/plugin/skills/forma-plan"; test ! -d "$tmp_dir/plugin/skill-bundles"; rm -rf "$tmp_dir"
Validate: repo=$PWD; tmp_dir=$(mktemp -d); uv run --extra dev forma create-bundle --target codex --output "$tmp_dir/bundle"; mkdir -p "$tmp_dir/project"; (cd "$tmp_dir/project" && uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/bundle" && test -d .codex/skills/forma-plan && test -d .codex/skills/forma-showhand && ! uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/bundle" && uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/bundle" --replace); rm -rf "$tmp_dir"
Validate: repo=$PWD; tmp_dir=$(mktemp -d); uv run --extra dev forma create-bundle --target claude-code --output "$tmp_dir/bundle"; mkdir -p "$tmp_dir/project"; (cd "$tmp_dir/project" && uv --project "$repo" run --extra dev forma install --target claude-code --scope project "$tmp_dir/bundle" && test -d .claude/skills/forma-plan && test -d .claude/skills/forma-showhand); rm -rf "$tmp_dir"
Validate: repo=$PWD; tmp_dir=$(mktemp -d); uv run --extra dev forma create-plugin --target codex --output "$tmp_dir/plugin"; mkdir -p "$tmp_dir/project"; (cd "$tmp_dir/project" && uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/plugin" && test -f .codex/plugins/forma/.codex-plugin/plugin.json && test -d .codex/plugins/forma/skills/forma-plan); rm -rf "$tmp_dir"
Depends: bundle-terminology-contract
Constraint: do not add URL download behavior to `install`; do not make `create-plugin` write `dist/skill-bundles/{codex,claude-code}`.

- [ ] [default-workflow-profile] Add the generic no-injection workflow profile and Codex plugin metadata
Accept: Task Type=step; the default profile emits `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand` with the settled descriptions, and the Codex plugin metadata is id `forma`, name `Forma`, and plan-first positioned
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py
Validate: tmp_dir=$(mktemp -d); uv run --extra dev forma create-bundle --target codex --output "$tmp_dir/bundle"; test -d "$tmp_dir/bundle/forma-plan"; test -d "$tmp_dir/bundle/forma-showhand"; uv run --extra dev forma verify "$tmp_dir/bundle"; rm -rf "$tmp_dir"
Depends: cli-create-plugin-install
Constraint: put product-owned default profile source at `profiles/default/forma-plan-first.yaml`, not `examples/profiles/`; keep downstream-specific constraints out of the profile.

- [ ] [plan-lock-sharpness-contract] Encode sharp planning gates into the default `forma-plan` and `forma-lock` workflow
Accept: Task Type=step; `source/methodology/resources/shape/references/plan-issue-rules.md` adds `## Execution Contract Completeness`, `source/methodology/fragments/seal/entry-gate.md` adds concrete fail-closed handoff rules, `source/methodology/resources/shared/references/planning-rules.md` adds execution-ready task validation rules, and generated `forma-plan` / `forma-lock` surfaces preserve those rules
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_layer_1_dogfood.py
Validate: rg -n "## Execution Contract Completeness" source/methodology/resources/shape/references/plan-issue-rules.md
Validate: rg -n "exact CLI command, API name, function name, skill id, plugin id" source/methodology/resources/shape/references/plan-issue-rules.md
Validate: rg -n "output paths and output layout" source/methodology/resources/shape/references/plan-issue-rules.md
Validate: rg -n "target support matrix" source/methodology/resources/shape/references/plan-issue-rules.md
Validate: rg -n "artifact state" source/methodology/resources/shape/references/plan-issue-rules.md
Validate: rg -n "negative proof" source/methodology/resources/shape/references/plan-issue-rules.md
Validate: rg -n "Treat any broad phrase such as" source/methodology/fragments/seal/entry-gate.md
Validate: rg -n "would need to choose a command name" source/methodology/fragments/seal/entry-gate.md
Validate: rg -n "plan.md.*preserve the execution contract" source/methodology/resources/shared/references/planning-rules.md
Validate: rg -n "Validate:.*could pass while the main promised behavior is absent" source/methodology/resources/shared/references/planning-rules.md
Validate: tmp_dir=$(mktemp -d); uv run --extra dev forma create-bundle --target codex --output "$tmp_dir/bundle"; rg -n "## Execution Contract Completeness" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "exact CLI command, API name" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "output paths and output layout" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "target support matrix" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "artifact state" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "negative proof" "$tmp_dir/bundle/forma-plan/references/plan-issue-rules.md"; rg -n "execution contract" "$tmp_dir/bundle/forma-lock/SKILL.md" "$tmp_dir/bundle/forma-lock/references/planning-rules.md"; rg -n "would need to choose a command name" "$tmp_dir/bundle/forma-lock/SKILL.md"; rm -rf "$tmp_dir"
Depends: default-workflow-profile
Constraint: keep the guidance concrete and gate-oriented; do not add generic planning philosophy or marketing copy.

- [ ] [creator-target-contracts] Update generated `forma-creator` behavior for bundle and plugin generation boundaries
Accept: Task Type=step; Codex-targeted creator can generate and verify workflow bundles and Codex plugins, Claude Code-targeted creator only presents workflow-bundle generation, and neither creator installs generated artifacts
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_layer_1_dogfood.py tests/test_creator_builder.py
Validate: uv run --extra dev forma verify source/skill-creator/
Depends: plan-lock-sharpness-contract
Constraint: creator output must report install instructions or paths only; do not add creator-side install actions.

- [ ] [dist-release-surface] Make `dist/` committable and generate the settled release artifacts
Accept: Task Type=step; `.gitignore` no longer ignores top-level `dist/`, and committed release outputs exist at `dist/skills/codex/forma-creator`, `dist/skills/claude-code/forma-creator`, `dist/skill-bundles/codex/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`, `dist/skill-bundles/claude-code/{forma-plan,forma-ground,forma-lock,forma-execute,forma-showhand}`, and `dist/plugins/codex/forma`
Validate: uv run --extra dev forma verify dist/skills/codex/forma-creator
Validate: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
Validate: uv run --extra dev forma verify dist/skill-bundles/codex
Validate: uv run --extra dev forma verify dist/skill-bundles/claude-code
Validate: uv run --extra dev forma verify dist/plugins/codex/forma
Depends: creator-target-contracts
Constraint: generate `dist/skill-bundles/{codex,claude-code}/*` through explicit `create-bundle --output dist/skill-bundles/<target>`, not as a side effect of `create-plugin`.

- [ ] [docs-agent-discovery] Update README, docs, AGENTS.md, CLAUDE.md, and discovery copy for the new release surface
Accept: Task Type=step; docs include quick-try agent wording for Codex plugin, skill bundle, and creator skill artifacts; usage docs cover `create-bundle`, `create-plugin`, `install`, `build-creator`, and `verify`; AGENTS.md is target-neutral and CLAUDE.md points Claude Code users back to it
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_docs_links.py
Validate: rg -n -e "create-bundle|create-plugin|forma install|forma-plan|forma-showhand|Codex plugin|Claude Code" README.md README.zh-CN.md docs AGENTS.md CLAUDE.md pyproject.toml source/skill-creator/interfaces/codex/openai.yaml
Depends: dist-release-surface
Constraint: keep homepage copy concise and product-facing; do not leave suite terminology in public docs except when explicitly discussing removed legacy names.
