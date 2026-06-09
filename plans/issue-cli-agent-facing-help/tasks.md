- [x] [conditional-decision-plan-template] Include conditional decisions in generated plan templates
Accept: Task Type=step; generated `plan-template.md` files name the exact conditional decision such as `Iteration Area` when a profile defines conditional overlays, no-overlay generated templates remove the placeholder, and affected example baselines plus `dist/` release artifacts are refreshed from source
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_layer_1_dogfood.py tests/test_creator_builder.py
Validate: uv run --extra dev forma verify source/skill-creator/
Validate: uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
Validate: uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
Validate: uv run --extra dev forma verify dist/skills/codex/forma-creator
Validate: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
Validate: uv run --extra dev forma verify dist/skill-bundles/codex
Validate: uv run --extra dev forma verify dist/skill-bundles/claude-code
Validate: uv run --extra dev forma verify dist/plugins/codex/forma
Depends: none
Constraint: specialize the shared plan template during bundle/plugin/creator generation; do not rely on `forma-lock` to infer missing conditional decision fields after a plan is written.

- [ ] [cli-agent-help-surface] Update CLI help and no-argument routing behavior
Accept: Task Type=step; `forma` exits 0 with agent-facing routing guidance, `forma --help` exposes the same routing guidance, command help names the next action for each major command, and old `forma create --help` remains rejected with suggestions for `create-bundle` / `create-plugin`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
Validate: uv run --extra dev forma
Validate: uv run --extra dev forma --help
Validate: ! uv run --extra dev forma create --help
Use-Check: creator-template-tests
Depends: conditional-decision-plan-template
Constraint: change only help/no-args behavior; do not change generation, verification, install, or explain execution semantics.
Constraint: keep help assertions focused on stable agent-routing phrases, not full Click output snapshots.

- [ ] [usage-docs-agent-manual] Align the English and Chinese command references with the new help surface
Accept: Task Type=step; `docs/usage.md` and `docs/usage.zh-CN.md` describe `forma` as a successful discovery entrypoint and document the full agent command routing for creator, bundle, plugin, install, verify, and explain paths
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
Validate: rg -n -e "create-bundle|create-plugin|build-creator|forma install|forma verify|forma explain" docs/usage.md docs/usage.zh-CN.md
Use-Check: cli-help-tests
Depends: cli-agent-help-surface
Constraint: keep Quick Start changes out of scope unless a broken link or direct inconsistency requires a small pointer update.
Constraint: do not edit `dist/`, `examples/generated/`, `source/methodology/`, `source/skill-creator/`, or `profiles/` for this help-only issue.
