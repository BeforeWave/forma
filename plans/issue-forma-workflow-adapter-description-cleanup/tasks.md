- [x] [stage-vocabulary-and-lock-policy] Replace legacy stage terminology and unconditional commit policy
Accept: Task Type=step; canonical methodology, bundled references, runner messages, verifier rules, docs, and tests use Forma stage vocabulary and require user-confirmed commit permission for lock-stage plan/task materialization
Validate: if rg -n "finalize-plan|plan-issue|ground-plan|implement-feature" source/methodology source/skill-creator docs tests; then exit 1; fi
Validate: rg -n "user confirmation|explicit user permission|only after explicit" source/methodology source/skill-creator
Depends: none
Constraint: preserve internal stage keys `shape`, `gauge`, `seal`, `pour`, `flow`, and `hone`; rename generated reference filenames only when they are user-visible in generated artifacts.

- [x] [workflow-target-adapters] Introduce workflow output target adapters
Accept: Task Type=step; bundle and plugin generation for Codex, Claude Code, and OpenCode delegates target-specific behavior to a shared adapter contract instead of scattered inline target branches
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py::test_default_profile_and_codex_plugin_metadata tests/test_creator.py::test_forma_self_profile_and_codex_plugin_metadata tests/test_creator.py::test_forma_self_profile_and_claude_code_plugin_localizes_skill_names tests/test_creator.py::test_sample_profile_codex_plugin_uses_bundle_name tests/test_creator.py::test_codex_plugin_rejects_non_kebab_bundle_name tests/test_creator.py::test_workflow_adapter_rejects_opencode_plugin_target tests/test_cli.py::test_create_bundle_default_profile_emits_forma_workflow tests/test_cli.py::test_create_bundle_opencode_emits_native_skill_frontmatter tests/test_cli.py::test_create_plugin_emits_codex_plugin_layout tests/test_cli.py::test_create_plugin_emits_claude_code_plugin_layout
Validate: tmp_dir="$(mktemp -d)"; uv run --extra dev forma create-bundle --target codex --output "$tmp_dir/codex"; uv run --extra dev forma create-bundle --target claude-code --output "$tmp_dir/claude"; uv run --extra dev forma create-bundle --target opencode --output "$tmp_dir/opencode"; uv run --extra dev forma verify "$tmp_dir/codex"; uv run --extra dev forma verify "$tmp_dir/claude"; uv run --extra dev forma verify "$tmp_dir/opencode"; rm -rf "$tmp_dir"
Depends: stage-vocabulary-and-lock-policy
Constraint: keep OpenCode plugin output unsupported with a clear error; do not change public CLI command names or default output layouts except for the accepted stage-vocabulary cleanup.

- [x] [description-generation-quality] Fix trigger descriptions and conditional generated guidance
Accept: Task Type=step; generated `SKILL.md` frontmatter descriptions and Codex `openai.yaml` short descriptions prefer stage `short_description`, long `skills.description` remains body guidance, and conditional reference/validation text is emitted only when relevant
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py::test_sample_conditional_overlay_profile_emits_valid_bundle tests/test_creator.py::test_forma_self_profile_and_codex_plugin_metadata tests/test_creator.py::test_creator_profile_supports_conditional_overlays tests/test_creator_builder.py::test_installed_codex_creator_script_can_emit_plugin_artifact tests/test_creator_builder.py::test_installed_creator_script_supports_conditional_overlays tests/test_verifier.py
Validate: tmp_dir="$(mktemp -d)"; uv run --extra dev forma create-plugin --target codex --profile profiles/forma-self/forma-self-iteration.yaml --output "$tmp_dir/plugin"; rg -n "Converge a Forma development issue" "$tmp_dir/plugin/skills/plan/SKILL.md" "$tmp_dir/plugin/skills/plan/agents/openai.yaml"; uv run --extra dev forma verify "$tmp_dir/plugin"; rm -rf "$tmp_dir"
Depends: workflow-target-adapters
Constraint: mirror the same generation semantics in `source/skill-creator/scripts/create.py`; do not add new profile schema.

- [x] [docs-tests-policy-alignment] Align docs, examples, tests, and release policy with the new contract
Accept: Task Type=step; README, STRUCTURE, AGENTS, dist policy docs, skill-bundle docs, and test fixtures describe the current Forma stage names, adapter target behavior, and no-self-profile-in-dist policy without legacy Engcraft-style names
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py tests/test_creator.py tests/test_runtime_assets.py
Validate: if rg -n "backend-plan-first-plan-issue|ground-plan|finalize-plan|implement-feature" README.md README.zh-CN.md STRUCTURE.md AGENTS.md dist/AGENTS.md docs tests; then exit 1; fi
Depends: description-generation-quality
Constraint: keep public examples generic; do not write local user-home paths into docs, tests, examples, plans, or generated artifacts.

- [x] [implement-notes-process-gate] Prevent process-gate bypasses from being recorded as decisions
Accept: Task Type=gate; `implement-notes.md` guidance and runner review checks prevent workflow, runner, approval, validation, safety, plan-lock, or plan-correction bypasses from being recorded as execution decisions while preserving ordinary execution notes
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_runner.py tests/test_creator.py
Depends: docs-tests-policy-alignment
Constraint: keep the guard targeted to current-task process-gate bypass language; do not turn `implement-notes.md` into a broad prose policy checker.

- [x] [regenerate-and-verify-release-artifacts] Regenerate committed release artifacts from default source
Accept: Task Type=gate; committed creator, bundle, and plugin artifacts under `dist/` are regenerated from default no-profile source, verified for all supported targets, and contain no stale stage vocabulary
Validate: uv run --extra dev forma verify dist/skills/codex/forma-creator
Validate: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
Validate: uv run --extra dev forma verify dist/skills/opencode/forma-creator
Validate: uv run --extra dev forma verify dist/skill-bundles/codex
Validate: uv run --extra dev forma verify dist/skill-bundles/claude-code
Validate: uv run --extra dev forma verify dist/skill-bundles/opencode
Validate: uv run --extra dev forma verify dist/plugins/codex/forma
Validate: uv run --extra dev forma verify dist/plugins/claude-code/forma
Validate: if rg -n "finalize-plan|plan-issue|ground-plan|implement-feature" dist/skills dist/skill-bundles dist/plugins; then exit 1; fi
Depends: implement-notes-process-gate
Constraint: regenerate `dist/skills/*/forma-creator` through `forma build-creator --target <target> --output dist/skills`, `dist/skill-bundles/<target>` through `forma create-bundle --target <target> --output dist/skill-bundles/<target>`, and `dist/plugins/<target>/forma` through `forma create-plugin --target <target> --output dist/plugins/<target>/forma` without a profile.
Constraint: keep all `profiles/forma-self` generation and install smokes in temporary directories only; do not commit self-profile output into `dist/`.
