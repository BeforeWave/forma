- [x] [base-origin-render-contract] Add normalized payload digests, base-origin manifest metadata, and neutral shared rendering
Accept: Task Type=step; generated bundle, Codex plugin, and creator artifacts record stable `base_origin` metadata where applicable, and creator/profile shared fields render with neutral workflow wording that can support exact adoption
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py
Validate: uv run --extra dev forma verify source/skill-creator/
Use-Check: diff-check
Depends: none
Constraint: do not modify README, README.zh-CN, docs/, STRUCTURE.md, AGENTS.md, or similar documentation files
Constraint: normalized payload digests must exclude `.forma-manifest.json` and include runtime payload files such as `SKILL.md`, resources, target metadata, scripts, and Codex plugin metadata

- [x] [exact-profile-adopt] Implement exact-only `forma profile adopt`
Accept: Task Type=step; `forma profile adopt <artifact-path> --output <dir> [--profile-id <id>] [--replace] [--json]` converts same-origin creator-generated bundles and Codex plugins into profile source, copies required resources, writes `adoption-report.json`, regenerates from the candidate profile, and succeeds only when normalized payloads match exactly
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_creator.py tests/test_creator_builder.py
Use-Check: verify-creator-source
Use-Check: diff-check
Depends: base-origin-render-contract
Constraint: fail closed when `base_origin` is missing, base digest mismatches, artifact target is unsupported, or residual diff cannot be represented by profile schema
Constraint: support creator-generated `codex` and `claude-code` skill bundles plus creator-generated Codex plugins; Claude Code plugin adoption is unsupported
Constraint: do not modify README, README.zh-CN, docs/, STRUCTURE.md, AGENTS.md, or similar documentation files

- [x] [drift-cli] Implement `forma drift` for artifacts and release surface
Accept: Task Type=step; `forma drift <artifact-path> [--profile <profile.yaml>] [--creator-source <dir>] [--json]` and `forma drift --release-surface [--json]` verify artifacts, regenerate from the declared source, compare normalized payloads, and report `fresh`, `stale`, `invalid`, or `unknown-source`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py tests/test_creator.py tests/test_creator_builder.py
Validate: uv run --extra dev forma drift --release-surface
Use-Check: diff-check
Depends: base-origin-render-contract
Constraint: `--release-surface` must check only the known Forma `examples/generated/` and `dist/` artifacts listed in plan.md
Constraint: single-artifact drift without `--profile` or `--creator-source` may report base-origin freshness but must not claim full profile drift proof
Constraint: do not modify README, README.zh-CN, docs/, STRUCTURE.md, AGENTS.md, or similar documentation files

- [x] [regenerate-release-surfaces] Regenerate and verify affected committed generated artifacts
Accept: Task Type=gate; every committed `examples/generated/` or `dist/` artifact affected by base-origin, rendering, adopt, or drift behavior is regenerated from source, verified, and passes release-surface drift with no unrelated documentation edits
Validate: uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
Validate: uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
Validate: uv run --extra dev forma verify dist/skills/codex/forma-creator
Validate: uv run --extra dev forma verify dist/skills/claude-code/forma-creator
Validate: uv run --extra dev forma verify dist/skill-bundles/codex
Validate: uv run --extra dev forma verify dist/skill-bundles/claude-code
Validate: uv run --extra dev forma verify dist/plugins/codex/forma
Validate: uv run --extra dev forma drift --release-surface
Use-Check: focused-adopt-drift-tests
Use-Check: verify-creator-source
Use-Check: diff-check
Depends: exact-profile-adopt
Depends: drift-cli
Constraint: generated artifact replacements must include both additions and deletions in the same review when output paths change
Constraint: do not modify README, README.zh-CN, docs/, STRUCTURE.md, AGENTS.md, or similar documentation files
