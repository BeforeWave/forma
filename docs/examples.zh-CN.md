# Examples

英文版：[examples.md](./examples.md)

这一页展示 Forma runtime harness 在一个端到端开发目标里应该让哪些东西变得可见。

下面是说明性示例，不是真实 Agent 运行记录。要生成并运行真实示例 bundle，请看 [快速开始](./quick-start.zh-CN.md)。

## 已提交的 Sample 来源

从已提交的 backend sample profile 开始：

```text
examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml
```

它为两个支持的 target 生成了已提交基线：

```text
examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
```

## 生成 Bundle

```bash
forma create-bundle \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

把生成出来的阶段技能安装到对应 target。见 [Targets](./targets.zh-CN.md)。

## 示例请求

```text
Update the issue-tracked backend behavior described by issue 123.
```

Forma 生成的 workflow 应该让这个请求沿着 runtime harness 推进，而不是直接跳到实现。

## 技能示例

| 技能 | 预期推进方式 |
|---|---|
| `forma-plan` | 澄清目标、范围、方案、验证方式和计划策略，并判断是否使用 issue source adapter。 |
| `forma-ground` | 只检查已接受范围需要的仓库和来源材料。分离事实、风险、未知项和建议。 |
| `forma-lock` | 写出 `plans/issue-<id>/plan.md` 和 `tasks.md`，包含已接受任务、验证和继续边界。 |
| `forma-execute` | 执行一个已接受任务，运行验证，并记录可审查的证明。 |
| `forma-showhand` | review 完毕、方案固定后，用连续 `forma-execute` 推进已接受任务。 |

## 应该检查什么

真实运行后，检查：

- 生成的 skill bundle 和 `.forma-manifest.json`；
- `plans/issue-<id>/plan.md` 下的计划；
- `plans/issue-<id>/tasks.md` 下的可执行任务；
- 如果工作流记录运行过程，检查 `plans/issue-<id>/runs/` 下的运行证据；
- 验证命令和结果；
- 如果 `forma-showhand` 无法继续，检查阻塞原因。

## 好结果应该看得见什么

一次好的运行应该让这些内容可见：

- 哪个需求来源被当作权威来源；
- Agent 规划前读了哪些证据；
- 哪些范围被接受；
- 执行的是哪个任务；
- 哪个验证证明了结果；
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
