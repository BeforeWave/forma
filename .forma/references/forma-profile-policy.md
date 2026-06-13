# Forma Profile Policy

Profiles are durable behavior source. Treat them like code.

## Profile Locations

- `.forma/`: project-owned profiles for managing Forma's own development iterations.
- `examples/profiles/`: sanitized examples only. They may demonstrate composition patterns, overlays, and target generation, but must not contain downstream private constraints.
- Downstream repositories: real organization-specific profiles that include true workflow commands, business rules, private repo paths, or product constraints.

## Promotion Rules

- One-off user constraints from the installed creator path stay local to the generated suite unless explicitly promoted to a profile file.
- Promote repeated behavior into a tracked profile only after review.
- Keep conditional behavior in `conditional_overlays` when execution must follow a recorded route instead of re-deciding during implementation.

## Generated Output Policy

- Profile source is primary. A top-level profile does not automatically require committed generated output.
- The `dist/` release surface is product default workflow output generated without an explicit `--profile`; self-profile output must stay in transient paths or local installs unless a future issue explicitly changes the release contract.
- Do not commit generated output for public examples by default; users can generate example output locally when they want to inspect it.
- Commit generated baselines only when they are explicitly part of the issue's review surface or drift guard.
- If committed generated baselines change, regenerate them from committed profiles and include both removed old files and added new files in the same review.
