# 核心概念

英文版：[concepts.md](./concepts.md)

这页展开 README 的主线：Forma 把项目规则变成专属 agent workflow，并通过 workflow skills 把规则落到每次任务的 task contract。

## Forma 解决什么

AGENTS.md、custom skill 或 Superpowers 可以给 agent 规则和流程。这个做法能减少直接开写，但仍然有缺口：计划可能没有把团队最关切的准则落到当前任务里。

Forma 补的是这一层。它让 agent 从项目文档、代码、测试和约定里梳理工程准则，再把这些准则变成一组 workflow skills。任务开始后，这些 skills 要求 agent 先产出 task contract，把事实依据、修改边界、验证方式、proof 和停手条件写清楚。

## 一句话生成 Workflow

轻量入口是让 agent 先提炼项目规则，确认后生成 workflow：

```text
用 Forma 给这个项目生成一套 Codex workflow。
先把你提炼出的项目规则给我看；确认后再生成并安装。
```

agent 会把提炼出的规则整理成 profile。profile 可以只是临时生成输入；如果这些规则要团队共用或长期维护，再把它提交进仓库。

## 三层模型

Forma 把项目准则放进三层：

| 层 | 含义 |
|---|---|
| Profile | 从项目里提炼出的工程规则说明：阶段约束、工具习惯、验证、proof 和停手条件。 |
| Workflow 产物 | 按 profile 生成并安装给 agent 的 workflow skills，可以是 skill bundle 或 plugin。 |
| Task contract | agent 面对一个具体任务时写出的计划契约，记录到 `plans/issue-<id>/`。 |

临时试用时，profile 可以只是本地临时文件。长期维护时，profile 进入版本控制，后续由 Forma 反复生成 workflow 产物。

## Profile vs Task Contract

Profile 不应该写死每个未来任务要改哪些文件、跑哪些命令。它描述工程准则：哪些证据更权威，哪些边界不能碰，哪些工具必须用，验证要到什么深度，什么情况必须停下来。

Task contract 是这些准则落到当前任务后的结果。到了这个阶段，agent 才会写清楚当前任务的证据、文件边界、任务顺序、验证命令、proof 路径和停手条件。

所以，示例里的具体命令和 task 顺序通常是 task contract 的结果，不是 profile 原文。Profile 决定计划必须按什么标准展开；task contract 说明这次任务具体怎么做。

## 生成模型

Forma 把 profile 里的项目规则变成专属 agent workflow。

```text
profile  ->  Forma generator  ->  workflow output  ->  task contract
项目规则      生成器                 安装产物              当前任务契约
```

Codex、Claude Code 和 OpenCode 是当前支持的 skill-bundle target。同一份 profile 可以生成不同 target 的产物，同时保持 task 级 workflow 语义不变。

Forma 不直接执行项目任务。它生成 agent 执行任务时遵守的 workflow skills。

## 默认 Workflow

默认 workflow 是“先计划、再执行”的形状：

```text
goal -> proposal -> evidence -> task contract -> task execution -> proof
```

四个核心阶段管住 task contract 的生命周期：

| 阶段 | 作用 | 边界 |
|---|---|---|
| `plan` | 把目标和项目准则对齐，形成 proposal。 | 不写文件，不执行任务。 |
| `ground` | 按准则需要的事实取证。 | 只读，不决定最终任务。 |
| `lock` | 写出 `plan.md` 和 `tasks.md`，锁定 task contract。 | 只落已接受方案。 |
| `execute` | 执行一个已接受 task，运行验证，记录 proof。 | 不越过 task 边界，不绕过停手条件。 |

`showhand` 是 `execute` 的自动驾驶入口，不是第五个规划阶段。计划锁定后，它连续推进剩余已接受 tasks，直到阻塞、验证没通过或需要人介入。

触发名取决于安装形态：plugin 用 `forma:plan` 这类 `forma:*`，direct skill bundle 用 `forma-plan` 这类 `forma-*` skill。项目可以重命名生成出来的 skills，但阶段语义应该保持不变。

## 三条路径

| 路径 | 适合 | 结果 |
|---|---|---|
| `forma explain profile` + agent | 从项目规则生成 workflow；profile 可临时，也可长期维护。 | profile + 已验证 workflow 产物。 |
| `forma build bundle` / `forma build plugin` | 已经有 review 过的 profile。 | 确定性生成 workflow bundle 或 plugin。 |
| `forma-creator` | 可选临场路径，不想先处理 profile 文件时使用。 | 一次性 workflow 产物，可安装体验。 |

三条路径都会走到已验证的 workflow 产物。默认理解是：规则先被整理成 profile；是否长期保存，由你决定。

## 为什么边界和 Proof 重要

Forma 的价值在于把项目准则写进 agent 的工作路径：

- 哪些事实必须先确认；
- 哪些边界不能碰；
- 哪些验证才能证明结果；
- proof 记录在哪里；
- 什么情况必须停下来 review。

这些内容进入 task contract 后，reviewer 审的就不只是 patch，还包括 agent 是不是按项目认可的准则完成了规划、取证、验证和证明。

这仍然不是行为保证。模型和宿主环境仍然会影响 agent 是否完全遵守。Forma 提供的是更清楚的控制面：workflow、task contract 和 proof 都留下来，具体任务可以被检查。

## 适用边界

当项目的工程准则需要影响 agent 如何执行具体任务时，用 Forma。

AI coding 是最直接的场景，但不是唯一场景。研究、分析、运营、治理、发布、客户交接等工作，只要有稳定来源、边界、阶段、验证和 proof，也可以用类似方式生成 workflow。

这些情况通常不需要 Forma：

- 几条本地规则已经够用；
- 一个可复用能力更适合作为单个自定义 skill；
- 主要问题是需求或事实来源本身还没定；
- 任务没有稳定来源、边界、验收路径，也不需要复用。

Forma 可以和 Spec 工具、规划文档、项目说明、通用 skill creator 一起使用。那些层定义需求、本地上下文或能力；Forma 定义 agent 如何按阶段使用它们，以及最终留下什么 proof。

## 第一次跑通

不要一开始就设计完美 profile。先生成一套可试用 workflow：

1. 安装 CLI。
2. 让 agent 从项目文档和代码里挖掘准则。
3. review 准则，补充缺口。
4. 生成并验证 workflow 产物。
5. 安装后，plugin 产物触发 `forma:plan`；direct skill bundle 触发对应的 `forma-*` skill。
6. 检查 task contract：事实、边界、任务顺序、验证和 proof。
7. 有用的 profile 再提交进版本控制。

具体路径见 [快速开始](./quick-start.zh-CN.md)。

## 继续阅读

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、门禁、边界、证据和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：profile 如何描述阶段约束、工具习惯、验证和 proof。
- [Forma Creator](./forma-creator.zh-CN.md)：可选临场路径和 temporary injection。
- [Verifier](./verifier.zh-CN.md)：验证器检查什么，以及不能证明什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [Examples](./examples.zh-CN.md)：sample profiles、本地生成说明和真实 runs。
- [使用说明](./usage.zh-CN.md)：命令参考和安装位置。
