- [x] [verifier-json] Add shared verifier JSON output and semantic failure classes
Accept: Task Type=step; the shared Layer 2 verifier emits stable JSON with semantic failure classes through both `forma verify --json <path>` and bundled `scripts/verify.py --json <path>`, while default human output and exit-code behavior remain compatible
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_cli.py tests/test_layer_1_dogfood.py
Validate: tmp_dir="$(mktemp -d)"; uv run --extra dev forma create-bundle --target codex --output "$tmp_dir/bundle"; uv run --extra dev forma verify --json "$tmp_dir/bundle"; python3 source/skill-creator/scripts/verify.py --json "$tmp_dir/bundle"; exit_status=$?; rm -rf "$tmp_dir"; exit "$exit_status"
Use-Check: verifier-focused
Constraint: keep `source/skill-creator/scripts/forma_verifier/` stdlib-only and do not make human verifier output depend on JSON serialization.

- [ ] [doctor-cli] Add CLI-only artifact diagnosis
Accept: Task Type=step; `forma doctor [--json] <path>` identifies artifact kind, target, verification status, Forma installability, correct install route, blockers, and next steps for skills, skill bundles, and Codex plugins
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_verifier.py
Validate: tmp_dir="$(mktemp -d)"; uv run --extra dev forma create-plugin --target codex --output "$tmp_dir/plugin"; uv run --extra dev forma doctor "$tmp_dir/plugin"; uv run --extra dev forma doctor --json "$tmp_dir/plugin"; exit_status=$?; rm -rf "$tmp_dir"; exit "$exit_status"
Use-Check: cli-focused
Depends: verifier-json
Constraint: keep `forma doctor` out of generated workflow skills and do not imply that `forma install` can install Codex plugin artifacts.

- [ ] [docs-profile-policy] Update public guidance, self-profile policy, and local user-path cleanup
Accept: Task Type=step; docs describe the new trust/handoff commands, `profiles/forma-self/` records CLI-first development, creator-visible sync, current-developer-home path exclusion, and post-profile-change plugin regeneration plus Codex installation, and current tracked current-developer-home strings are removed
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py tests/test_creator.py
Validate: ! rg -ni --fixed-strings "$HOME" . --glob '!.git'
Use-Check: local-user-path-policy
Depends: doctor-cli
Constraint: do not broaden cleanup to unrelated `/private/tmp`, `/absolute/path/to/...`, or synthetic non-local examples.

- [ ] [regenerate-install-plugin] Regenerate release surfaces and install the refreshed Codex plugin
Accept: Task Type=promote; regenerated creator and Codex plugin artifacts reflect the source/profile changes, verify successfully, and the refreshed plugin is installed through Codex so `forma@personal` is visible to new Codex work
Validate: uv run --extra dev forma verify dist/skills/codex/forma-creator
Validate: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
Validate: uv run --extra dev forma verify dist/plugins/codex/forma
Validate: codex plugin list | rg 'forma@personal'
Depends: docs-profile-policy
Constraint: regenerate from source/profile inputs only; do not hand-edit generated `dist` output or write local marketplace paths into repository files.
