# Workflow Contract

英文版：[workflow-contract.md](./workflow-contract.md)

Workflow contract 是 Forma 生成 workflow 的 task 执行形状。它定义 Agent 如何从一个具体开发目标走到证据、计划、有序任务、验证 gate、证明和 review。

Forma 把静态项目规则编译成 target 专用 skills。当这些 skills 被调用时，contract 就变成包住 Agent 工作路径的 harness。

## 实际作用

Forma 不保证 Agent 行为完美。它提供的是更清晰的工作流控制点。

| 只有提示词的工作流 | Forma workflow harness |
|---|---|
| 规则需要在每次对话里重新解释。 | 长期规则进入 profiles。 |
| 规划、取证和执行容易混在一起。 | 阶段会拆开澄清、取证、定稿、执行和继续。 |
| 验证可能到最后才想起来。 | 具体验证命令、共享检查和证明要求写进任务契约。 |
| 是否继续取决于 Agent 当下判断。 | `forma-showhand` 在已锁定计划下自动推进已接受任务。 |

## Contract 流程

Forma 默认方法使用四个核心对外 workflow skills，并带一个用于连续执行的 `forma-showhand`：

```text
goal -> proposal -> evidence -> execution contract -> ordered task -> proof
        plan        ground     lock                 execute
```

每个核心阶段只有一个职责：

| 对外技能 | 职责 | 交接物 |
|---|---|---|
| `forma-plan` | 澄清需求，并收敛成有边界的方案。 | 已收敛的决策门，或明确的阻塞 / 澄清状态。 |
| `forma-ground` | 只读收集仓库、Spec、文档和历史证据。 | 包含事实、风险和未知项的 grounding handoff。 |
| `forma-lock` | 把已收敛方案和证据变成执行契约。 | `plans/issue-<id>/plan.md` 和 `tasks.md`。 |
| `forma-execute` | 执行一个已接受任务，并记录证明。 | 可评审的任务结果和验证证据。 |

`forma-showhand` 是 `forma-execute` 的连续执行 candy skill，不是独立阶段。review 完毕、方案固定后，它会沿着已锁定任务列表继续推进，直到 proof、验证、权限或前置条件阻塞安全继续。

这些技能名是默认值。Profile 可以重命名生成技能，但工作流语义不变。

## 技能权限

Contract 有价值，是因为每个对外技能的权限不同。

| 对外技能 | 允许 | 不允许 |
|---|---|---|
| `forma-plan` | 澄清 goal、scope、approach、validation、plan strategy 和边界。 | 检查仓库、写计划文件或实现。 |
| `forma-ground` | 读取文件、检查仓库状态、产出 grounding。 | 写文件、运行会修改状态的命令、决定最终执行任务。 |
| `forma-lock` | 在决策已经收敛后写入已接受计划和任务契约。 | 编造缺失范围、跳过 grounding、扩大验收条件。 |
| `forma-execute` | 实现当前已接受任务，并运行对应验证。 | 执行未接受任务、重写计划、绕过评审门禁继续。 |
| `forma-showhand` | 从已锁定任务列表恢复执行，并逐项套用 `forma-execute`。 | 绕过缺失计划、缺失证明、权限不清或已阻塞路线。 |

## 小例子

请求：

```text
更新一个生成 schema 的 source。
```

Forma workflow 应该让这个请求按 contract 推进：

| 对外技能 | 发生什么 |
|---|---|
| `forma-plan` | 判断这个任务是否只能改 source、生成文件是否出界、完成前需要什么 proof。 |
| `forma-ground` | 读取 source schema、生成器入口、附近测试和现有生成文件策略。 |
| `forma-lock` | 写出带具体边界和命令的已接受任务，例如 `make generate-schema` 加 schema 验证 gate。 |
| `forma-execute` | 只修改已接受的 source/test 文件，运行 task 验证，并记录 generated diff 和命令输出作为 proof。 |

review 完毕、方案固定后，`forma-showhand` 可以继续推进已接受任务，直到证明、验证、权限或前置条件阻塞。

## 证据策略

Workflow contract 应说明 Agent 在行动前必须使用哪些证据。

常见证据规则包括：

- PRD、issue、spec、brief 等权威需求来源；
- 仓库文件和当前实现事实；
- 相关历史、运行证据或之前的计划；
- 验证命令和证明要求；
- 必要证据缺失时明确标出 unknown。

证据规则应该放在需要它的技能里。例如，来源读取通常属于 `forma-ground`；最终任务验证属于 `forma-lock` 和 `forma-execute`。

## 执行边界

执行边界用于防止 Agent 因顺手而扩大范围。

一份有用的 contract 会说明：

- 哪个任务已经被接受；
- 哪些文件或子系统在范围内；
- 哪些工作路线需要额外批准；
- 哪些具体命令或共享检查能证明结果；
- 生成输出、日志或运行证据应该写到哪里；
- 哪些情况必须停止自动继续。

宽泛规则不应该复制进每个 skill。稳定默认规则进 profile，阶段规则进 stage constraints，路线专用规则进 conditional overlays。

## 验证和证明

验证不只是命令列表，而是任务完成的证明路径。

`forma-lock` 应把验证预期写入任务契约。`forma-execute` 应先运行最窄的相关检查，再运行计划要求的共享门禁。`forma-showhand` 会重复这条已接受任务执行回路，而不是每个任务后都请求 review。

如果证明缺失、过期，或不属于当前已接受任务，contract 应让 Agent 停下或要求修正计划。

## Showhand

`forma-showhand` 是 `forma-execute` 连续执行的 candy skill。review 完毕、方案固定后，用它让 Agent 沿着已接受任务列表继续自动驾驶。

但它仍然只在现有 harness 能覆盖下一步时继续。遇到这些情况应该停止：

- `plan.md` 或 `tasks.md` 缺失、不完整或过期；
- 下一个任务未被接受；
- 当前改动需要新的决策边界；
- 验证失败或无法运行；
- 前置条件或权限不可用；
- 用户中断或要求评审。

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
