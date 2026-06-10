# 核心概念

英文版：[concepts.md](./concepts.md)

这页展开 README 的主线：Forma 把项目规则编译成专属 agent workflow，并通过 workflow skills 把规则落到每次任务的 task contract。

## Forma 解决什么

AGENTS.md、custom skill 或 Superpowers 可以给 agent 规则和流程。这个做法能减少直接开写，但仍然有缺口：计划可能没有把团队最关切的准则落到当前任务里。

Forma 补的是这一层。它让 agent 从项目文档、代码、测试和约定里梳理工程准则，再把这些准则编译成一组 workflow skills。任务开始后，这些 skills 要求 agent 先产出 task contract，把事实依据、修改边界、验证方式、proof 和停手条件写清楚。

## 一句话定制 Workflow

Forma 的轻量入口是先让 agent 用 `forma-creator` 临场定制，团队不用先写 YAML：

```text
用 forma-creator 给这个项目定制一套 workflow。
从文档和代码里挖掘工程准则，先整理给我看；我确认后再生成 workflow，并按提示安装。
```

这条路径里，准则先进入一次生成出来的可试用 workflow。它适合探索、试用、快速适配当前项目。

如果团队已经确定要长期维护这些规则，可以让 agent 用 Forma 起草 profile：

```text
用 Forma 从这个项目的文档和代码里提炼工程准则，给我一版 profile 草案。
```

profile 经过 review 后，再反复编译成 workflow 产物。

## 三层模型

Forma 把项目准则放进三层：

| 层 | 含义 |
|---|---|
| 项目准则 | 团队认可的做事方式：权威资料、修改边界、工具要求、验证深度、proof 和停手条件。 |
| Workflow 产物 | 安装给 agent 的 workflow skills，可以是 Codex / Claude Code skill bundle，也可以是 plugin。 |
| Task contract | agent 面对一个具体任务时写出的计划契约，记录到 `plans/issue-<id>/`。 |

临场定制时，项目准则进入本次生成的 workflow 产物。长期维护时，项目准则沉淀成 tracked profile，再由 Forma 编译成 workflow 产物。

## Profile vs Task Contract

Profile 不应该写死每个未来任务要改哪些文件、跑哪些命令。它描述长期准则：哪些证据更权威，哪些边界不能碰，哪些工具必须用，验证要到什么深度，什么情况必须停下来。

Task contract 是这些准则落到当前任务后的结果。到了这个阶段，agent 才会写清楚当前任务的证据、文件边界、任务顺序、验证命令、proof 路径和停手条件。

所以，示例里的具体命令和 task 顺序通常是 task contract 的结果，不是 profile 原文。Profile 决定计划必须按什么标准展开；task contract 说明这次任务具体怎么做。

## 编译模型

Forma 是把项目准则变成专属 agent workflow 的编译器。

```text
profile / temporary injection  ->  Forma compiler  ->  workflow output  ->  task contract
长期规则 / 临场规则                  编译器              安装产物              当前任务契约
```

Codex 和 Claude Code 是当前支持的 target。同一份 profile 可以生成不同 target 的产物，同时保持 task 级 workflow 语义不变。

Forma 不直接执行项目任务。它生成 agent 执行任务时遵守的 workflow skills。

## 默认 Workflow

默认 workflow 是“先计划、再执行”的形状：

```text
goal -> proposal -> evidence -> task contract -> task execution -> proof
```

四个核心 skills 管住 task contract 的生命周期：

| Skill | 作用 | 边界 |
|---|---|---|
| `forma-plan` | 把目标和项目准则对齐，形成 proposal。 | 不写文件，不执行任务。 |
| `forma-ground` | 按准则需要的事实取证。 | 只读，不决定最终任务。 |
| `forma-lock` | 写出 `plan.md` 和 `tasks.md`，锁定 task contract。 | 只落已接受方案。 |
| `forma-execute` | 执行一个已接受 task，运行验证，记录 proof。 | 不越过 task 边界，不绕过停手条件。 |

`forma-showhand` 是 `forma-execute` 的自动驾驶入口，不是第五个规划阶段。计划锁定后，它连续推进剩余已接受 tasks，直到阻塞、验证没通过或需要人介入。

项目可以重命名生成出来的 skills，但阶段语义应该保持不变。

## 三条路径

| 路径 | 适合 | 结果 |
|---|---|---|
| `forma-creator` | 临场定制，先试一套项目 workflow。 | 一次性 workflow 产物，可安装体验。 |
| `forma explain profile` + agent | 一开始就要长期维护的源码。 | tracked profile YAML，review 后再编译。 |
| `forma create-bundle` / `forma create-plugin` | 已经有 review 过的 profile。 | 确定性生成 workflow bundle 或 plugin。 |

三条路径都会走到已验证的 workflow 产物。区别在于：准则是临场进入一次性产物，还是长期进入 profile。

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

不要一开始就设计完美 profile。先让 `forma-creator` 临场定制一套可试用 workflow：

1. 安装 CLI 和 `forma-creator`。
2. 让 creator 从项目文档和代码里挖掘准则。
3. review 准则，补充缺口。
4. 生成并验证 workflow 产物。
5. 安装后触发 `forma-plan`。
6. 检查 task contract：事实、边界、任务顺序、验证和 proof。
7. 有用的规则再提升成 tracked profile。

具体路径见 [快速开始](./quick-start.zh-CN.md)。

## 继续阅读

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、门禁、边界、证据和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源格式。
- [Forma Creator](./forma-creator.zh-CN.md)：临场 workflow 生成和 temporary injection。
- [Verifier](./verifier.zh-CN.md)：验证器检查什么，以及不能证明什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [Examples](./examples.zh-CN.md)：sample profiles、生成基线和真实 runs。
- [使用说明](./usage.zh-CN.md)：命令参考和安装位置。
