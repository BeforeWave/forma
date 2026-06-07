# Task Evidence

- Task: [cli-create-plugin-install] Implement `create-bundle`, Codex-only `create-plugin`, and local `install` CLI behavior
- Completed At (UTC): 2026-06-07T13:30:42Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- MANIFEST.in
- plans/issue-bundle-plugin-install-surface/implement-notes.md
- profiles/default/forma-plan-first.yaml
- setup.py
- src/forma/cli.py
- src/forma/install.py
- src/forma/plugins.py
- tests/test_cli.py
- tests/test_creator.py

## Validation Results
- PASS [task]: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_cli.py
- PASS [task]: tmp_dir=$(mktemp -d); uv run --extra dev forma create-plugin --target codex --output "$tmp_dir/plugin"; test -f "$tmp_dir/plugin/.codex-plugin/plugin.json"; test -d "$tmp_dir/plugin/skills/forma-plan"; test ! -d "$tmp_dir/plugin/skill-bundles"; rm -rf "$tmp_dir"
- PASS [task]: repo=$PWD; tmp_dir=$(mktemp -d); uv run --extra dev forma create-bundle --target codex --output "$tmp_dir/bundle"; mkdir -p "$tmp_dir/project"; (cd "$tmp_dir/project" && uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/bundle" && test -d .codex/skills/forma-plan && test -d .codex/skills/forma-showhand && ! uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/bundle" && uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/bundle" --replace); rm -rf "$tmp_dir"
- PASS [task]: repo=$PWD; tmp_dir=$(mktemp -d); uv run --extra dev forma create-bundle --target claude-code --output "$tmp_dir/bundle"; mkdir -p "$tmp_dir/project"; (cd "$tmp_dir/project" && uv --project "$repo" run --extra dev forma install --target claude-code --scope project "$tmp_dir/bundle" && test -d .claude/skills/forma-plan && test -d .claude/skills/forma-showhand); rm -rf "$tmp_dir"
- PASS [task]: repo=$PWD; tmp_dir=$(mktemp -d); uv run --extra dev forma create-plugin --target codex --output "$tmp_dir/plugin"; mkdir -p "$tmp_dir/project"; (cd "$tmp_dir/project" && uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/plugin" && test -f .codex/plugins/forma/.codex-plugin/plugin.json && test -d .codex/plugins/forma/skills/forma-plan); rm -rf "$tmp_dir"

## Risks / Unresolved Items
- None recorded.
