# 使用说明

英文版：[usage.md](./usage.md)

这页是 Forma 的命令参考。第一次跑通不要从命令背起，先看 [快速开始](./quick-start.zh-CN.md)：让 agent 提炼项目规则，确认后生成并安装 workflow。

不带子命令运行 `forma` 是一个成功的 discovery 入口。它会以退出码 `0`
打印和 `forma --help` 相同的 agent 路由指南，所以 coding agent 不确定该走哪条
命令路径时，可以先从这里开始。

## Agent 命令路由

| 目标 | 命令路径 | 下一步 |
|---|---|---|
| 让 agent 读取 profile 编写规则 | `forma explain profile --target codex` | agent-facing 命令；把输出作为只读指南，再结合项目事实起草 profile。 |
| 从已经 review 的 tracked profile 生成 skill bundle | `forma create-bundle --target <target> --profile <profile.yaml> --output <dir>` | 生成 `target` 填 `codex`、`claude-code` 或 `opencode`；运行 `forma verify <dir>`，再用匹配的 target 安装。 |
| 生成默认 Plan-First skill bundle | `forma create-bundle --target <target> --output <dir>` | 生成 `target` 填 `codex`、`claude-code` 或 `opencode`；运行 `forma verify <dir>`，再用匹配的 target 安装。 |
| 生成 plugin source | `forma create-plugin --target codex|claude-code --profile <profile.yaml> --output <dir>` | 运行 `forma verify <dir>`；Codex plugin 通过 Codex 安装，Claude Code plugin root 用 `forma install --target claude-code` 安装。 |
| handoff 前诊断生成产物 | `forma doctor <dir>` 或 `forma doctor --json <dir>` | 用结果确认 artifact kind、target、验证状态、Forma 是否能安装、安装路线、blockers 和下一步。 |
| 构建可选 creator 临场路径 | `forma build-creator --target <target> --output <dir>` | 只在 creator 路径使用；运行 `forma verify <dir>/<target>/forma-creator`，再用匹配的 target 安装。 |
| 给 agent 提供 temporary-injection 规则 | `forma explain temporary-injection --target codex` | 只用于可选 creator / 临场生成路径。 |

使用 `create-bundle` 或 `create-plugin`；旧的 `forma create` 命令不再支持。

## 命令

### `forma` / `forma --help`

打印根命令指南和命令列表。不带子命令时，`forma` 返回退出码 `0`，并显示
和 `forma --help` 相同的路由指南。

当 agent 需要判断是打印 authoring guidance、create skill bundle、create plugin、
install verified 本地产物、verify 产物，还是构建可选 creator 时，先用这个命令做 discovery。

### `forma verify <path>`

验证生成的 skill bundle、`forma-creator` bundle、Codex plugin 或 Claude Code plugin：

```bash
forma verify /tmp/settings-workflow-codex
forma verify --json /tmp/settings-workflow-codex
```

安装、提交或分享生成 workflow 产物前，先运行这个命令。

下一步：

- 如果 skill bundle 或 creator 验证通过，用 `forma install` 安装 verified 本地路径。
- 如果 Codex plugin 验证通过，通过 Codex 安装，不要用 `forma install`。
- 如果 Claude Code plugin 验证通过，用 `forma install --target claude-code` 安装 plugin root。
- 如果路径含义不清楚，运行 `forma doctor <path>` 查看安装路线和下一步。

`forma verify` 检查结构和方法规则。它不替代 profile 评审，也不替代产品判断。验证边界见 [Verifier](./verifier.zh-CN.md)。

当其他工具或 agent 需要结构化结果时，使用 `--json`。JSON report 保持同样的退出码契约，并为每条 rule result 提供语义 failure class。

### `forma doctor <path>`

handoff 或安装前诊断一个生成产物：

```bash
forma doctor /tmp/settings-workflow-codex
forma doctor --json /tmp/forma-codex-plugin
```

doctor 输出会说明 artifact kind、target、验证状态、`forma install` 是否支持、当前是否可安装、正确安装路线、blockers 和下一步。

当用户或 agent 不确定当前路径是 skill、skill bundle、Codex plugin、Claude Code plugin、损坏产物还是不支持的目录时，先运行这个命令。

### `forma create-bundle`

把标准方法和解析后的 tracked profile 组合起来，生成 target 专用 workflow bundle：

```bash
forma create-bundle --target codex --output /tmp/forma-codex-bundle
```

必需选项：

- `--target codex|claude-code|opencode`
- `--output <dir>`

可选输入：

- `--profile <file>`：顶层 tracked profile。省略时，Forma 会输出 `plan`、`ground`、`lock`、`execute` 和 `showhand` 这些阶段对应的通用 direct skills，skill 名带 `forma-*` 前缀。

开发时可选覆盖：

- `--methodology <dir>`：使用指定的方法目录，而不是打包内置的运行时资源。

下一步：运行 `forma verify <output-dir>`，再用 `forma install` 安装 verified 本地 bundle。

Profile 格式见 [Profile Schema](./profile-schema.zh-CN.md)。

### `forma create-plugin`

从 profile 生成本地 plugin 产物：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma create-plugin --target claude-code --output /tmp/forma-claude-code-plugin
```

Codex plugin 输出根目录包含 `.codex-plugin/plugin.json`、根 `.forma-manifest.json` 和 `skills/<skill-id>/` 子目录。Claude Code plugin 使用 `.claude-plugin/plugin.json`，同样带根 manifest 和嵌套 `skills/<skill-id>/`。它不会顺带输出 `dist/skill-bundles` 或 sibling bundle。

对 tracked profile 来说，plugin id 来自 profile 的 `bundle.name`。plugin 展示名也从这个值派生，`plugin.json` 指向嵌套的 `./skills/` 目录。如果 generated skill 名称以精确的 `<plugin-id>-` 开头，Forma 会在 plugin-local skill 名称里去掉这个前缀。比如 plugin `forma` 中，默认 local 阶段是 `plan`、`ground`、`lock`、`execute` 和 `showhand`。

Plugin 输出会在 manifest 和 metadata prompt 里记录 `forma:plan` 这类 qualified name。Plugin 用 `forma:*` 触发；direct skill bundle 用 `forma-*`。

必需选项：

- `--target codex|claude-code`
- `--output <dir>`

可选输入：

- `--profile <file>`：顶层 tracked profile。省略时，plugin 会暴露 plugin-local 的 `plan`、`ground`、`lock`、`execute` 和 `showhand` 阶段。

下一步：运行 `forma verify <output-dir>`。Codex plugin 通过 Codex marketplace/plugin UI 安装。Claude Code plugin root 用 `forma install --target claude-code --scope user|project <output-dir>` 安装。

### `forma build-creator`

生成 target 专用的可安装 `forma-creator`。这是可选临场路径：不想先处理 profile 文件时，可以让 agent 临场生成 workflow：

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target opencode --output /tmp/forma-creator-dist
```

必需选项：

- `--target codex|claude-code|opencode`
- `--output <dir>`

开发时可选覆盖：

- `--source <dir>`：使用指定的 `forma-creator` 源目录，而不是打包内置的运行时资源。

每个生成的 `forma-creator` 都固定一个 target。Codex creator 生成 Codex 形态的 skill bundle 和 Codex plugin。Claude Code creator 生成 Claude Code 形态的 skill bundle 和 Claude Code plugin。OpenCode creator 生成 OpenCode 原生 skill bundle，不生成 OpenCode JS/TS runtime plugin。临场定制路径见 [Forma Creator](./forma-creator.zh-CN.md)。

下一步：运行 `forma verify <output-dir>/<target>/forma-creator`，再用 `forma install`
安装这个 verified creator 路径。

### `forma install`

安装已经验证过的本地单个 skill、skill bundle 或 Claude Code plugin root：

```bash
forma install --target codex --scope project /tmp/forma-codex-bundle
forma install --target opencode --scope project /tmp/forma-opencode-bundle
forma install --target claude-code --scope user /tmp/forma-claude-code-bundle
forma install --target claude-code --scope project /tmp/forma-claude-code-plugin
```

必需参数和选项：

- `PATH`：本地产物路径；这个命令故意不做 URL 下载。
- `--target codex|claude-code|opencode`
- `--scope user|project`

覆盖行为：

- 不加 `--replace` 时，如果目标目录已经存在，会拒绝覆盖。
- 加 `--replace` 时，Forma 只替换 verified source 对应的目标产物。
- Codex plugin 安装会明确报错，并提示 Codex marketplace 设置、
  `codex plugin add <plugin>@<marketplace-name>`，以及安装后新开 thread。
- Claude Code plugin root 会安装到项目级 `.claude/skills/<plugin-name>` 或用户级 `$HOME/.claude/skills/<plugin-name>`。

下一步：安装 skill、skill bundle 或 Claude Code plugin 后，新开 agent thread，让新安装的 skills 被发现。

### `forma explain`

输出标准编写指南，让外部 agent 不需要阅读 Forma 源码：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

当另一个 agent 需要起草 profile 或 temporary injection 时，用这个命令给它规则。正常 profile-first 路径可以直接说：

```text
用 Forma 给这个项目生成一套 Codex workflow。
先把你提炼出的项目规则给我看；确认后再生成并安装。
```

agent 会用 `forma explain profile --target codex` 读取 profile 编写标准，再结合项目事实提出 profile YAML。只有这些规则需要长期复用时，才把 profile 提交进版本控制。

下一步：profile review 通过后，用 `forma create-bundle` 生成 skill bundle，或用
`forma create-plugin` 生成 plugin source。

## 安装目标

Forma 生成 target 专用 skill bundle。`forma install` 会把 verified 本地 skill 产物写到对应位置：

| 目标 | 个人安装 | 项目安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.agents/skills` |
| OpenCode skills | `$HOME/.config/opencode/skills` | `.opencode/skills` |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

OpenCode 使用 direct skill bundle。先用 `forma create-bundle --target opencode`
生成 OpenCode bundle，验证后用 `forma install --target opencode` 安装。Forma
不生成 OpenCode JS/TS runtime plugin。

Codex plugin 输出是本地 plugin source。Forma 不安装 Codex plugin。按照当前 Codex
官方文档把生成出的 plugin root 加到 Codex marketplace，然后运行
`codex plugin add <plugin>@<marketplace-name>`，或在 Codex plugin UI 里安装。安装后新开
Codex thread，这样 plugin skills 才会被发现。

Claude Code plugin 输出可以通过 Forma 安装，因为 Claude Code 会从 `.claude/skills/<plugin-name>` 加载 skills-directory plugin。

- [Install a local plugin manually](https://developers.openai.com/codex/plugins/build#install-a-local-plugin-manually)
- [Add a marketplace from the CLI](https://developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli)

target 发现规则、metadata 和信任边界见 [Targets](./targets.zh-CN.md)。

## 重命名生成技能

Forma 保留 `shape`、`gauge`、`seal`、`pour`、`flow` 这些语义阶段，但生成技能名可以使用项目自己的语言。

### 长期 profile 命名

Tracked profile 里，设置 `stages.<stage>`：

```yaml
stages:
  shape:
    name: settings-workflow-plan
    directory: settings-workflow-plan
    display_name: Settings Workflow Plan
  gauge:
    name: settings-workflow-ground
    directory: settings-workflow-ground
    display_name: Settings Workflow Ground
```

规则：

- `name` 是 skill frontmatter 里的名字；
- `directory` 是安装目录名；
- `display_name` 是 target 里的展示名；
- `name` 和 `directory` 必须是 lower kebab-case；
- 语义阶段键仍然是 `shape`、`gauge`、`seal`、`pour`、`flow`。
- 同一个 profile 用于 `forma create-plugin` 时，plugin id 仍然是 `bundle.name`；如果生成名带有这个精确前缀，plugin-local skills 会去掉前缀。Plugin 使用最终的 `<plugin-id>:<local-skill>` 形式触发，默认 Forma plugin 是 `forma:plan` 这类 `forma:*`。

### 一次性 creator 命名

通过 `forma-creator` 临场生成时，用户不需要给 agent 一个 JSON 文件。用自然语言告诉 agent 命名意图；creator 再分类这条要求，并在内部写 temporary injection。

示例话术：

```text
使用 forma-creator 生成这套 workflow，技能名前缀用 `settings-workflow`。
生成前先展示拟定的技能名；我确认后再生成并验证 bundle。
```

规则：

- creator 生成的 injection 应使用 `rename.prefix` 生成 `<prefix>-plan`、`<prefix>-ground`、`<prefix>-lock`、`<prefix>-execute`、`<prefix>-showhand`；
- creator 生成的 injection 只在覆盖单个阶段完整技能名时使用 `rename.stages`；
- 内部 injection map 使用内部阶段键 `shape`、`gauge`、`seal`、`pour`、`flow`，不要用 `plan`、`showhand` 或 `forma-*` direct skill 名这类最终输出名当键；
- 名字必须唯一，必须是 kebab-case，不能直接叫裸阶段名 `shape` 或 `flow`；
- creator 的一次性注入不接受 profile 风格的 `stages.shape.name`。长期命名进 profile，临场命名进 `rename`。
- 通过 `forma-creator` 生成 plugin 时，`rename.prefix` 也会成为 plugin id/name。没有 prefix 时，plugin id/name 保持 `forma`。
- Plugin-local skill 名会在存在精确 plugin-name 前缀时去掉该前缀。Plugin 使用 `<plugin-id>:<local-skill>` 触发，默认 Forma plugin 是 `forma:*`；direct skill bundle 使用 `forma-*`。

改名后验证生成 bundle：

```bash
forma verify <generated-bundle-dir>
```

## 仓库检查

维护 Forma 仓库时，先完成本地开发安装，再从仓库根目录运行主要检查：

```bash
forma verify source/skill-creator/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
python -m pytest -p no:cacheprovider tests/
git diff --check
```

## 源码结构

- `source/methodology/`：生成 task 级 workflow skills 的标准方法。
- `source/skill-creator/`：自包含的 `forma-creator` 源码，包含 references、creator script 和 verifier。
- `src/forma/`：Python CLI、profile compiler、runtime asset resolver 和 target emitters。
- `profiles/forma-self/`：Forma 管理本仓库时使用的 profile。
- `examples/profiles/`：profile 示例。
- `examples/generated/`：已提交的生成基线，用于检查漂移。
- `tests/`：verifier、creator、runtime asset、profile 和生成基线测试。

详细源码结构见 [仓库结构](../STRUCTURE.md)。

## 安装后的命令行为

打包安装后的 Forma 命令默认使用 `forma.assets` 中的运行时资源。源码路径只作为开发覆盖：

- `forma create-bundle` 和 `forma create-plugin` 默认使用打包内置的方法，除非提供 `--methodology`。
- `forma install` 只安装 verified 本地产物，不下载 URL。
- `forma build-creator` 默认使用打包内置的 creator 源，除非提供 `--source`。
- `forma explain` 从打包内置的 references 渲染编写指南。

因此，通过 `forma-cli` 发行包安装后的命令不依赖 Forma 源码仓库。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、task 契约、门禁、边界和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：profile 如何描述阶段约束、工具习惯、验证和 proof。
- [Forma Creator](./forma-creator.zh-CN.md)：可选临场 workflow 生成路径。
- [Verifier](./verifier.zh-CN.md)：验证检查和限制。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
