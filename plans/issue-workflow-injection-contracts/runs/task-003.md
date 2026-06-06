# Task Run: source-adapter-injection-boundary

Status: complete

## Scope

- Remove GitHub issue helper behavior from base generated `shape` / `seal` requirements and default copied resources.
- Keep the reusable helper packaged for explicit profile or temporary injection usage.
- Update Layer 1 guidance so source-context adapters are classified as optional injection/profile behavior.
- Regenerate committed and installed outputs that previously inherited the helper unconditionally.

## Evidence

- `uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py` passed with 42 tests.
- `uv run --extra dev forma build-creator --output /tmp/forma-creator-dist --target codex` generated the updated installed creator bundle.
- `uv run --extra dev forma create --target codex --profile profiles/forma-self/forma-self-iteration.yaml --output /tmp/forma-self-iteration-codex` generated the updated self-iteration bundle.
- `uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator` passed.
- `uv run --extra dev forma verify /tmp/forma-self-iteration-codex` passed.
- `uv run --extra dev forma verify ~/.codex/skills/forma-creator` passed.
- `uv run --extra dev forma verify ~/.codex/skills/forma-shape` passed.
- `uv run --extra dev forma verify ~/.codex/skills/forma-seal` passed.
- `find examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code -path '*github_issue_context.py' -print | sort` confirmed the GitHub issue helper is emitted only under `backend-plan-first-plan-issue/scripts/` and `backend-plan-first-finalize-plan/scripts/`.
- `rg -n "github_issue_context|gh issue view|GitHub issue helper" ~/.codex/skills/forma-shape ~/.codex/skills/forma-seal` returned no matches.
- `rg -n "source adapter|Source Context Adapters|github_issue_context|gh issue view|script-resource-adapter" ~/.codex/skills/forma-creator/SKILL.md ~/.codex/skills/forma-creator/references ~/.codex/skills/forma-creator/resources/plan-first/methodology/resources/shared` confirmed the installed creator retained explicit adapter guidance/resources before the generic reference rename.
- `forma explain temporary-injection --format json --target codex` includes the canonical `Script Resource Injection Template` with `resources.<stage>.scripts`.
- `uv run --extra dev forma create --target codex --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml --output /tmp/sample-backend-go-github-issue-tracked-gh-profile-check` generated the renamed GitHub issue tracked sample suite with `scripts/github_issue_context.py` only under `backend-plan-first-plan-issue` and `backend-plan-first-finalize-plan`.
- `rg -n "github_issue_context|gh issue view|script-resource-adapter" /tmp/sample-backend-go-github-issue-tracked-gh-profile-check/backend-plan-first-implement-feature /tmp/sample-backend-go-github-issue-tracked-gh-profile-check/backend-plan-first-showhand` returned no matches, confirming execution stages do not inherit the adapter.
- `uv run --extra dev pytest -p no:cacheprovider tests/` passed with 67 tests after the sample rename.
- `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/` passed.
- `uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/` passed.
- `uv run --extra dev forma create --target codex --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml --output /tmp/sample-backend-go-github-issue-tracked-rename-check-codex` passed.
- `uv run --extra dev forma create --target claude-code --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml --output /tmp/sample-backend-go-github-issue-tracked-rename-check-claude-code` passed.
- `uv run --extra dev forma verify /tmp/sample-backend-go-github-issue-tracked-rename-check-codex` passed.
- `uv run --extra dev forma verify /tmp/sample-backend-go-github-issue-tracked-rename-check-claude-code` passed.
- `uv run --extra dev pytest -p no:cacheprovider tests/` passed with 67 tests after replacing the GitHub-specific adapter reference with generic `script-resource-adapter.md`.
- `uv run --extra dev forma build-creator --output /tmp/forma-creator-dist --target codex` generated an updated creator bundle whose guidance says source-context helper scripts are optional adapters.
- `uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator/` passed.
- `uv run --extra dev forma verify source/skill-creator/` passed.
- `uv run --extra dev forma explain temporary-injection --format json --target codex` includes the generic `resources.<stage>.scripts` template and no old GitHub-specific adapter reference.
- `python3 /tmp/forma-creator-dist/codex/forma-creator/scripts/create.py --output /tmp/forma-creator-script-resource-injection-check --injection-json /tmp/forma-creator-script-resource-injection.json` passed and auto-verified the generated suite.
- `python3 /tmp/forma-creator-dist/codex/forma-creator/scripts/verify.py /tmp/forma-creator-script-resource-injection-check` passed.
- `find /tmp/forma-creator-script-resource-injection-check ... | sort` showed only `script-resource-adapter.md` plus `github_issue_context.py` under `forma-shape` and `forma-seal`.
- Negative `rg` checks confirmed `forma-pour` / `forma-flow` do not contain the generic script reference, the GitHub helper, or GitHub CLI invocation.
- Negative `rg` checks confirmed the old GitHub-specific adapter filename and title no longer appear in active source, tests, examples, docs, or current issue artifacts.
- `git diff --check` passed.
