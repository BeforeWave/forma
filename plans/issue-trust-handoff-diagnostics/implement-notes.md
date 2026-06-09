# Implement Notes

## Task 2: doctor-cli

Outcome:
- Added CLI artifact diagnosis for skills, skill bundles, and Codex plugins with human and JSON output.

Decision Notes:
- `doctor` treats a verified Codex plugin as a successful diagnosis with `forma_install_supported=false`, not as a failed command. The rejected option was using "Forma does not install Codex plugins" as a blocker, which would make the planned plugin smoke fail even though the artifact is valid and has a correct Codex install route.
- Artifact classification was promoted into a reusable install-facing helper instead of copying install detection logic into the CLI doctor command.

Plan Gaps Found:
- None.

Classifications:
- Valid Codex plugin: routed to Codex plugin install, not Forma install.

Deviations From Plan:
- None.

Follow-ups:
- None.

## Task 3: docs-profile-policy

Outcome:
- Updated trust/handoff command guidance in English and Chinese docs, added self-profile rules for CLI-first planning and post-profile plugin reinstall proof, and removed tracked current-developer-home strings from current repository files.

Decision Notes:
- The cleanup scope stayed limited to the current developer home path class. Generic placeholders, `/private/tmp` evidence, and non-local synthetic examples were intentionally left untouched because the user narrowed the sensitivity level before execution.
- Documentation updates were applied to both English and Chinese verifier, usage, and targets pages because the changed CLI surface is user-facing in both doc sets.

Plan Gaps Found:
- None.

Classifications:
- Current-developer-home strings: sensitive local path class requiring cleanup.
- Other absolute path examples: out of scope for this issue.

Deviations From Plan:
- None.

Follow-ups:
- History rewrite for older commits remains outside this issue.

## Task 4: regenerate-install-plugin

Outcome:
- Regenerated the Codex and Claude Code creator release surfaces plus the Forma Codex plugin release surface, then reinstalled `forma@personal` through Codex.

Decision Notes:
- The regenerated plugin source was synchronized into the existing `personal` marketplace source before running Codex remove/add, so Codex reinstalled from the refreshed generated artifact rather than stale marketplace contents.
- The marketplace source path was intentionally not recorded because repository files must not persist local machine paths.

Plan Gaps Found:
- None.

Classifications:
- `dist/skills/codex/forma-creator` and `dist/skills/claude-code/forma-creator`: committed creator release surfaces.
- `dist/plugins/codex/forma`: committed Codex plugin source.
- `forma@personal`: external installed plugin state verified through Codex.

Deviations From Plan:
- None.

Follow-ups:
- None.
