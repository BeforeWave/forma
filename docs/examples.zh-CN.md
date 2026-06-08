# Examples

英文版：[examples.md](./examples.md)

这一页展示 Forma workflow harness 在一个端到端开发目标里应该让哪些东西变得可见。

下面是说明性示例，不是真实 Agent 运行记录。要生成并运行真实示例 bundle，请看 [快速开始](./quick-start.zh-CN.md)。

## 已提交的 Sample 来源

面向读者生成时，从已清洗的软件 sample profile 开始：

```text
examples/profiles/sample-software/sample-software-plan-first.yaml
```

仓库里也保留了 backend sample profile 生成出来的已提交 drift baseline：

```text
examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
```

## 生成 Bundle

```bash
forma create-bundle --target codex --profile examples/profiles/sample-software/sample-software-plan-first.yaml --output /tmp/software-plan-first-codex
forma verify /tmp/software-plan-first-codex
```

把生成出来的阶段技能安装到对应 target。见 [Targets](./targets.zh-CN.md)。

## 示例请求

```text
Use forma-plan to plan this issue first.

Issue:
<粘贴当前 issue、需求描述、问题背景或任务目标>
```

Forma 生成的 workflow 应该让这个请求沿着 task contract 推进，而不是直接跳到实现。

## 技能示例

| 技能 | 预期推进方式 |
|---|---|
| `forma-plan` | 澄清目标、范围、方案、验证模型、计划策略，以及必要的 artifact/evidence boundary。 |
| `forma-ground` | 只检查已接受范围需要的仓库和来源材料。分离事实、风险、未知项和建议。 |
| `forma-lock` | 写出 `plans/issue-<id>/plan.md` 和 `tasks.md`，包含 task 文件、边界、命令、gate 和继续规则。 |
| `forma-execute` | 执行一个已接受任务，运行具体验证，并记录可审查的 proof。 |

`forma-showhand` 是 `forma-execute` 的连续执行 candy skill，不是独立阶段。review 完毕、方案固定后，它会在已锁定契约下继续推进已接受任务，直到阻塞出现才停止。

## 应该检查什么

真实运行后，检查：

- 生成的 skill bundle 和 `.forma-manifest.json`；
- `plans/issue-<id>/plan.md` 下的计划；
- `plans/issue-<id>/tasks.md` 下的可执行任务；
- 如果工作流记录运行过程，检查 `plans/issue-<id>/runs/` 下的运行证据；
- 验证命令、共享检查、gate 结果和 proof 路径；
- 如果 `forma-showhand` 无法继续，检查阻塞原因。

## 好结果应该看得见什么

一次好的运行应该让这些内容可见：

- 哪个需求来源被当作权威来源；
- Agent 规划前读了哪些证据；
- 哪些范围被接受；
- 已执行 task 的哪些文件和产物在边界内或边界外；
- 哪条具体命令或验证 gate 证明了结果；
- 为什么允许或阻止连续执行。

## 常见坏模式

- `forma-execute` 在 `forma-lock` 写出已接受任务前就开始实现。
- `forma-ground` 写文件或决定最终执行任务。
- 每个 skill 重复所有规则，而不是使用 stage constraints 和 references。
- 验证失败、证明缺失，或下一个已接受任务无法在当前计划内执行时，`forma-showhand` 仍继续执行。
- 生成 bundle 结构验证通过，但 profile 从未经过负责项目评审。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段门禁和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Profile Schema](./profile-schema.zh-CN.md)：sample profile 的源码格式。
- [Verifier](./verifier.zh-CN.md)：验证边界。
