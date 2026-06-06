# 使用说明

英文版：[usage.md](./usage.md)

## 命令

`forma verify <path>`

验证一个 Plan-First 技能套件或 `forma-creator` 套件：

```bash
forma verify /tmp/backend-plan-first-codex
```

`forma create`

把标准方法和解析后的长期 profile 组合起来，生成目标 Agent 专用的工作流套件：

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

`forma build-creator`

生成目标 Agent 专用的可安装 `forma-creator`：

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

`forma explain`

输出 profile 和一次性注入的编写指南，让外部 Agent 不需要阅读 Forma 源码：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

## Profile Schema

长期 profile 是严格的 YAML 来源。未知顶层键或未知嵌套键会被拒绝，避免 profile 静默绕过工作流契约。

允许的顶层键：

- `profile`：稳定 `id` 和可选的人类说明。
- `includes`：相对路径或 profile id，会先于当前文件解析。
- `bundle`：面向评审的 bundle `name` 和 `description`。
- `org`：可选的所属组织或团队名。
- `stages`：为 `shape`、`gauge`、`seal`、`pour`、`flow` 设置安装名、目录名、展示名、提示词和 `enabled` 开关。
- `resources`：按阶段复制进生成技能的 `references`、`scripts` 或 `files`。
- `skills`：按阶段设置触发说明，不改变阶段语义。
- `terminology`：写入生成技能指引的项目词汇。
- `validation_commands`：默认或阶段专用验证命令。
- `decision_gate_extras`：`shape` 必须额外收敛的决策维度。
- `constraints`：默认或阶段专用工作流约束。
- `conditional_overlays`：只有计划记录了所选路线后才启用的路线专用约束、资源和验证。

保持 `constraints.default` 轻量。规划规则放进 `constraints.shape`，只读取证据的规则放进 `constraints.gauge`，计划定稿规则放进 `constraints.seal`，当前任务执行规则放进 `constraints.pour`，自动继续边界放进 `constraints.flow`。

## 重命名生成技能

不想叫 `shape`、`gauge`、`seal`、`pour`、`flow`？可以。Forma 保留这五个阶段的语义，但允许项目把安装后的技能改成自己的名字。

有两条路径。

长期 profile 里，改 `stages.<stage>`：

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

- `name` 是技能 frontmatter 里的名字；
- `directory` 是安装目录名；
- `display_name` 是界面展示名；
- `name` 和 `directory` 必须是 lower kebab-case；
- 语义阶段仍然是 `shape`、`gauge`、`seal`、`pour`、`flow`，不要把阶段键本身改掉。

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

- `rename.prefix` 会生成 `<prefix>-shape`、`<prefix>-gauge`、`<prefix>-seal`、`<prefix>-pour`、`<prefix>-flow`；
- `rename.stages` 可以覆盖单个阶段的完整技能名；
- 名字必须唯一，必须是 kebab-case，不能直接叫裸阶段名 `shape`、`gauge`、`seal`、`pour`、`flow`；
- creator 的一次性注入不接受 profile 风格的 `stages.shape.name` 写法。长期命名进 profile，现场命名进 `rename`。

改完后运行：

```bash
forma verify <generated-suite-dir>
```

验证器会检查 manifest、目录名和 `SKILL.md` frontmatter 是否一致。

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
- `source/skill-creator/`：自包含的 `forma-creator` 源码，包含引用材料、创建脚本和验证器。
- `src/forma/`：命令行工具、profile 编译器、运行时资源解析器和目标界面生成器。
- `profiles/forma-self/`：Forma 管理本仓库时使用的 profile。
- `examples/profiles/`：经过脱敏的 profile 示例。
- `examples/generated/`：已提交的生成基线，用于检查漂移。
- `tests/`：验证器、creator、运行时资源、profile 和生成基线测试。

详细源码结构见 [仓库结构](../STRUCTURE.md)。

## 安装后的命令行为

打包安装后的 Forma 命令默认使用 `forma.assets` 中的运行时资源。源码路径只作为开发覆盖：

- `forma create` 默认使用打包内置的方法，除非提供 `--methodology`。
- `forma build-creator` 默认使用打包内置的 creator 源，除非提供 `--source`。
- `forma explain` 从打包内置的引用材料渲染编写指南。

因此，通过 pip 或 pipx 安装后的命令不依赖 Forma 源码仓库。
