# 使用说明

英文版：[usage.md](./usage.md)

这页是 Forma 的命令参考。第一次跑通请先看 [快速开始](./quick-start.zh-CN.md)。

## 命令

### `forma verify <path>`

验证生成的 skill bundle、`forma-creator` bundle 或 Codex plugin：

```bash
forma verify /tmp/backend-plan-first-codex
```

安装、提交或分享生成 workflow 产物前，先运行这个命令。

`forma verify` 检查结构和方法规则。它不替代 profile 评审，也不替代产品判断。验证边界见 [Verifier](./verifier.zh-CN.md)。

### `forma create-bundle`

把标准方法和解析后的 tracked profile 组合起来，生成 target 专用 workflow bundle：

```bash
forma create-bundle --target codex --output /tmp/forma-codex-bundle
```

必需选项：

- `--target codex|claude-code`
- `--output <dir>`

可选输入：

- `--profile <file>`：顶层 tracked profile。省略时，Forma 会输出通用 Plan-First skills，技能名是 `forma-plan`、`forma-ground`、`forma-lock`、`forma-execute` 和 `forma-showhand`。

开发时可选覆盖：

- `--methodology <dir>`：使用指定的方法目录，而不是打包内置的运行时资源。

Profile 格式见 [Profile Schema](./profile-schema.zh-CN.md)。

### `forma create-plugin`

从 profile 生成本地 plugin 产物。当前 plugin 输出只支持 Codex：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
```

输出根目录包含 `.codex-plugin/plugin.json`、根 `.forma-manifest.json` 和 `skills/<skill-id>/` 子目录。它不会顺带输出 `dist/skill-bundles` 或 sibling bundle。

对 tracked profile 来说，Codex plugin id 来自 profile 的 `bundle.name`。plugin 展示名也从这个值派生，`plugin.json` 指向嵌套的 `./skills/` 目录。嵌套 skill 名称跟随 `.forma-manifest.json` 记录的 emitted skill 名称。如果 profile 通过 `stages.<stage>.name` 改了技能名，plugin 也会暴露这些改名后的 skills。

必需选项：

- `--target codex`
- `--output <dir>`

可选输入：

- `--profile <file>`：顶层 tracked profile。省略时，plugin 会暴露 `forma-plan`、`forma-ground`、`forma-lock`、`forma-execute` 和 `forma-showhand`。

`--target claude-code` 会明确失败，因为当前不支持 Claude Code plugin 输出。

### `forma build-creator`

生成 target 专用的可安装 `forma-creator`：

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

必需选项：

- `--target codex|claude-code`
- `--output <dir>`

开发时可选覆盖：

- `--source <dir>`：使用指定的 `forma-creator` 源目录，而不是打包内置的运行时资源。

每个生成的 `forma-creator` 都固定一个 target。Codex creator 生成 Codex 形态的 skill bundle，并且可以在固定 target contract 允许时生成 Codex plugin。Claude Code creator 只生成 Claude Code 形态的 skill bundle。Agent 侧生成路径见 [Forma Creator](./forma-creator.zh-CN.md)。

### `forma install`

安装已经验证过的本地单个 skill 或 skill bundle：

```bash
forma install --target codex --scope project /tmp/forma-codex-bundle
forma install --target claude-code --scope user /tmp/forma-claude-code-bundle
```

必需参数和选项：

- `PATH`：本地产物路径；这个命令故意不做 URL 下载。
- `--target codex|claude-code`
- `--scope user|project`

覆盖行为：

- 不加 `--replace` 时，如果目标目录已经存在，会拒绝覆盖。
- 加 `--replace` 时，Forma 只替换 verified source 对应的目标产物。
- Codex plugin 安装会明确失败，并提示使用
  `codex plugin add <plugin>@<marketplace>` 或 Codex plugin UI。

### `forma explain`

输出标准编写指南，让外部 Agent 不需要阅读 Forma 源码：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

当另一个 Agent 需要起草 profile 或 temporary injection 时，用这个命令给它规则。轻量起草 profile 的常用方式是：先运行 `forma explain profile --target codex`，再让 Agent 读仓库、吸收人的补充，并提出 tracked profile YAML。这个路径的产物是 profile 源，不是一次性 harness。

## 安装目标

Forma 生成 target 专用 skill bundle。`forma install` 会把 verified 本地 skill 产物写到对应位置：

| 目标 | 个人安装 | 项目安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

Codex plugin 输出是本地 plugin source。把生成出的 plugin 加到 Codex marketplace 后，
用 `codex plugin add <plugin>@<marketplace>` 安装，或在 Codex plugin UI 里安装。

target 发现规则、metadata 和信任边界见 [Targets](./targets.zh-CN.md)。

## 重命名生成技能

Forma 保留 `shape`、`gauge`、`seal`、`pour`、`flow` 这些语义阶段，但生成技能名可以使用项目自己的语言。

### 长期 profile 命名

Tracked profile 里，设置 `stages.<stage>`：

```yaml
stages:
  shape:
    name: backend-plan-first-plan-issue
    directory: backend-plan-first-plan-issue
    display_name: Backend Plan-First Plan Issue
  gauge:
    name: backend-plan-first-ground-plan
    directory: backend-plan-first-ground-plan
    display_name: Backend Plan-First Ground Plan
```

规则：

- `name` 是 skill frontmatter 里的名字；
- `directory` 是安装目录名；
- `display_name` 是 target 里的展示名；
- `name` 和 `directory` 必须是 lower kebab-case；
- 语义阶段键仍然是 `shape`、`gauge`、`seal`、`pour`、`flow`。
- 同一个 profile 用于 `forma create-plugin` 时，plugin id 仍然是 `bundle.name`，plugin 的嵌套 skills 跟随改名后的 emitted skills。

### 一次性 creator 命名

通过 `forma-creator` 现场生成时，不是让用户给 Agent 一个 JSON 文件。用户应该用自然语言告诉 Agent 命名意图；creator 再分类这条要求，并在内部写 temporary injection。

示例话术：

```text
使用 forma-creator 生成这套 workflow，技能名前缀用 `backend-plan-first`。
planning skill 命名为 `backend-plan-first-plan-issue`，showhand skill 命名为
`backend-plan-first-showhand`。其他技能名从前缀推导。
生成前先展示拟定的名字，然后验证生成 bundle。
```

规则：

- creator 生成的 injection 应使用 `rename.prefix` 生成 `<prefix>-plan`、`<prefix>-ground`、`<prefix>-lock`、`<prefix>-execute`、`<prefix>-showhand`；
- creator 生成的 injection 只在覆盖单个阶段完整技能名时使用 `rename.stages`；
- 内部 injection map 使用内部阶段键 `shape`、`gauge`、`seal`、`pour`、`flow`，不要用 `forma-plan` 或 `forma-showhand` 这类对外 skill id 当键；
- 名字必须唯一，必须是 kebab-case，不能直接叫裸阶段名 `shape` 或 `flow`；
- creator 的一次性注入不接受 profile 风格的 `stages.shape.name`。长期命名进 profile，现场命名进 `rename`。
- 通过 `forma-creator` 生成 Codex plugin 时，`rename.prefix` 也会成为 plugin id。没有 prefix 时，plugin id 保持 `forma`。

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

- `source/methodology/`：生成 task 级 Plan-First 工作流技能的标准方法。
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

因此，通过 pip 或 pipx 安装后的命令不依赖 Forma 源码仓库。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、task 契约、门禁、边界和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源格式。
- [Forma Creator](./forma-creator.zh-CN.md)：Agent 侧一次性生成。
- [Verifier](./verifier.zh-CN.md)：验证检查和限制。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
