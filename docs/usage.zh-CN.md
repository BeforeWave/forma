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

`forma verify` 检查结构和方法规则。它不替代 profile review 或产品判断。Bundle 结构见 [Skill Bundle](./skill-bundle.zh-CN.md)。

### `forma create`

把标准方法和解析后的 tracked profile 组合起来，生成目标环境专用 workflow bundle：

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
```

必需选项：

- `--target codex|claude-code`
- `--profile <file>`
- `--output <dir>`

开发时可选覆盖：

- `--methodology <dir>`：使用指定的方法目录，而不是打包内置的运行时资源。

Profile 格式见 [Profile Schema](./profile-schema.zh-CN.md)。

### `forma build-creator`

生成目标环境专用的可安装 `forma-creator`：

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

每个生成的 `forma-creator` 都固定一个目标环境。Codex creator 生成 Codex 形态的 workflow bundle。Claude Code creator 生成 Claude Code 形态的 workflow bundle。

### `forma explain`

输出标准编写指南，让外部 Agent 不需要阅读 Forma 源码：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

当另一个 Agent 需要起草 profile 或 temporary injection 时，用这个命令给它规则。

## 安装目标

Forma 生成的是目标环境专用 bundle。把生成技能目录复制到对应位置：

| 目标 | 个人安装 | 项目/团队安装 |
|---|---|---|
| Codex | `$HOME/.agents/skills` | `.agents/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

Codex 的项目 skills 可以放在当前工作目录、父目录或仓库根目录下的 `.agents/skills`。

Claude Code 的项目 skills 放在 `.claude/skills`。

信任项目 skills 前先审查内容，因为 skills 可以包含脚本和目标环境专用工具行为。

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
- `display_name` 是目标环境展示名；
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
forma verify <generated-suite-dir>
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

- `forma create` 默认使用打包内置的方法，除非提供 `--methodology`。
- `forma build-creator` 默认使用打包内置的 creator 源，除非提供 `--source`。
- `forma explain` 从打包内置的 references 渲染编写指南。

因此，通过 pip 或 pipx 安装后的命令不依赖 Forma 源码仓库。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、门禁、边界和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源格式。
