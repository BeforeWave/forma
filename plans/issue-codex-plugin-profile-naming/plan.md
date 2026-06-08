# Issue Plan

## Goal

- Fix Codex plugin generation and install semantics so profile-renamed workflows produce usable Codex plugins: plugin ids come from the profile bundle name, and plugin skill ids match the actual emitted skills.

## Plan Strategy

- Plan Strategy: step-execution

## Iteration Area

- cross-layer

## Scope

- In scope:
  - `src/forma/plugins.py` CLI `create-plugin` output for profile-owned Codex plugins.
  - `source/skill-creator/scripts/create.py` Codex plugin output identity from installed `forma-creator` bundles.
  - `source/skill-creator/scripts/forma_verifier/rules.py` verifier behavior for `plugin.json` to nested-skill consistency.
  - Tests for default profile output, `profiles/forma-self`, sample backend renamed profiles, creator `rename.prefix`, temporary project install placement, and negative verifier mismatch.
  - English and Chinese usage/target docs for plugin id and renamed-skill propagation semantics.
  - Regenerated creator dist artifacts affected by `source/skill-creator/scripts/create.py`; regenerate the default Codex plugin dist artifact only if the updated emitter changes its tracked output.
- Out of scope:
  - Adding a new `plugin.id` or `plugin.name` profile schema.
  - Inferring plugin identity from stage skill names.
  - Claude Code plugin output.
  - User-scope installation or mutation of the real user Codex root during tests.
  - Changing internal stage keys `shape`, `gauge`, `seal`, `pour`, and `flow`.

## Approach

- Use `bundle.name` as the Codex plugin id source for profile-based CLI plugin generation; require a valid lower-kebab value and derive display name from the same value.
- Build the nested workflow bundle first, then copy its `.forma-manifest.json` to the plugin root and derive `.codex-plugin/plugin.json` skills from manifest `emitted_skills`, not from hard-coded default skill ids.
- Read generated `SKILL.md` frontmatter descriptions for plugin skill metadata so renamed profiles keep useful plugin descriptions.
- Preserve default profile behavior: `bundle.name: forma`, plugin id `forma`, and skills `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand`.
- In `source/skill-creator/scripts/create.py`, use `rename.prefix` as the Codex plugin id/name source when present; otherwise keep the default `forma` identity. Keep plugin skill ids based on the generated `skill_names`.
- Add a verifier rule that fails Codex plugin roots when `plugin.json` skill ids do not match nested `skills/<id>/SKILL.md` directories and the bundle manifest's emitted skills.
- Update docs for the public command/install contract, then regenerate and verify release artifacts affected by the source changes.

## Artifact/Evidence Boundary

- Source-of-truth refs: the current user request and the current conversation decisions take precedence; the `forma-gauge` grounding handoff provides repository facts and confirms the reproduced self-profile plugin mismatch.
- Source edit paths: `src/forma/plugins.py`, `source/skill-creator/scripts/create.py`, `source/skill-creator/scripts/forma_verifier/rules.py`, focused tests under `tests/`, and English/Chinese docs under `docs/`.
- Committed generated artifact paths: `dist/skills/codex/forma-creator` and `dist/skills/claude-code/forma-creator`; `dist/plugins/codex/forma` only if regeneration from the new emitter changes tracked output.
- Transient artifact paths: plugin generation and temporary project install smoke outputs under `mktemp -d` or `/private/tmp`.
- Evidence paths: execution proof is recorded under `plans/issue-codex-plugin-profile-naming/runs/`.
- State policy: tests must use temporary project-scope install directories only; do not install into user scope or modify the real `$HOME/.codex/plugins` tree.
- Validation gates: each behavior change needs focused tests or direct create/verify/install smoke proof; final validation must cover full tests, source creator verification, relevant dist verification, and whitespace checks.
- Metadata/provenance: `plugin.json` `id`, `name`, and `skills` must match the profile bundle name and emitted skill manifest; regenerated dist creator manifests must reflect the current generator output.

## Constraints

- Keep Layer 1, Layer 2, Layer 3, docs, and generated artifact boundaries explicit.
- Do not add plugin-specific profile schema in this issue.
- Keep `source/skill-creator/scripts/forma_verifier/` stdlib-only.
- Do not make `install` fetch URLs or install into user scope.
- Preserve default plugin id `forma` for the default profile.

## Acceptance Criteria

- `forma create-plugin --target codex --profile profiles/forma-self/forma-self-iteration.yaml` emits plugin id `forma`, nested skills `forma-shape` through `forma-flow`, and `plugin.json` skills with the same ids.
- Installing that output into a temporary project writes `.codex/plugins/forma` with matching `plugin.json` and nested skills.
- `forma create-plugin --target codex --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml` emits plugin id `sample-backend-go-github-issue-tracked` and installs to `.codex/plugins/sample-backend-go-github-issue-tracked`.
- Installed creator plugin output with `rename.prefix: acme-plan-first` emits plugin id `acme-plan-first` and skill ids `acme-plan-first-plan` through `acme-plan-first-showhand`.
- `forma verify` fails a Codex plugin artifact whose `plugin.json` skill ids do not match actual nested skills.
- Docs describe `bundle.name`-derived plugin ids and renamed skill propagation in English and Chinese.

## Validation

Check: plugin-tests
Command: uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py tests/test_cli.py tests/test_verifier.py
Note: covers plugin metadata, creator plugin identity, install path, and verifier mismatch behavior.

Check: docs-links
Command: uv run --extra dev pytest -p no:cacheprovider tests/test_docs_links.py
Note: use after edited docs links or cross-doc references.

Check: source-creator-verify
Command: uv run --extra dev forma verify source/skill-creator/
Note: required after Layer 1 creator or Layer 2 verifier script changes.

## Final Validation

```sh
uv run --extra dev pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify dist/skills/codex/forma-creator
uv run --extra dev forma verify dist/skills/claude-code/forma-creator
uv run --extra dev forma verify dist/plugins/codex/forma
git diff --check
```

## Risks / Notes

- The current verifier passes the broken generated plugin, so the negative verifier test is required before future plugin artifacts can be trusted.
- Invalid non-kebab `bundle.name` values should fail clearly when building a Codex plugin because `bundle.name` is now plugin identity.

## Addendum: Codex Plugin Ingestion And Public Self Profile Names

The live Codex plugin page proved the original `plugin.json` shape was still not
the current Codex ingestion contract. The follow-up scope adds two tasks:

- Align generated Codex plugin manifests and personal marketplace registration
  with the current `plugin-creator` contract: plugin `name` is the kebab-case
  identifier, `skills` points to `./skills/`, and installability is proven
  through `codex plugin add forma@personal`.
- Change `profiles/forma-self` back to the default public skill names
  `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and
  `forma-showhand`, and make the Codex plugin page copy describe the workflow
  rather than the implementation detail that a profile emits skills.

Additional acceptance:

- `plugin-creator` validation passes for generated, dist, source, and installed
  Forma Codex plugin artifacts.
- `codex plugin list` shows `forma@personal` as installed and enabled.
- `profiles/forma-self/forma-self-iteration.yaml` emits the default public
  skill names while preserving Forma-owned self-iteration constraints.
- The plugin page description and starter prompts are concise user-facing
  workflow copy.

Follow-up install boundary:

- `forma install` must stop accepting Codex plugin artifacts. Generated plugin
  output should direct users to install through Codex's plugin system:
  `codex plugin add <plugin>@<marketplace>` or the Codex plugin UI.
