# Workflow Contract

英文版：[workflow-contract.md](./workflow-contract.md)

Workflow contract 是项目准则落到当前任务后的计划契约。它回答的是：这次任务依据哪些事实、允许改什么、不能改什么、怎么验证、proof 留在哪里、什么情况必须停下来 review。

Forma 生成的 workflow 安装到 agent 后，会推动 agent 从目标走到 proposal、证据、task contract、执行和 proof。重点不只是“先写计划”，而是计划必须按项目最关切的准则展开。

## 实际作用

很多通用 workflow 会要求 agent 先说明准备怎么做。Forma contract 继续往前走一步：让这份计划变成可以按项目准则审查的任务契约。

| 通用先计划流程 | Forma workflow contract |
|---|---|
| 计划说明大致步骤。 | contract 说明当前任务适用哪些项目准则。 |
| 证据读取容易靠 agent 自觉。 | contract 写清楚权威来源和必须确认的事实。 |
| 边界常常停在“我会小心”。 | contract 写清楚允许触碰和必须停手的边界。 |
| 验证可能只是命令列表。 | contract 说明验证为什么足以证明当前 task。 |
| 继续执行依赖当下判断。 | `showhand` 只在已锁定 task 和停手条件允许时继续。 |

Forma 不保证 agent 行为完美。它提供的是更清楚的控制面：contract、验证和 proof 留下来，reviewer 可以检查。

## Contract 流程

默认 workflow 使用四个核心 skills 管住 contract 生命周期，并带一个连续执行入口：

```text
goal -> proposal -> evidence -> task contract -> accepted task -> proof
        plan        ground     lock             execute
```

| 阶段 | 职责 | 交接物 |
|---|---|---|
| `plan` | 把目标和项目准则对齐，形成 proposal。 | 已收敛的方向，或明确的阻塞 / 澄清状态。 |
| `ground` | 按准则要求只读收集证据。 | 包含事实、风险、未知项的 grounding handoff。 |
| `lock` | 把已接受方案写成 task contract。 | `plans/issue-<id>/plan.md` 和 `tasks.md`。 |
| `execute` | 执行一个已接受 task，运行验证，记录 proof。 | 可 review 的任务结果和验证证据。 |

`showhand` 是 `execute` 的自动驾驶入口。计划锁定后，它连续推进剩余已接受 tasks，直到阻塞、验证没通过或需要人介入。

这些阶段名是默认值。Plugin 用 `forma:plan` 这类 `forma:*`，direct skill bundle 用 `forma-plan` 这类 `forma-*` skill。Profile 或 creator 可以改生成名，但阶段语义应该保持不变。

## 技能边界

Contract 有价值，是因为每个阶段的权限不同。

| 阶段 | 允许 | 不允许 |
|---|---|---|
| `plan` | 澄清 goal、scope、approach、validation、plan strategy 和边界。 | 检查仓库、写计划文件或实现。 |
| `ground` | 读取文件、检查仓库状态、产出 grounding。 | 写文件、运行会修改状态的命令、决定最终执行任务。 |
| `lock` | 在方案已经收敛后写入已接受计划和任务契约。 | 编造缺失范围、跳过 grounding、扩大验收条件。 |
| `execute` | 实现当前已接受 task，并运行对应验证。 | 执行未接受 task、重写计划、绕过评审门禁继续。 |
| `showhand` | 从已锁定任务列表恢复执行，并逐项套用 `execute`。 | 绕过缺失计划、缺失证明、权限不清或已阻塞路线。 |

## 读一个 Task Contract

请求：

```text
更新 settings schema source，并刷新生成出来的 API 文档。
```

如果项目最关切的是“生成文件必须可追溯，API contract 变更必须先 review”，task contract 应该把这些准则落到当前任务里：

```text
Focus: 先确认 schema source 和 API contract 影响，再刷新 generated docs。
Evidence: settings schema source；generator entrypoint；API contract policy；nearby schema tests.
Tasks:
  1. impact-check: 判断 contract 变化是 none / additive / breaking。
  2. source-change: 只改 schema source 和必要测试。
  3. generated-proof: 运行 generator，记录 generated diff 来源。
Boundary: 不直接手改 generated docs；breaking 影响未确认前不进入实现。
Validate: schema test；generator command；generated diff check。
Proof: 写入 `plans/issue-<id>/runs/`，包含命令和 generated diff 摘要。
Stop if: contract 影响需要 API review；
         generator 无法复现 generated docs；
         需要修改当前 task 之外的共享 schema 基础设施。
```

这里的命令、任务顺序和停手条件是当前 task contract 的结果。Profile 或 creator 提供的是审查标准：事实来源、生成物追溯、API review 和 proof 要求。

## 证据策略

Workflow contract 应说明 agent 在行动前必须使用哪些证据。

常见证据规则包括：

- PRD、issue、spec、brief 等权威需求来源；
- 仓库文件和当前实现事实；
- 相关历史、运行证据或之前的计划；
- 验证命令和证明要求；
- 必要证据缺失时明确标出 unknown。

证据规则应该放在需要它的阶段里。例如，来源读取通常属于 `ground`；最终任务验证属于 `lock` 和 `execute`。

## 执行边界

执行边界用于防止 agent 因顺手而扩大范围。

一份有用的 contract 会说明：

- 哪个 task 已经被接受；
- 哪些文件或子系统在范围内；
- 哪些工作路线需要额外批准；
- 哪些具体命令或共享检查能证明结果；
- 生成输出、日志或运行证据应该写到哪里；
- 哪些情况必须停止自动继续。

宽泛规则不应该复制进每个 skill。稳定默认规则进 profile，阶段规则进 stage constraints，路线专用规则进 conditional overlays。

## 验证和证明

验证不只是命令列表，而是任务完成的证明路径。

`lock` 应把验证预期写入 task contract。`execute` 应先运行最窄的相关检查，再运行计划要求的共享门禁。`showhand` 会重复这条已接受 task 执行回路。

如果证明缺失、过期，或不属于当前已接受 task，contract 应让 agent 停下或要求修正计划。

## Showhand

`showhand` 是 `execute` 连续执行的自动驾驶入口。review 完毕、方案固定后，用它让 agent 沿着已接受任务列表继续推进。

它仍然只在现有 contract 能覆盖下一步时继续。遇到这些情况应该停止：

- `plan.md` 或 `tasks.md` 缺失、不完整或过期；
- 下一个 task 未被接受；
- 当前改动需要新的决策边界；
- 验证没通过或无法运行；
- 前置条件或权限不可用；
- 用户中断或要求 review。

## Profile 如何影响 Contract

Profile 不替代 contract。Profile 维护长期准则；contract 把这些准则落到当前任务。

Profile 适合添加：

- 长期权威来源规则；
- 目标技能名和展示名；
- 阶段约束；
- 验证命令；
- 按阶段选择的 references 和 scripts；
- docs-only、migration、generated-baseline、governance、backend、cross-layer 等路线的 conditional overlays。

Temporary injection 适合只影响本次生成产物的临场准则。

## 相关文档

- [核心概念](./concepts.zh-CN.md)：编译器模型和核心术语。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源格式。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Examples](./examples.zh-CN.md)：sample profiles、本地生成说明和真实 runs。
- [使用说明](./usage.zh-CN.md)：命令参考。
