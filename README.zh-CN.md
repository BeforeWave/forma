<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**一句话定制项目 workflow，让 agent 按团队准则规划、验证和交付。**

Coding agent 在真实项目里出问题，通常不是不会写代码，而是还没把团队的交付规则落到当前任务，就开始实现。

很多团队已经有 agent-facing docs，也会接入通用的“先计划、再执行”工作流。它们能让 agent 读规则、按阶段写计划，但固定流程不等于团队准则；计划仍然可能缺少当前任务可以依赖和验证的约束细节。

Forma 做的就是把这层缺口补上。你可以直接告诉 agent：

```text
请用 forma CLI 为这个项目定制 workflow：从文档和代码里挖掘工程准则，生成后给我使用。
```

此时 Forma 会先帮团队理清最关切的实践准则，再生成守护这些准则的 workflow。这个 workflow 会盯住 agent 的规划、验证、proof 和停手条件，让当前任务按团队准则推进。

---

## Forma 怎么做

Forma 不直接替 agent 做项目任务；它把项目准则变成 agent 会遵守的 workflow。安装后，workflow 会先要求 agent 写 task contract，再进入取证、实现、验证和 proof 记录。

这些准则会进入三层载体：

- `profile`：团队认可的实践准则，进入版本控制，后续可以 review 和维护。
- `workflow 产物`：安装到 agent 的工作流，可以是 Codex / Claude Code skill bundle，也可以是 Codex plugin。
- `task contract`：agent 面对具体任务时生成的计划契约，记录到 `plans/issue-<id>/`。

默认 workflow 用四个核心 skills 管住 task contract 的生命周期：

| Skill | 作用 |
|---|---|
| `forma-plan` | 把目标和项目准则对齐，形成可 review 的 proposal；不写文件，不执行任务。 |
| `forma-ground` | 按准则需要的事实取证，只读代码、文档、issue、测试等资料。 |
| `forma-lock` | 把已接受的方案写成 `plan.md` 和 `tasks.md`，锁定 task contract。 |
| `forma-execute` | 执行一个已接受 task，跑验证，记录 proof，需要 review 时停。 |

`forma-showhand` 是 `forma-execute` 的自动驾驶入口：计划已经锁定后，它连续推进剩余 tasks，直到遇到阻塞、验证没通过或需要人介入。

团队后续调整 profile，就等于调整 workflow 守护哪些准则；重新生成 bundle 或 plugin 后，agent 会按新的约束规划和执行。

---

## 开始使用

`forma-creator` 是最轻入口：你用自然语言让 agent 读项目、提炼规则，并生成一套个人可用的 workflow。需要团队 review、持续迭代规则时，再走 `forma CLI + profile`。

个人使用：

```text
用 forma-creator 给这个项目定制一套 workflow。
先整理关键规则给我看；确认后生成并按提示安装。
```

团队长期维护时，先准备 profile：

```text
用 forma CLI 为这个项目准备长期 profile：
基于项目事实给我一版 profile 草案；我确认后，再生成、验证并安装 Codex workflow。
```

安装完成后，新开 thread 触发生成的 workflow：

```text
Use forma-plan to plan this issue first.

Issue:
<你的任务或 issue>
```

正常的第一步是 proposal，而不是 patch。如果 agent 直接改文件，说明 workflow 没有加载成功，或者没有被触发。

Codex skill bundle、Claude Code 和安装位置细节见 [Quick Start](./docs/quick-start.zh-CN.md) 和 [Usage](./docs/usage.zh-CN.md)。

---

## 同一个目标，不同团队的过关标准

同样是给 settings 增加 rate limiting，普通计划可能只写：读相关代码、加 limiter、跑测试。Forma 生成的 workflow 会带着团队原则，让 agent 在计划里先确定这次任务的工作边界和验收标准：

- API contract 稳定性：先判断 API impact、response shape 和 generator proof，不能先改 handler，最后再补 contract。
- 运行控制稳定性：先复用现有 config、rollout 开关或 limiter path，并覆盖 allowed、limited、disabled、invalid-config，不能顺手加新共享基础设施。
- 设计系统一致性：先映射到已有 component state，说明文案来源，并留下 responsive 和 accessibility proof，不能临时做一个相似的 warning UI。
- 运营效率：先确认操作员能处理、表格和筛选不退化，并对齐 runbook、telemetry、audit，不能只展示错误不给操作路径。

如果 agent 的计划没有落实这些项目准则，就还不该进入实现。完整的 contract 例子见 [Workflow Contract](./docs/workflow-contract.zh-CN.md)，更多 profile 和真实运行记录见 [Examples](./docs/examples.zh-CN.md)。

---

## 谁适合

Forma 先从 coding agent 开始，因为软件工作有明确的 source 文件、生成物、测试、diff 和 review proof。

它适合规则多、边界多、验证要求高的项目：团队不只是想让 agent 会做一件事，而是想让 agent 在不同任务里持续按项目标准规划、验证和停手。

这套方法也可以用于研究、分析、运营、发布、治理、客户交接或内部流程执行，只要工作有稳定来源、清楚边界、验证方式和 proof。

如果只是几条本地偏好，或者只需要一个单点能力，一个普通 custom skill 可能就够了。

---

## 真实样例和运行记录

仓库里不只有概念文档。

`examples/profiles/` 里有来自真实 workflow 家族、脱敏后的 profile，展示团队如何表达工程准则、source adapter、验证深度、proof 和停手条件。

`examples/generated/` 里保留了这些 profile 编译后的 Codex / Claude Code baselines，用来检查生成产物和 drift。

`plans/issue-*/` 是 Forma 自己开发过程留下的 workflow track。每个 issue 都有 `plan.md`、`tasks.md` 和 `runs/task-*.md`，记录真实 task contract、验证结果和 proof。

---

## 现状

Forma 还处在早期阶段。

Forma 把团队准则写进 workflow 和 task contract，但不保证模型永远听话。具体任务仍然要看 agent 实际留下的 contract 和 proof。

当前重点是：

- 降低团队梳理项目准则和生成 profile 的成本；
- 让 workflow bundle 和 Codex plugin 更容易安装；
- 改进生成 bundle 的验证；
- 补充展示真实 task contract、execution、validation 和 proof 的例子。

仓库中提交的 generated examples 主要用于检测生成结果 drift；runtime 行为要看具体 agent 执行时留下的 contract 和 proof。

Forma 也使用自己的先计划、再执行 workflow 管理开发；这个仓库的 source profile 位于 [`profiles/forma-self/`](./profiles/forma-self/)。

---

## 文档

| | |
|---|---|
| [Quick Start](./docs/quick-start.zh-CN.md) | 首次运行，从 creator 到 tracked profile 的路径。 |
| [Concepts](./docs/concepts.zh-CN.md) | 项目准则、workflow 产物、task contract 和阶段边界。 |
| [Workflow Contract](./docs/workflow-contract.zh-CN.md) | task contract 如何组织证据、边界、验证和 proof。 |
| [Profile Schema](./docs/profile-schema.zh-CN.md) | 如何把长期工程准则维护成 YAML profile。 |
| [Forma Creator](./docs/forma-creator.zh-CN.md) | 让 agent 辅助梳理准则并生成 workflow。 |
| [Skill Bundle](./docs/skill-bundle.zh-CN.md) | 生成产物结构。 |
| [Verifier](./docs/verifier.zh-CN.md) | 验证检查什么，以及不能证明什么。 |
| [Targets](./docs/targets.zh-CN.md) | Codex 和 Claude Code target 行为。 |
| [Examples](./docs/examples.zh-CN.md) | 脱敏 sample profile、生成基线和真实 tracked runs。 |
| [使用说明](./docs/usage.zh-CN.md) | 命令参考。 |

Apache-2.0 - see [LICENSE](./LICENSE)
