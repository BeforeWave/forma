- [x] [plugin-emitter-profile-identity] Fix CLI Codex plugin metadata from profile bundle and emitted skills
Accept: Task Type=step; profile-based `create-plugin` writes plugin id from `bundle.name`, plugin skill ids from emitted skills, and descriptions from generated `SKILL.md` frontmatter while preserving default profile output
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_cli.py
Validate: tmp_dir="$(mktemp -d)"; uv run --extra dev forma create-plugin --target codex --profile profiles/forma-self/forma-self-iteration.yaml --output "$tmp_dir/plugin"; test -d "$tmp_dir/plugin/skills/forma-shape"; python3 -m json.tool "$tmp_dir/plugin/.codex-plugin/plugin.json" >/dev/null; rg -n '"id": "forma-shape"' "$tmp_dir/plugin/.codex-plugin/plugin.json"; rm -rf "$tmp_dir"
Depends: none
Constraint: do not add a `plugin` profile schema or infer plugin identity from stage names.

- [ ] [creator-plugin-prefix-identity] Align installed creator plugin identity with rename prefix
Accept: Task Type=step; Codex-targeted installed creator plugin output uses `rename.prefix` as plugin id/name source when provided and keeps default `forma` identity otherwise
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_creator_builder.py
Validate: uv run --extra dev forma verify source/skill-creator/
Depends: plugin-emitter-profile-identity
Constraint: keep `source/skill-creator/scripts/forma_verifier/` stdlib-only and do not add creator-side install behavior.

- [ ] [plugin-verifier-consistency] Add plugin.json consistency verification
Accept: Task Type=step; verifier rejects Codex plugin roots where `plugin.json` skills do not match nested skill directories and manifest emitted skills
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_verifier.py tests/test_creator.py tests/test_creator_builder.py
Depends: plugin-emitter-profile-identity
Constraint: verifier rule must be deterministic and stdlib-only.

- [ ] [docs-plugin-naming] Document plugin identity and renamed skill propagation
Accept: Task Type=step; English and Chinese Usage/Targets docs state that profile-based Codex plugin ids come from `bundle.name`, installs land under `.codex/plugins/<bundle.name>`, and plugin skills follow emitted renamed skills
Validate: uv run --extra dev pytest -p no:cacheprovider tests/test_docs_links.py
Validate: rg -n -e "bundle.name|plugin id|\\.codex/plugins/<" docs/usage.md docs/targets.md docs/usage.zh-CN.md docs/targets.zh-CN.md
Depends: plugin-emitter-profile-identity
Constraint: do not imply Claude Code plugin support or URL install support.

- [ ] [dist-creator-plugin-refresh] Regenerate affected release artifacts and prove install smoke
Accept: Task Type=step; regenerated creator dist artifacts include the plugin identity fix, default Codex plugin release remains verified, and temporary project install smoke proves forma-self plugin output is usable
Validate: uv run --extra dev forma verify dist/skills/codex/forma-creator
Validate: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
Validate: uv run --extra dev forma verify dist/plugins/codex/forma
Validate: repo="$PWD"; tmp_dir="$(mktemp -d)"; uv run --extra dev forma create-plugin --target codex --profile profiles/forma-self/forma-self-iteration.yaml --output "$tmp_dir/plugin"; mkdir -p "$tmp_dir/project"; (cd "$tmp_dir/project" && uv --project "$repo" run --extra dev forma install --target codex --scope project "$tmp_dir/plugin" && test -d .codex/plugins/forma/skills/forma-shape && rg -n '"id": "forma-shape"' .codex/plugins/forma/.codex-plugin/plugin.json); rm -rf "$tmp_dir"
Depends: creator-plugin-prefix-identity
Depends: plugin-verifier-consistency
Depends: docs-plugin-naming
Constraint: do not install into user scope; update `dist/plugins/codex/forma` only if default plugin output changes.
