# AGENTS

This directory contains reader-facing Forma documentation. Keep it useful for
people choosing, trying, operating, or extending Forma. Do not turn public docs
into a dump of internal workflow mechanics.

## Documentation Boundaries

| Document | Purpose | Keep Out |
|---|---|---|
| `AGENTS.md` | Editing rules for docs in this directory and the boundary between reader-facing docs and agent-facing guidance. | Product tutorials, command reference, and workflow policy details that belong in narrower docs or `forma explain agent`. |
| `quick-start.md` / `quick-start.zh-CN.md` | The shortest safe first run from project rules to a generated and installed workflow. | Deep command matrices, implementation internals, and agent completion gates. |
| `concepts.md` / `concepts.zh-CN.md` | Public mental model: project rules, profiles, workflow output, task contracts, and target boundaries. | CLI option detail and source-layout minutiae. |
| `usage.md` / `usage.zh-CN.md` | Command reference and routing: which command path to use, required options, and next action. | Agent-only execution policy, script authoring recipes, generated source internals, and per-project local install details. |
| `targets.md` / `targets.zh-CN.md` | Target behavior and install surfaces for Codex, Claude Code, and OpenCode. | Per-profile workflow rules and private marketplace paths. |
| `profile-schema.md` / `profile-schema.zh-CN.md` | Reviewed profile source format and field semantics. | Agent planning behavior and generated artifact walkthroughs beyond schema examples. |
| `skill-bundle.md` / `skill-bundle.zh-CN.md` | Generated skill-bundle shape and what readers can inspect in output. | CLI routing and product positioning. |
| `workflow-contract.md` / `workflow-contract.zh-CN.md` | The task contract model and stage-level execution semantics. | Install commands and profile YAML reference detail. |
| `verifier.md` / `verifier.zh-CN.md` | What verification checks, what it does not prove, and how to read failures. | Broad usage tutorials and unrelated validation policy. |
| `examples.md` / `examples.zh-CN.md` | Sample profiles, local build instructions, and real tracked runs. | Claims that samples are runtime guarantees. |
| `forma-creator.md` / `forma-creator.zh-CN.md` | Optional on-the-spot creator path and its boundary with reviewed profiles. | General command reference already covered by `usage`. |

## Agent-Facing Rules

- `forma explain agent` is the authoritative surface for agent execution
  routing, bootstrap, reuse, and completion rules.
- Keep detailed agent-only requirements there, not in reader-facing docs.
- Reader-facing docs may link to or name `forma explain agent` when an agent
  needs those rules, but should not repeat its full operational policy.
- Profile-local `reinstall-workflow.sh` may be mentioned in `quick-start` and
  `usage` only as an external routing rule: if present beside the profile, run
  it before reconstructing commands.

## Writing Rules

- Prefer public concepts and reader tasks over source-layer names.
- Keep command snippets current and minimal for the page's purpose.
- Avoid non-temporary absolute filesystem paths in tracked docs. Temporary paths
  under `/tmp` or `/private/tmp` are allowed only when they are part of the
  documented behavior.
- Keep English and Chinese versions aligned when editing paired documents.
- If a detail is mainly for maintainers or generated-output authors, put it in
  the narrowest relevant reference doc or in `forma explain agent`, not in the
  general command reference.
