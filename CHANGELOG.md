# Changelog

This file is the source of truth for Forma release notes. GitHub Releases,
PyPI, npm, Homebrew, and downstream announcements should derive their release
notes from the matching version section here. Channel-specific notes may be
shortened, but should not introduce release claims that are not represented in
this file.

## 0.1.2 - 2026-06-12

### Added

- Added the canonical PyPI publishing path for `forma-cli`, with
  `beforewave-forma` kept as a compatibility distribution name.
- Added the npm launcher package `@beforewave/forma` as a discovery and entry
  package for npm users.
- Added native OpenCode direct-skill output alongside the existing Codex and
  Claude Code targets.
- Added agent-facing CLI routing and diagnostics, including clearer root help,
  `forma doctor`, verifier JSON output, and release-surface drift checks.
- Added `plugin.display_name` for profile and creator-generated Codex plugin
  outputs so install-surface display labels can differ from plugin ids without
  changing skill names or triggers.
- Added release packaging and validation scripts for PyPI and npm packages.

### Changed

- Updated public documentation to recommend `pipx install forma-cli` as the
  primary CLI install path.
- Clarified plugin versus direct skill behavior: plugin output exposes
  plugin-local stage names and qualified triggers such as `forma:plan`, while
  direct skill bundles use standalone `forma-*` skill names.
- Kept committed `dist/` artifacts as default no-profile release output;
  self-profile generated output stays out of the generic release surface.
- Tightened generated workflow language around planning boundaries, staged
  snapshots, execution proof, and release/install responsibilities.
- Updated Codex plugin install guidance to list configured marketplaces, ask the
  user to choose or approve a marketplace, and install with an explicit
  `<plugin-id>@<marketplace-name>` selector.
- Clarified that postprocessing profile-generated artifacts must happen after
  drift checks, and that postprocessed artifacts should use `forma verify` as
  the final gate.

### Fixed

- Fixed workflow validation execution so it does not read Bash startup files
  while still inheriting the process environment needed by real validation.
- Fixed generated workflow and plugin naming so Codex plugin triggers,
  standalone skill names, and generated metadata stay aligned.
- Fixed artifact freshness and base-origin handling so generated examples and
  release surfaces can be checked for drift more reliably.
- Fixed profile adoption behavior so regenerated artifacts preserve the
  intended baseline.

### Notes

- This release is a packaging, target-support, install-surface, and workflow
  semantics release.

## 0.1.1 - 2026-06-09

### Added

- Added the committed release surface for default Codex and Claude Code
  workflow bundles and Codex plugin output.
- Added `forma create-bundle`, `forma create-plugin`, and local install
  behavior for generated workflow artifacts.
- Added plugin metadata consistency checks and clearer target-specific
  generation boundaries.
- Added the profile draft workflow for extracting project rules into a reviewed
  profile before generating workflow output.

### Changed

- Reworked the public README and docs around Forma's workflow-generation model
  and task-contract lifecycle.
- Clarified that Codex plugin artifacts are installed through Codex
  marketplace/plugin flows, not through `forma install`.
- Refined CLI help and no-argument behavior so agents can choose the intended
  command path without trial and error.
- Refreshed the Forma self-profile plugin artifact used by this repository.

### Fixed

- Fixed plugin install guidance and handoff wording for generated Codex plugin
  artifacts.
- Fixed conditional plan-template task handling in the workflow output.
- Fixed validation wording so final validation lines do not depend on stateful
  shell assumptions.

## 0.1.0 - 2026-06-07

### Added

- Initial public pre-release of Forma.
- Added the project-rule to workflow-output model: profile source, generated
  workflow bundle/plugin output, and task contract records under
  `plans/issue-<id>/`.
- Added the default plan-before-execute workflow shape: `plan`, `ground`,
  `lock`, `execute`, and `showhand`.
- Added the verifier, sample profiles, generated sample baselines, and public
  documentation entrypoints.

### Changed

- Adopted Apache-2.0 licensing and public-facing project metadata.
- Organized the README and docs around Forma's value, fit, quick start, target
  behavior, verifier behavior, and examples.

### Notes

- The `0.1.0` release established the public project shape and was intentionally
  early-stage.
