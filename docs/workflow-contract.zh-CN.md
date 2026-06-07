# Workflow Contract

英文版：[workflow-contract.md](./workflow-contract.md)

Workflow contract 定义 Agent 如何从需求走到证据、从证据走到计划、从计划走到执行，再从执行走到继续。

Forma 把这份 contract 编译成 target 专用技能。输出不是一个更好的 prompt，而是一条带阶段、门禁、边界和证明要求的工作回路。

## 实际作用

Forma 不保证 Agent 行为完美。它提供的是更清晰的工作流控制点。

| 只有提示词的工作流 | Forma 的工作流控制点 |
|---|---|
| 规则需要在每次对话里重新解释。 | 长期规则进入 profiles。 |
| 规划、取证和执行容易混在一起。 | 阶段会拆开澄清、取证、定稿、执行和继续。 |
| 验证可能到最后才想起来。 | 证明要求写进任务契约。 |
| 是否继续取决于 Agent 当下判断。 | `flow` 有明确停止条件。 |

## Contract 流程

Forma 默认方法使用五个阶段：

```text
demand -> proposal -> evidence -> plan -> task -> proof -> continuation
          shape       gauge      seal    pour    pour     flow
```

每个阶段只有一个核心职责：

| 阶段 | 职责 | 交接物 |
|---|---|---|
| `shape` | 澄清需求，并收敛成有边界的方案。 | 已收敛的决策门，或明确的阻塞 / 澄清状态。 |
| `gauge` | 只读收集仓库、Spec、文档和历史证据。 | 包含事实、风险和未知项的 grounding handoff。 |
| `seal` | 把已收敛方案和证据变成执行契约。 | `plans/issue-<id>/plan.md` 和 `tasks.md`。 |
| `pour` | 执行一个已接受任务，并记录证明。 | 可评审的任务结果和验证证据。 |
| `flow` | 只有 sealed plan 允许时，才继续执行已接受任务。 | 已完成任务，或明确停止原因。 |

阶段名是默认值。Profile 可以重命名生成技能，但 contract 阶段语义不变。

## 阶段权限

Contract 有价值，是因为每个阶段的权限不同。

| 阶段 | 允许 | 不允许 |
|---|---|---|
| `shape` | 澄清 goal、scope、approach、validation、plan strategy 和边界。 | 检查仓库、写计划文件或实现。 |
| `gauge` | 读取文件、检查仓库状态、产出 grounding。 | 写文件、运行会修改状态的命令、决定最终执行任务。 |
| `seal` | 在决策已经收敛后写入已接受计划和任务契约。 | 编造缺失范围、跳过 grounding、扩大验收条件。 |
| `pour` | 实现当前已接受任务，并运行对应验证。 | 执行未接受任务、重写计划、绕过评审门禁继续。 |
| `flow` | 在允许继续时，从 sealed task list 恢复执行。 | 绕过缺失计划、缺失证明、权限不清或已阻塞路线。 |

## 小例子

请求：

```text
Update the billing API behavior.
```

Forma workflow 应该让这个请求按 contract 推进：

| 阶段 | 发生什么 |
|---|---|
| `shape` | 判断这是否改变 public API 行为、持久化或兼容性预期。 |
| `gauge` | 读取当前 routes、API docs、tests，以及相关历史 plan 或 issue 证据。 |
| `seal` | 写出带验证的已接受任务，例如 API tests、兼容性检查或 contract review。 |
| `pour` | 执行一个已接受任务，并运行该任务要求的证明。 |
| `flow` | 只有 sealed plan 允许时继续；如果出现新的 API contract 决策，就停下。 |

## 证据策略

Workflow contract 应说明 Agent 在行动前必须使用哪些证据。

常见证据规则包括：

- PRD、issue、spec、brief 等权威需求来源；
- 仓库文件和当前实现事实；
- 相关历史、运行证据或之前的计划；
- 验证命令和证明要求；
- 必要证据缺失时明确标出 unknown。

证据规则应该放在需要它的阶段。例如，来源读取通常属于 `gauge`；最终任务验证属于 `seal` 和 `pour`。

## 执行边界

执行边界用于防止 Agent 因顺手而扩大范围。

一份有用的 contract 会说明：

- 哪个任务已经被接受；
- 哪些文件或子系统在范围内；
- 哪些工作路线需要额外批准；
- 哪些命令能证明结果；
- 哪些情况必须停止自动继续。

宽泛规则不应该复制进每个 skill。稳定默认规则进 profile，阶段规则进 stage constraints，路线专用规则进 conditional overlays。

## 验证和证明

验证不只是命令列表，而是任务完成的证明路径。

`seal` 应把验证预期写入任务契约。`pour` 应先运行最窄的相关检查，再运行计划要求的共享门禁。`flow` 只有在已接受任务和证明要求仍然清楚时才能继续。

如果证明缺失、过期，或不属于当前已接受任务，contract 应让 Agent 停下或要求修正计划。

## 继续规则

`flow` 不是“无论如何继续”，而是受控继续。

遇到这些情况应该停止：

- `plan.md` 或 `tasks.md` 缺失、不完整或过期；
- 下一个任务未被接受；
- 当前改动需要新的决策边界；
- 验证失败或无法运行；
- 计划没有允许当前路线自动继续；
- 用户中断或要求 review。

## Profile 如何影响 Contract

Profile 不替代 contract，而是让 contract 专门化。

Profile 适合添加：

- 长期权威来源规则；
- 目标技能名和展示名；
- 阶段约束；
- 验证命令；
- 按阶段选择的 references 和 scripts；
- docs-only、migration、generated-baseline、governance、backend、cross-layer 等路线的 conditional overlays。

一次性注入适合只影响本次生成套件的临时约束。

## 相关文档

- [核心概念](./concepts.zh-CN.md)：编译器模型和核心术语。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源格式。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Examples](./examples.zh-CN.md)：说明性端到端示例。
- [使用说明](./usage.zh-CN.md)：命令参考。
