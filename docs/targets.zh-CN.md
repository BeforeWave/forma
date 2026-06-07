# Targets

英文版：[targets.md](./targets.md)

Forma 生成的是 target 专用 skill bundle。Codex plugin 是同一套 skills 的 Codex 安装形态。这里的 target 指加载这套技能的 Agent 环境，例如 Codex 或 Claude Code。

同一份 workflow profile 可以生成到不同 target，但生成产物必须匹配实际加载它的 Agent。

## 支持的 Target

| 产物 | CLI target | 个人安装 | 项目安装 |
|---|---|---|---|
| Codex skills | `codex` | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | `codex` | `$HOME/.codex/plugins` | `.codex/plugins` |
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

Codex 项目级 plugins 安装到 `.codex/plugins/<plugin-id>`。用户级 plugins 安装到 `$HOME/.codex/plugins/<plugin-id>`。安装后的 plugin root 会保留 `.codex-plugin/plugin.json`。

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

Target adapter 会影响生成的 metadata 和安装行为，但不应该改变 workflow contract 本身。

例如：

- Codex 输出可以包含 `agents/openai.yaml`。
- Claude Code 输出不应该包含 Codex-only metadata。
- Codex plugin 输出包含 `.codex-plugin/plugin.json`、根 `.forma-manifest.json` 和嵌套 `skills/`。
- Skill 目录名和 frontmatter 必须符合该 target 的 bundle 契约。

## 分发边界

直接使用 skill 目录，适合本地编写和项目级 workflow。

如果 workflow 要更广泛分发，打包或分发方式可能会和 target 绑定。Forma profile 仍然是工作流来源，再按目标生成需要的产物。

## 信任前先审查

生成的 bundle 可以包含 scripts。信任项目 bundle 前先审查，尤其当 target 支持工具权限或动态上下文注入时。

## 相关文档

- [快速开始](./quick-start.zh-CN.md)：首次跑通安装命令。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Verifier](./verifier.zh-CN.md)：target metadata 检查。
- [使用说明](./usage.zh-CN.md)：命令参考。
