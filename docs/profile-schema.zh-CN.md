# Profile Schema

英文版：[profile-schema.md](./profile-schema.md)

Profile 是团队长期认可的工程准则源码。

它描述项目希望 agent 如何工作：哪些资料更权威，哪些边界不能碰，哪些工具或来源必须使用，验证要到什么深度，proof 放在哪里，什么情况必须停下来 review。

Profile 不写当前任务的具体计划。当前任务要改哪些文件、跑哪些命令、停在哪个 review gate，由 workflow 在 task contract 里展开。

Profile 是严格 YAML：未知顶层键或未知嵌套键会被拒绝，避免错误静默改变生成出来的 workflow contract。

## 最小 Profile

```yaml
profile:
  id: sample-docs-workflow
  description: Minimal docs workflow profile.
bundle:
  name: sample-docs-workflow
  description: Documentation workflow skills.
constraints:
  default:
    - Preserve unrelated user work.
  shape:
    - Clarify the documentation audience and acceptance criteria before planning.
  gauge:
    - Use project docs and nearby source files as evidence before proposing doc behavior changes.
  seal:
    - Each accepted task must name evidence, boundary, validation, proof, and stop conditions.
  pour:
    - Use lightweight markdown or link checks for docs-only changes.
```

完整的可组合示例可以从这里开始看：

```text
examples/profiles/sample-software/sample-software-plan-first.yaml
```

这个顶层 profile 引入已清洗的软件默认准则，并重命名生成阶段技能，不依赖组织私有路径或私有 workflow 命令。

## 顶层键

| 键 | 用途 |
|---|---|
| `profile` | 稳定 profile `id` 和可选的人类说明。 |
| `includes` | 相对路径或 profile id，会先于当前文件解析。 |
| `bundle` | 面向评审的 bundle `name` 和 `description`。 |
| `plugin` | 可选的 plugin 顶层展示 metadata。 |
| `org` | 可选的所属组织或项目名。 |
| `stages` | 为各阶段设置安装名、目录名、展示名、提示词和 `enabled` 开关。 |
| `resources` | 按阶段复制进生成技能的 `references`、`scripts` 或 `files`。 |
| `skills` | 按阶段设置触发说明，不改变阶段语义。 |
| `terminology` | 写入生成技能指引的项目词汇。 |
| `validation_commands` | 默认或阶段专用验证命令。 |
| `decision_gate_extras` | `shape` 必须额外收敛的决策维度。 |
| `constraints` | 默认或阶段专用工程准则。 |
| `conditional_overlays` | 计划记录所选路线后才启用的路线专用约束、资源和验证。 |

## Includes

用 `includes` 从通用到具体组合项目规则：

```yaml
profile:
  id: sample-software-workflow
includes:
  - sample-software-base
  - sample-software
```

被 include 的 profiles 会先于当前 profile 解析。后面的 profile 可以按 Forma 的合并规则细化前面的字段。

Includes 适合项目默认准则、开发准则、领域准则、语言准则等稳定层。不要用 includes 隐藏一次性用户指令；这种情况应该用 temporary injection。

## 阶段命名和目标展示

当生成技能名需要使用项目语言时，用 `stages`：

```yaml
stages:
  shape:
    name: software-workflow-plan
    directory: software-workflow-plan
    display_name: Software Workflow Plan
    short_description: Clarify software work before finalizing a plan.
    default_prompt: Clarify the software task and stop before repository inspection.
```

阶段键仍然是 `shape`、`gauge`、`seal`、`pour`、`flow`。只重命名可安装名称、目录、展示名和提示词。

## Plugin 展示 metadata

当 profile 用于 `forma create-plugin` 时，`bundle.name` 仍然是 plugin id，
必须保持 lower kebab-case。Codex plugin 的 `interface.displayName` 默认由这个
id title-case 派生。只有当安装界面的品牌名需要不同大小写或措辞时，才使用
`plugin.display_name`：

```yaml
bundle:
  name: api-tools
plugin:
  display_name: API Tools
```

这个字段不改变 plugin id、生成的 skill 名称，也不改变
`<plugin-id>:plan` 这类 Codex plugin 触发名。

## Constraints

保持 `constraints.default` 轻量。把准则放到需要它的阶段：

| 阶段约束 | 适合放什么 |
|---|---|
| `constraints.shape` | 需求澄清、路线选择、范围、计划策略和未决问题。 |
| `constraints.gauge` | 只读收集和整理证据。 |
| `constraints.seal` | task contract 必须写清楚的边界、验证、proof 和停手条件。 |
| `constraints.pour` | 当前 task 执行、验证 gate、评审门禁和证明。 |
| `constraints.flow` | 连续执行时的继续条件和停止条件。 |

不好的写法：

```yaml
constraints:
  default:
    - Always read all docs, all plans, all generated baselines, and all run evidence.
```

更好的写法：

```yaml
constraints:
  default:
    - Preserve unrelated user work.
  gauge:
    - Read only evidence needed for the selected scope.
  seal:
    - Put exact validation commands or shared checks into each accepted task.
  pour:
    - Execute only the current accepted task and record proof under `plans/issue-<id>/runs/`.
```

## Resources

Resources 会把阶段拥有的文件复制进生成技能：

```yaml
resources:
  shape:
    references:
      - source: references/backend-workflow-rules.md
        dest: backend-rules.md
    scripts:
      - source: ../../../source/methodology/resources/shared/script/github_issue_context.py
        dest: github_issue_context.py
```

Resources 适合放稳定 references 和明确需要的辅助脚本。来源读取器和辅助脚本应该由 profile 或 temporary injection 明确选择，不应该作为无归属的基础能力出现。

## Validation Commands

用 `validation_commands` 给生成技能提供验证指引：

```yaml
validation_commands:
  default:
    - python -m pytest tests/
  pour:
    - go test ./...
```

Validation commands 是工作流指引，不会替代 task contract 中针对当前任务写出的验证证明路径。

## Conditional Overlays

路线专用行为放进 conditional overlays：

```yaml
conditional_overlays:
  docs-only:
    constraints:
      pour:
        - Keep edits limited to documentation files.
    validation_commands:
      pour:
        - git diff --check
```

docs-only、migration、generated-baseline、governance、backend、cross-layer 等较重或场景专用规则适合放在这里。

## Temporary Injection 和 Profile

长期、稳定、需要作为项目源码评审的准则，用 tracked profile。

这些准则适合 temporary injection：

- 一次性；
- 只属于当前生成；
- 实验性；
- 还没准备好成为长期维护策略；
- 通过 `forma-creator` 临场定制后，先试用再决定是否长期化。

Temporary injection 应先分类确认后的准则，再写 JSON。不要为了保留上下文，把大段来源文档复制进 injection。

## 常见错误

- 把宽泛读取准则放进 `constraints.default`。
- 重命名语义阶段键，而不是 `stages.<stage>.name`。
- 把私有下游命令复制进公开 examples。
- 用 temporary injection 长期承载本应评审成 profile 的准则。
- 添加来源读取器，但没有让 profile 或 injection 明确拥有它。
- 把 `forma verify` 当成人工 profile 评审的替代品。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：profile 如何落到当前任务 contract。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Forma Creator](./forma-creator.zh-CN.md)：临场准则如何先进入一次性 workflow。
- [Examples](./examples.zh-CN.md)：sample profile 示例。
- [使用说明](./usage.zh-CN.md)：命令参考。
