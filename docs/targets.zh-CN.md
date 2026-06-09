# Targets

英文版：[targets.md](./targets.md)

Forma 生成的是 target 专用 workflow 产物。Codex plugin 是同一套 task 级 skills 的 Codex 安装形态。这里的 target 指加载这套技能的 agent 环境，例如 Codex 或 Claude Code。

同一份 tracked profile 可以生成到不同 target；`forma-creator` 生成的一次性 workflow 则由 creator 固定 target。无论哪条路径，生成产物都必须匹配实际加载它的 agent。

## 支持的 Target

| 产物 | CLI target | 个人安装 | 项目安装 |
|---|---|---|---|
| Codex skills | `codex` | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | `codex` | Codex marketplace / plugin UI | Codex marketplace / plugin UI |
| Claude Code skills | `claude-code` | `$HOME/.claude/skills` | `.claude/skills` |

使用对应的 `--target`：

```bash
forma create-bundle --target codex --profile <profile.yaml> --output <dir>
forma create-bundle --target claude-code --profile <profile.yaml> --output <dir>
forma create-plugin --target codex --profile <profile.yaml> --output <dir>
```

## Codex

Codex 会从 repository、user、admin 和 bundled system 等位置读取 skills。

Codex 项目级 skills 安装到 `.codex/skills`。用户级 skills 安装到 `$HOME/.codex/skills`。

对 Codex plugins，Forma 只生成本地 plugin source。按照当前 Codex 官方文档把这个
source 加到 Codex marketplace，然后交给 Codex 安装和启用：运行
`codex plugin add <plugin>@<marketplace-name>`，或在 Codex plugin UI 里安装。安装后新开 thread。

- [Install a local plugin manually](https://developers.openai.com/codex/plugins/build#install-a-local-plugin-manually)
- [Add a marketplace from the CLI](https://developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli)

对 profile 生成的 Codex plugin，`<plugin-id>` 是 profile 的 `bundle.name`。对 Codex `forma-creator` 生成的 plugin，如果存在 `rename.prefix`，`<plugin-id>` 就是这个 prefix；否则保持 `forma`。plugin manifest 指向 `./skills/`；`.forma-manifest.json` 记录的 emitted skill 名称决定嵌套 skill 目录和 frontmatter 名称，所以 profile 或 creator 改名后的 skills 会同步出现在 plugin 里。

Codex target bundle 可以包含 `agents/openai.yaml`，用于界面信息、调用策略和工具依赖声明。

官方文档见：
<https://developers.openai.com/codex/skills>。

## Claude Code

Claude Code 的个人 skills 放在 `$HOME/.claude/skills`。项目级 skills 放在 `.claude/skills`。

Claude Code 也会在仓库中发现父目录和嵌套目录里的 `.claude/skills`。项目级 skills 的工具权限可能需要 workspace trust 后才生效。

当前 Forma 不支持 Claude Code plugin 输出。Claude Code 使用 skill bundle。

官方文档见：
<https://code.claude.com/docs/en/skills>。

## Target 专用输出

Target adapter 会影响生成的 metadata 和安装行为，但不应该改变 task 级 workflow contract 本身。

例如：

- Codex 输出可以包含 `agents/openai.yaml`。
- Claude Code 输出不应该包含 Codex-only metadata。
- Codex plugin 输出包含 `.codex-plugin/plugin.json`、根 `.forma-manifest.json` 和嵌套 `skills/`。
- Codex plugin 的 `plugin.json` 使用 profile 的 `bundle.name` 或 creator 的 `rename.prefix` 作为 plugin id，并且其中的 `skills` 路径必须指向嵌套 `skills/` 目录。
- Skill 目录名和 frontmatter 必须符合该 target 的 bundle 契约。

## 分发边界

直接使用 skill 目录，适合本地试用和项目级 workflow。

如果 workflow 要更广泛分发，打包或分发方式可能会和 target 绑定。长期路径里，Forma profile 仍然是工作流来源，再按目标生成需要的产物；creator 路径里，先试用生成产物，再决定哪些准则提升成 profile。

## 信任前先审查

生成的 bundle 可以包含 scripts。信任项目 bundle 前先审查，尤其当 target 支持工具权限或动态上下文注入时。

## 相关文档

- [快速开始](./quick-start.zh-CN.md)：首次跑通安装命令。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Verifier](./verifier.zh-CN.md)：target metadata 检查。
- [使用说明](./usage.zh-CN.md)：命令参考。
