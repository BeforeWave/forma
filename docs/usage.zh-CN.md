# 使用说明

英文版：[usage.md](./usage.md)

这页是 Forma 的命令参考。第一次跑通请先看 [快速开始](./quick-start.zh-CN.md)。

## 命令

### `forma verify <path>`

验证生成的 workflow bundle 或 `forma-creator` bundle：

```bash
forma verify /tmp/backend-plan-first-codex
```

安装、提交或分享生成 bundle 前，先运行这个命令。

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

- `--profile <file>`：顶层 tracked profile。省略时，Forma 会输出无注入的通用 Plan-First workflow，技能名是 `forma-plan`、`forma-ground`、`forma-lock`、`forma-execute` 和 `forma-showhand`。

开发时可选覆盖：

- `--methodology <dir>`：使用指定的方法目录，而不是打包内置的运行时资源。

Profile 格式见 [Profile Schema](./profile-schema.zh-CN.md)。

### `forma create-plugin`

从 profile 生成本地 plugin 产物。当前 plugin 输出只支持 Codex：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
```

输出根目录包含 `.codex-plugin/plugin.json`、根 `.forma-manifest.json` 和 `skills/<skill-id>/` 子目录。它不会顺带输出 `dist/skill-bundles` 或 sibling bundle。

必需选项：

- `--target codex`
- `--output <dir>`

可选输入：

- `--profile <file>`：顶层 tracked profile。省略时，plugin 会暴露 `forma-plan`、`forma-ground`、`forma-lock`、`forma-execute` 和 `forma-showhand`。

`--target claude-code` 会明确失败，因为当前不支持 Claude Code plugin 输出。

### `forma build-creator`

生成 target 专用的可安装 `forma-creator`：

```bash
forma build-creator \
  --target codex \
  --output /tmp/forma-creator-dist
```

必需选项：

- `--target codex|claude-code`
- `--output <dir>`

开发时可选覆盖：

- `--source <dir>`：使用指定的 `forma-creator` 源目录，而不是打包内置的运行时资源。

每个生成的 `forma-creator` 都固定一个 target。Codex creator 生成 Codex 形态的 workflow bundle，并且可以在固定 target contract 允许时生成 Codex plugin。Claude Code creator 只生成 Claude Code 形态的 workflow bundle。Agent 侧生成路径见 [Forma Creator](./forma-creator.zh-CN.md)。

### `forma install`

安装已经验证过的本地单个 skill、skill bundle 或 Codex plugin：

```bash
forma install --target codex --scope project /tmp/forma-codex-bundle
forma install --target codex --scope project /tmp/forma-codex-plugin
forma install --target claude-code --scope user /tmp/forma-claude-code-bundle
```

必需参数和选项：

- `PATH`：本地产物路径；这个命令故意不做 URL 下载。
- `--target codex|claude-code`
- `--scope user|project`

覆盖行为：

- 不加 `--replace` 时，如果目标目录已经存在，会拒绝覆盖。
- 加 `--replace` 时，Forma 只替换 verified source 对应的目标产物。
- Claude Code plugin 安装会明确失败。

### `forma explain`

输出标准编写指南，让外部 Agent 不需要阅读 Forma 源码：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

当另一个 Agent 需要起草 profile 或 temporary injection 时，用这个命令给它规则。

## 安装目标

Forma 生成 target 专用 bundle 和 Codex plugin。`forma install` 会把 verified 本地产物写到对应位置：

| 目标 | 个人安装 | 项目/团队安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | `$HOME/.codex/plugins` | `.codex/plugins` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

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

### 一次性 creator 命名

通过 `forma-creator` 现场生成时，用一次性注入里的 `rename`：

```json
{
  "rename": {
    "prefix": "backend-plan-first",
    "stages": {
      "shape": "backend-plan-first-plan-issue",
      "flow": "backend-plan-first-showhand"
    }
  }
}
```

规则：

- `rename.prefix` 会生成 `<prefix>-shape`、`<prefix>-gauge`、`<prefix>-seal`、`<prefix>-pour`、`<prefix>-flow`；
- `rename.stages` 可以覆盖单个阶段的完整技能名；
- 名字必须唯一，必须是 kebab-case，不能直接叫裸阶段名 `shape` 或 `flow`；
- creator 的一次性注入不接受 profile 风格的 `stages.shape.name`。长期命名进 profile，现场命名进 `rename`。

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

- `source/methodology/`：生成 `shape`、`gauge`、`seal`、`pour`、`flow` 的标准 Plan-First 方法。
- `source/skill-creator/`：自包含的 `forma-creator` 源码，包含 references、creator script 和 verifier。
- `src/forma/`：Python CLI、profile compiler、runtime asset resolver 和 target emitters。
- `profiles/forma-self/`：Forma 管理本仓库时使用的 profile。
- `examples/profiles/`：经过脱敏的 profile 示例。
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

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、门禁、边界和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源格式。
- [Forma Creator](./forma-creator.zh-CN.md)：Agent 侧一次性生成。
- [Verifier](./verifier.zh-CN.md)：验证检查和限制。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
