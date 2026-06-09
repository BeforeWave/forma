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
