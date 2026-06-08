# Implement Notes

## Task 1: plugin-emitter-profile-identity

Outcome:
- CLI Codex plugin metadata now derives plugin identity from `bundle.name` and skill entries from the emitted skill manifest.

Decision Notes:
- Options considered for plugin skill descriptions were profile `skills.<stage>.description` versus generated `SKILL.md` frontmatter. Selected generated frontmatter so `plugin.json` describes the actual emitted skill artifact.
- `uv run --extra dev pytest ...` initially executed the global pyenv `pytest` because the local `.venv/bin/pytest` shebang pointed at a literal `~/...` path. Repaired the local validation environment so the planned command validates the checkout source instead of the installed package.

Plan Gaps Found:
- None.

Classifications:
- `uv run forma ...` smoke commands need uv cache access in this sandbox; validation used the same command with escalation when the sandbox denied `~/.cache/uv`.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 5: dist-creator-plugin-refresh

Outcome:
- Rebuilt Codex and Claude Code `forma-creator` dist artifacts, rebuilt the default Codex plugin dist artifact, and proved forma-self plugin output installs into a temporary project with `forma-shape` exposed.

Decision Notes:
- The default Codex plugin dist artifact changed because the updated emitter now writes the default profile `bundle.description` into `plugin.json`, and regenerated manifest provenance reflects the current source revision. Included that dist change because it is generated from the updated emitter.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 4: docs-plugin-naming

Outcome:
- English and Chinese Usage/Targets docs now state that profile-generated Codex plugin ids come from `bundle.name`, creator plugin ids come from `rename.prefix` when present, and plugin skill ids follow emitted renamed skills.

Decision Notes:
- Kept the docs change to `docs/usage*` and `docs/targets*` because the task contract names those surfaces and the README quick-start does not need the full naming matrix.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 3: plugin-verifier-consistency

Outcome:
- `forma verify` now rejects Codex plugin roots whose `plugin.json` skill ids do not match manifest emitted skills and nested `skills/<id>/SKILL.md` entries.

Decision Notes:
- Options considered were checking plugin consistency once per nested skill versus once per plugin root. Selected a bundle-level rule gated to the first discovered skill so one mismatch produces one focused verifier error.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 2: creator-plugin-prefix-identity

Outcome:
- Installed Codex creator plugin output now uses `rename.prefix` as plugin id/name source while preserving default `forma` identity when no prefix is present.

Decision Notes:
- Options considered were deriving plugin id from the first emitted skill name versus using `rename.prefix`. Selected `rename.prefix` because it is the existing creator-side bundle-wide naming control and matches the settled plan.

Plan Gaps Found:
- None.

Classifications:
- None.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 6: codex-plugin-ingestion-contract

Outcome:
- Codex plugin generation now emits the current `plugin-creator` manifest contract, the verifier rejects legacy plugin schema drift, dist artifacts were regenerated, and `forma@personal` installs through Codex's marketplace flow.

Decision Notes:
- Options considered were preserving the previous `plugin.json.skills` skill-list array versus switching to the current Codex contract where `skills` points at `./skills/`. Selected the current contract because `plugin-creator` validation and Codex marketplace ingestion both reject the legacy array shape.
- Options considered for personal marketplace source were a symlink under `~/.agents/plugins/plugins/forma` versus the scaffolded personal marketplace source under `~/plugins/forma`. Selected `~/plugins/forma` because `plugin-creator` defines `./plugins/<plugin-name>` relative to the personal marketplace root as the user plugin source.

Plan Gaps Found:
- The original task contract treated `plugin.json` skill ids as the Codex plugin skill registry. Current Codex ingestion discovers bundled skills through the `skills` path and nested `SKILL.md` files.

Classifications:
- The user-scope install and marketplace mutation were intentionally performed after the user requested global install/debugging, even though the original issue validation only allowed temporary project-scope install smoke.

Deviations From Plan:
- Added `plugin-creator` validation and `codex plugin add forma@personal` evidence because Forma's own verifier was insufficient to prove Codex UI installability.

Follow-ups:
- Task 7 will change the Forma self profile skill names and plugin page copy now that the install path is usable.

## Task 7: forma-self-public-skill-names

Outcome:
- `profiles/forma-self` now emits the default public skill names `forma-plan`, `forma-ground`, `forma-lock`, `forma-execute`, and `forma-showhand`; the installed `forma@personal` plugin exposes those names and uses user-facing workflow copy.

Decision Notes:
- The Codex plugin page already displays the plugin name before each starter prompt, so prompts that started with "Use Forma..." produced visible repetition. Selected short action prompts without the plugin name prefix.
- The previous bundle description described the implementation detail that a profile emits skills. Selected product-facing copy that explains the usable workflow surface: scoped planning through verified execution.

Plan Gaps Found:
- The original issue acceptance expected forma-self to emit `forma-shape` through `forma-flow`; the addendum reversed that requirement after the user tested the plugin page.

Classifications:
- Updating `~/plugins/forma`, reinstalling `forma@personal`, and refreshing the legacy `~/.codex/plugins/forma` copy are user-scope install actions requested by the user to validate the real Codex plugin surface.

Deviations From Plan:
- Regenerated the default Codex plugin dist artifact because the shared starter prompt generator changed.

Follow-ups:
- Restart Codex Desktop or open a new thread for the app UI to pick up the latest installed plugin cache.
