# 核心概念

英文版：[concepts.md](./concepts.md)

这页展开 README 里的三层模型。建议先读首页定位，再读本页，最后再写长期 profile。

Agent 通常不是因为不会产出文字或修改文件而失败。它们更常失败在：这个项目希望它怎样工作，其实没有被显式写出来。

Forma 做的是把这套工作方式编译成 workflow harness。

## 变化是什么

当 AI coding 进入日常工作后，项目里重要的资产不再只有代码。

Agent 遵守的 Spec、读取的证据、定稿的计划、接受的任务边界、执行后留下的证明，都会进入项目生命周期。如果这些东西是模糊的、散落的，或者只存在于一次对话里，Agent 的工作方式就会每次都变。

过去，项目的工程风格主要体现在架构、代码模式、测试习惯和评审标准里。Agent 进入流程后，项目也需要表达工作如何被委托：Agent 必须澄清什么、必须读什么、什么时候可以行动、什么时候必须停下，以及如何证明结果。

Forma 把这套 Agent 工作方式当成源码来处理。它把静态项目规则编译成分阶段 skills，再让这些 skills 在具体开发目标出现时落成 task 级文件、边界、命令、验证 gate 和 proof。

## 任务工作流编译

Forma 先从 AI coding 开始，因为软件任务容易检查：source 文件、生成文件、测试、命令、diff 和 review proof 都很清楚。

同一个模型也可以用于其他重复工作。只要一类任务有来源、边界、验证和 proof，就可以生成自己的 workflow。

不同任务验证的东西不同：

- coding 检查测试、生成结果和 diff；
- research 检查来源、结论和引用；
- analysis 检查数据假设、计算和输出；
- operations 检查 runbook、安全 gate 和执行日志。

## 生成式 Workflow vs 固定 Workflow

固定 workflow 给每个项目同一套流程。

Forma 从项目或任务自己的规则生成 workflow。

| 固定 workflow | Forma 生成的 workflow |
|---|---|
| 安装一套预设流程。 | 从项目自己的规则编译 workflow。 |
| 到处使用同一种验证方式。 | 让验证方式匹配任务类型。 |
| 把项目规则当作额外说明。 | 把项目规则变成阶段、边界、gate 和 proof。 |

## 三层工作

Forma 分三层工作：

| 层 | 含义 |
|---|---|
| Layer 0：项目规则 | 定义长期规则：代码约定、修改边界、验证要求、review 预期、生成文件策略、高风险区域和证据来源。 |
| Layer 1：Workflow harness | Forma 把这些规则编译成项目专属 Plan-First skill bundle 或 Codex plugin。 |
| Layer 2：任务级执行 | 已安装 workflow 把具体开发目标变成 task 级义务：文件、边界、命令、gate 和 proof。 |

这三层需要分清。Profile 不是已安装 skill。生成出来的 skill bundle 不是源码真相。Workflow harness 也不是另一个文件，而是已安装 workflow 在 Agent 执行具体目标时发挥作用的方式。

## 编译器模型

Forma 是面向项目专属 Plan-First workflow skills 的编译器。

```text
profile  ->  Forma compiler  ->  workflow bundle/plugin  ->  task 执行契约
源码          编译器              安装产物                    文件、命令、gate、proof
```

Codex 和 Claude Code 是当前支持的 target。同一份 profile 可以生成不同 target 的产物，同时保持 workflow contract 不变。

Forma 不直接执行项目任务。它生成的是 Agent 执行任务时遵守的 skills。

## 五个核心概念

| 概念 | 含义 |
|---|---|
| Workflow contract | 从需求到证据、计划、task 执行、证明和 review 的分阶段规则。 |
| Profile | 像项目源码一样被评审的长期项目规则来源。 |
| Temporary injection | 一次性生成输入，用于不应意外变成长期策略的范围规则。 |
| Skill bundle | target 专用的编译产物，包含阶段技能、references、scripts 和 manifest。 |
| Target | 加载生成技能的 Agent 环境，目前是 Codex 或 Claude Code。 |

详细说明见 [Workflow Contract](./workflow-contract.zh-CN.md)、[Profile Schema](./profile-schema.zh-CN.md) 和 [Skill Bundle](./skill-bundle.zh-CN.md)。

## 默认工作流

默认方法是 Plan-First：

```text
clarify -> gather evidence -> lock plan -> execute task
plan    -> ground         -> lock      -> execute
```

这些对外技能名是默认值：

| 默认技能 | 更直白的说法 | 职责 |
|---|---|---|
| `forma-plan` | 澄清请求 | 把松散请求收敛成有边界的方案。 |
| `forma-ground` | 先读再动 | 收集仓库、Spec、文档和相关证据。 |
| `forma-lock` | 锁定计划 | 把方案变成已接受的任务契约。 |
| `forma-execute` | 在边界内执行 | 实现一个已接受任务，并记录证明。 |

`forma-showhand` 是 `forma-execute` 连续执行的 candy skill：review 完毕、方案固定后，用它让 Agent 在同一套 harness 下继续推进已接受任务。

不习惯上面的对外名字？它们是默认名，不是教条。项目可以重命名生成技能，但阶段语义保持不变。

## 为什么重要

Forma 的价值不是“帮你写代码”。它不直接写业务任务。

Forma 把项目专属的 Agent 工作纪律，变成可版本化、可安装、可验证的工作流源码。它让 Agent 工作更容易做到：

- 可重复：长期规则有固定来源和生命周期；
- 分阶段：澄清、取证、规划、执行和证明不会混成一个提示词；
- 有边界：实现限制在已接受 task 的文件和修改边界内；
- 具体：验证被写成具体命令、gate 和 proof 路径，而不是泛泛提醒；
- 可评审：评审者能看到从需求、证据、计划、task 执行到证明的路径；
- 可迁移：同一份 profile 可以生成到支持的 target。

## 适用边界

当项目的长期规则需要影响 Agent 如何执行具体开发任务时，用 Forma。

AI coding 是最直接的场景，但不是唯一场景。研究、分析、出版、设计评审、客户交接、治理、运营等工作，只要有重复来源、边界、阶段和证明要求，也可能适合 Forma。

这些情况通常不需要 Forma：

- 几条本地项目规则已经够用；
- 一个可复用能力更适合作为单个自定义技能；
- 主要问题是组织需求和 Spec 事实；
- 任务没有稳定来源、没有明确边界、没有验收路径，也不需要复用。

Forma 可以和 Spec 工具、规划文档、项目说明、通用技能创建器一起使用。那些层定义需求、本地上下文或能力；Forma 定义 Agent 如何按阶段使用它们，以及最终留下什么 proof。

## 第一次跑通

不要一开始就设计完美 profile。先用一个小 workflow 试手感。

1. 安装 CLI。
2. 生成默认 Codex plugin，或一个小的 target bundle。
3. 安装到一个 target。
4. 触发一个 Plan-First 任务。
5. 检查 task 契约：文件、边界、命令、验证 gate 和 proof。
6. 等 workflow 证明有用后，再用 creator 或 profile 塑造 harness。

具体路径见 [快速开始](./quick-start.zh-CN.md)。

## 继续阅读

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、门禁、边界、证据和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源格式。
- [Forma Creator](./forma-creator.zh-CN.md)：一次性 workflow 生成。
- [Verifier](./verifier.zh-CN.md)：验证器检查什么，以及不能证明什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [Examples](./examples.zh-CN.md)：端到端 workflow 示例。
- [使用说明](./usage.zh-CN.md)：命令参考和安装位置。
