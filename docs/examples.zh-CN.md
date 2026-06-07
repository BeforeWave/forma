# Examples

英文版：[examples.md](./examples.md)

这一页展示一个端到端 Forma workflow 应该长什么样。

下面是说明性示例，不是真实 Agent 运行记录。要生成并运行真实 sample bundle，请看 [快速开始](./quick-start.zh-CN.md)。

## 真实 Sample Source

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
forma create \
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

Forma 生成的 workflow 应该让这个请求按 contract 阶段推进，而不是直接跳到实现。

## 阶段示例

| 阶段 | 预期推进方式 |
|---|---|
| `shape` | 澄清 goal、scope、approach、validation、plan strategy，并判断是否使用 issue source adapter。 |
| `gauge` | 只检查已接受范围需要的仓库和来源材料。分离事实、风险、未知项和建议。 |
| `seal` | 写出 `plans/issue-<id>/plan.md` 和 `tasks.md`，包含已接受任务、验证和继续边界。 |
| `pour` | 执行一个已接受任务，运行验证，并记录评审证明。 |
| `flow` | 只有 sealed plan 允许且证明仍然清楚时才继续；否则停下。 |

## 应该检查什么

真实运行后，检查：

- 生成的 skill bundle 和 `.forma-manifest.json`；
- `plans/issue-<id>/plan.md` 下的计划；
- `plans/issue-<id>/tasks.md` 下的可执行任务；
- workflow 记录时，`plans/issue-<id>/runs/` 下的运行证据；
- 验证命令和结果；
- 如果 `flow` 拒绝继续，检查停止原因。

## 好结果应该看得见什么

一次好的运行应该让这些内容可见：

- 哪个需求来源被当作权威来源；
- Agent 规划前读了哪些证据；
- 哪些范围被接受；
- 执行的是哪个任务；
- 哪个验证证明了结果；
- 为什么允许或阻止继续。

## 常见坏模式

- `pour` 在 `seal` 写出已接受任务前就开始实现。
- `gauge` 写文件或决定最终执行任务。
- 每个 skill 重复所有规则，而不是使用 stage constraints 和 references。
- validation 失败或 plan 没有继续权限时，`flow` 仍继续执行。
- 生成 bundle 结构验证通过，但 profile 从未被负责团队评审。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段门禁和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Profile Schema](./profile-schema.zh-CN.md)：sample profile 的源码格式。
- [Verifier](./verifier.zh-CN.md)：验证边界。
