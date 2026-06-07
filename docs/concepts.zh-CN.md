# 核心概念

英文版：[concepts.md](./concepts.md)

这页解释 Forma 的心智模型和核心术语。建议先读 README，再读本页，最后再写大型 profile。

Agent 通常不是因为不会产出文字或修改文件而失败。它们更常失败在：这项工作应该怎样发生，其实没有被显式写出来。

Forma 放的就是“这类工作应该怎样发生”这一层。

## 变化

当 AI coding 进入日常工作后，项目里重要的资产不再只有代码。

Agent 遵守的 Spec、读取的证据、定稿的计划、接受的任务边界、执行后留下的证明，都会进入项目生命周期。如果这些东西是模糊的、散落的，或者只存在于一次对话里，Agent 的工作方式就会每次都变。

过去，团队的工程风格主要体现在架构、代码模式、测试习惯和评审标准里。Agent 进入流程后，团队风格也会体现在工作如何被委托：Agent 必须澄清什么、必须读什么、什么时候可以行动、什么时候必须停下，以及如何证明结果。

Forma 把这套 Agent 工作风格当成源码来处理。它给工作流规则一个长期位置，把规则编译成分阶段 skills，让这条工作回路可以被评审，而不是每次临场发挥。

## 编译器模型

Forma 是面向项目专属 Agent 工作流的编译器。

```text
workflow profile  ->  Forma compiler  ->  skill bundle
工作流源码              编译器              可安装产物
```

Profile 是源码。生成出来的 skill bundle 是可安装产物。Codex 和 Claude Code 是当前支持的 target。

Forma 不直接执行项目任务。它生成的是 Agent 执行任务时遵守的工作流。

## 三个层次

这三层需要分清：

| 层次 | 含义 |
|---|---|
| Forma 本体 | 生成器、CLI、verifier、creator builder、方法源码和 target adapter。 |
| 生成 bundle | 安装到 Codex 或 Claude Code 的工作流技能。 |
| Profile 和 temporary injection | 长期规则和一次性规则的输入层。 |

混淆这些层会导致判断错误。Profile 不是已安装技能。生成技能不是源码真相。Temporary injection 也不是长期团队策略，除非它被提升成经过评审的 profile。

## 五个核心概念

| 概念 | 含义 |
|---|---|
| Workflow contract | 从需求到证据、计划、执行、证明、继续的分阶段规则。 |
| Profile | 像项目源码一样被评审的长期工作流来源。 |
| Temporary injection | 一次性生成输入，用于不应意外变成长期策略的范围规则。 |
| Skill bundle | target 专用的编译产物，包含阶段技能、references、scripts 和 manifest。 |
| Target | 加载生成技能的 Agent 环境，目前是 Codex 或 Claude Code。 |

详细说明见 [Workflow Contract](./workflow-contract.zh-CN.md)、[Profile Schema](./profile-schema.zh-CN.md) 和 [Skill Bundle](./skill-bundle.zh-CN.md)。

## 默认工作流

默认方法是 Plan-First：

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

这些阶段名是默认值：

| 阶段 | 更直白的说法 | 职责 |
|---|---|---|
| `shape` | 澄清请求 | 把松散请求收敛成有边界的方案。 |
| `gauge` | 先读再动 | 收集仓库、Spec、文档和相关证据。 |
| `seal` | 锁定计划 | 把方案变成已接受的任务契约。 |
| `pour` | 在边界内执行 | 实现一个已接受任务，并记录证明。 |
| `flow` | 安全继续 | 从 sealed plan 继续，或在缺少证明时停下。 |

不习惯这些名字？它们是默认名，不是教条。项目可以重命名生成技能，但阶段语义保持不变。

## 为什么重要

Forma 的价值不是“帮你写代码”。它不直接写业务任务。

Forma 把团队反复强调的 AI 工作纪律，变成可版本化、可安装、可验证的工作流源码。它让 Agent 工作更容易做到：

- 可重复：长期规则有固定来源和生命周期；
- 分阶段：澄清、取证、规划、执行和证明不会混成一个提示词；
- 有边界：实现限制在已接受任务内；
- 可评审：评审者能看到从需求、证据、计划、执行到证明的路径；
- 可迁移：同一套工作流可以生成到支持的 target。

## 适用边界

当 AI Agent 已经进入重复工作，并且这类工作需要稳定的规划、证据、验证、证明和停止条件时，用 Forma。

AI coding 是最直接的场景，但不是唯一场景。研究、分析、出版、设计评审、客户交接、治理、运营等工作，只要有重复来源、边界、阶段和证明要求，也可能适合 Forma。

这些情况通常不需要 Forma：

- 几条 `AGENTS.md` 仓库规则已经够用；
- 一个可复用能力更适合作为单个自定义技能；
- 主要问题是组织需求和 Spec 事实；
- 任务没有稳定来源、没有明确边界、没有验收路径，也不需要复用。

Forma 可以和 Spec 工具、规划文档、`AGENTS.md`、通用技能创建器一起使用。那些层定义需求、本地上下文或能力；Forma 定义 Agent 如何按阶段使用它们。

## 第一次跑通

不要一开始就设计完美 profile。先用一个小 workflow 试手感。

1. 选择一个小 sample profile。
2. 生成 Codex 或 Claude Code skill bundle。
3. 验证生成结果。
4. 安装到一个 target。
5. 触发一个 Plan-First 任务。
6. 检查计划、任务契约、验证结果和执行证据。
7. 只把真正有用的规则沉淀进长期 profile。

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
