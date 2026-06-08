# Targets

Chinese version: [targets.zh-CN.md](./targets.zh-CN.md)

Forma emits target-specific workflow bundles. A Codex plugin is a Codex install
shape for the same task-level skills.

The workflow source can be the same, but the emitted bundle must match the
target that will load it.

## Supported Targets

| Output | CLI target | Personal install | Project install |
|---|---|---|---|
| Codex skills | `codex` | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | `codex` | `$HOME/.codex/plugins` | `.codex/plugins` |
| Claude Code skills | `claude-code` | `$HOME/.claude/skills` | `.claude/skills` |

Use the matching `--target` value:

```bash
forma create-bundle --target codex --profile <profile.yaml> --output <dir>
forma create-bundle --target claude-code --profile <profile.yaml> --output <dir>
forma create-plugin --target codex --profile <profile.yaml> --output <dir>
```

## Codex

Codex reads skills from repository, user, admin, and bundled system locations.

For project skills, Forma installs into `.codex/skills`. User skills install
under `$HOME/.codex/skills`.

For project plugins, Forma installs into `.codex/plugins/<plugin-id>`. User
plugins install under `$HOME/.codex/plugins/<plugin-id>`. The installed plugin
root keeps `.codex-plugin/plugin.json`.

Codex target bundles may include `agents/openai.yaml` for UI metadata,
invocation policy, and tool dependency declarations.

See the official Codex Agent Skills docs:
<https://developers.openai.com/codex/skills>.

## Claude Code

Claude Code personal skills live under `$HOME/.claude/skills`. Project skills
live under `.claude/skills`.

Claude Code also discovers project skills from parent directories and nested
`.claude/skills` directories while working in a repository. Project skills may
require workspace trust before tool permissions apply.

Claude Code plugin output is not supported by Forma in this release. Use a
Claude Code skill bundle instead.

See the official Claude Code skills docs:
<https://code.claude.com/docs/en/skills>.

## Target-Specific Output

Target adapters affect emitted metadata and install behavior. They should not
change the task-level workflow contract itself.

For example:

- Codex output may include `agents/openai.yaml`.
- Claude Code output should not contain Codex-only metadata.
- Codex plugin output includes `.codex-plugin/plugin.json`, root
  `.forma-manifest.json`, and nested `skills/`.
- Skill directory names and frontmatter must match the target-readable bundle
  contract.

## Distribution Boundary

Direct skill directories are good for local authoring and project-scoped
workflows.

If a workflow should be distributed more broadly, package or distribution
mechanisms may become target-specific. Keep Forma profiles as the workflow
source, and generate the target output needed for the destination.

## Review Before Trust

Generated bundles can include scripts. Review project bundles before
trusting them, especially when a target allows tool permissions or dynamic
context injection.

## Related Docs

- [Quick Start](./quick-start.md): first-run install commands.
- [Skill Bundle](./skill-bundle.md): generated output layout.
- [Verifier](./verifier.md): target metadata checks.
- [Usage](./usage.md): command reference.
