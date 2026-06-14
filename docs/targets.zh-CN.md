# Targets

英文版：[targets.md](./targets.md)

Forma 生成的是 target 专用 workflow 产物。Codex plugin 是同一套 task 级 skills 的 Codex 安装形态。这里的 target 指加载这套技能的 agent 环境，例如 Codex、Claude Code 或 OpenCode。

同一份 tracked profile 可以生成到不同 target；`forma-creator` 生成的一次性 workflow 则由 creator 固定 target。无论哪条路径，生成产物都必须匹配实际加载它的 agent。

## 支持的 Target

| 产物 | CLI target | 个人安装 | 项目安装 |
|---|---|---|---|
| Codex skills | `codex` | `$HOME/.codex/skills` | `.agents/skills` |
| OpenCode skills | `opencode` | `$HOME/.config/opencode/skills` | `.opencode/skills` |
| Codex plugins | `codex` | Codex marketplace / plugin UI | Codex marketplace / plugin UI |
| Claude Code skills | `claude-code` | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `claude-code` | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

使用对应的 `--target`：

```bash
forma build bundle --target codex --profile <profile.yaml> --output <dir>
forma build bundle --target claude-code --profile <profile.yaml> --output <dir>
forma build bundle --target opencode --profile <profile.yaml> --output <dir>
forma build plugin --target codex --profile <profile.yaml> --output <dir>
forma build plugin --target claude-code --profile <profile.yaml> --output <dir>
```

OpenCode 使用 direct skill 形态。Forma 生成 OpenCode 原生 skill bundle，不生成
OpenCode JS/TS runtime plugin。

## Codex

Codex 会从 repository、user、admin 和 bundled system 等位置读取 skills。

Codex 项目级 skills 安装到 `.agents/skills`。用户级 skills 安装到
`$HOME/.codex/skills`，与 Codex UI / installer 的本地 skill 安装面一致。

对 Codex plugins，Forma 只生成本地 plugin source。先运行
`codex plugin marketplace list`，询问用户选择哪个已有 marketplace，
或者是否创建/注册一个新的 marketplace；确认所选 marketplace catalog 指向生成出的
plugin root 后，再交给 Codex 安装和启用：运行
`codex plugin add <plugin-id>@<marketplace-name>`，或在 Codex plugin UI 里安装。安装后新开 thread。
如果 Codex CLI 输出或 marketplace 行为和这里不一致，再看当前 Codex 官方文档或
`codex plugin marketplace --help`。

把 plugin 交给其他用户或 agent 前，先运行 `forma verify <plugin-root>`。需要结构化
安装 handoff 时，使用 `forma build plugin --format agent|json` 的输出，并把安装路线
说清楚：Codex plugin 交给 Codex 安装，不通过 `forma install`。

- [Install a local plugin manually](https://developers.openai.com/codex/plugins/build#install-a-local-plugin-manually)
- [Add a marketplace from the CLI](https://developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli)

对 profile 生成的 Codex plugin，`<plugin-id>` 是 profile 的 `bundle.name`。对 Codex `forma-creator` 生成的 plugin，如果存在 `rename.prefix`，`<plugin-id>` 就是这个 prefix；否则保持 `forma`。`plugin.display_name` 设置 Codex plugin 安装界面的展示名，不改变 plugin id、plugin-local skill 名或触发名。plugin manifest 指向 `./skills/`。如果 nested plugin skill 名称带有精确的 `<plugin-id>-` 前缀，Forma 会去掉这个前缀，所以 plugin `forma` 暴露 `plan`、`ground`、`lock`、`execute` 和 `showhand` 这些 local 阶段。Profile 或 creator 改名后的 skills 也会按同样规则出现在 plugin 里。

Metadata 会记录 `forma:plan` 这类 qualified name。Plugin 用 `forma:*` 触发；direct skill bundle 用 `forma-*`。

Codex target bundle 可以包含 `agents/openai.yaml`，用于界面信息、调用策略和工具依赖声明。

官方文档见：
<https://developers.openai.com/codex/skills>。

## OpenCode

OpenCode 使用 direct skill 目录。Forma 把 OpenCode 项目级 skills 安装到
`.opencode/skills`，把用户级 skills 安装到
`$HOME/.config/opencode/skills`。OpenCode 也可以读取 `.agents/skills` 和
`.claude/skills` 里的兼容 direct skills，但 Forma 的 `opencode` install
target 使用 OpenCode 原生 skill 根目录。

Forma 不生成 OpenCode JS/TS runtime plugin。

官方文档见：
<https://opencode.ai/docs/skills>。

## Claude Code

Claude Code 的个人 skills 放在 `$HOME/.claude/skills`。项目级 skills 放在 `.claude/skills`。

Claude Code 也会在仓库中发现父目录和嵌套目录里的 `.claude/skills`。项目级 skills 的工具权限可能需要 workspace trust 后才生效。

Claude Code plugin 输出包含 `.claude-plugin/plugin.json`、根 `.forma-manifest.json` 和嵌套 `skills/<skill-name>/` 目录。先运行 `forma verify <plugin-root>`，再用 `forma install --target claude-code --scope user|project <plugin-root>` 安装整个 plugin root。

Claude Code plugin 里的 skills 是 plugin-local 命名。生成 plugin 时，如果 skill 名称以精确的 `<plugin-name>-` 开头，Forma 会去掉这个前缀。比如 plugin `forma` 里，plugin-local 阶段是 `plan`、`ground`、`lock`、`execute` 和 `showhand`。Direct skill bundle 则使用 `forma-*` 形式的独立 skill 名。

官方文档见：
<https://code.claude.com/docs/en/skills>。

## Target 专用输出

Target adapter 会影响生成的 metadata 和安装行为，但不应该改变 task 级 workflow contract 本身。

例如：

- Codex 输出可以包含 `agents/openai.yaml`。
- Claude Code 输出不应该包含 Codex-only metadata。
- OpenCode 输出使用原生 direct skill frontmatter，包含
  `compatibility: opencode` 和 string-to-string `metadata`；不应该包含
  `agents/openai.yaml`、`.codex-plugin` 或 `.claude-plugin` metadata。
- Codex plugin 输出包含 `.codex-plugin/plugin.json`、根 `.forma-manifest.json` 和嵌套 `skills/`。
- Codex plugin 的 `plugin.json` 使用 profile 的 `bundle.name` 或 creator 的 `rename.prefix` 作为 plugin id，并且其中的 `skills` 路径必须指向嵌套 `skills/` 目录。
- Claude Code plugin 输出包含 `.claude-plugin/plugin.json`、根 `.forma-manifest.json` 和嵌套 `skills/`。
- Claude Code plugin 的 `plugin.json` 使用 profile 的 `bundle.name` 或 creator 的 `rename.prefix` 作为 plugin name，并且其中的 `skills` 路径必须指向嵌套 `skills/` 目录。
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
