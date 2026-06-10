# AGENTS

This directory contains committed Forma release artifacts.

## Release Boundary

- Treat `dist/` as generated output, not source truth.
- The artifacts committed here are default Forma outputs with no tracked profile
  and no temporary injection unless a future issue explicitly changes the release
  contract.
- Do not commit outputs generated from `profiles/forma-self/` into `dist/`.
  Forma self-profile outputs are for local self-iteration checks, installation,
  or temporary verification only.
- When updating `dist/`, regenerate from the intended default release command and
  verify the result with `forma verify <path>`.
- If a generated artifact should come from a tracked profile, commit it under the
  owning example or downstream repository, not this default release surface.

