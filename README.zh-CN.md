<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**把项目规则编译成专属 agent workflow。**

Superpowers + AGENTS.md 给 agent 规则和流程。对轻量项目，这个组合够了。

Forma 把项目规则编译成一组 workflow skills，让 agent 在实现前先预览规则如何落到当前任务，再按 task contract 执行并留下 proof。

装好 Forma 后，你可以用一句话让 agent 从当前项目生成这套 workflow。

> **适合：** 规则多、边界多、验证要求高，并且希望计划和执行记录可审查的仓库。
>
> **不适合：** 只想给 agent 加几条个人偏好的轻量场景。

---

## 同一个目标，不同团队的过关标准

同样是给 settings 增加 rate limiting，普通计划可能只写：读相关代码、加 limiter、跑测试。

但不同团队对“合格计划”的定义不一样。Forma 生成的 workflow skills 会把各自的标准带进计划阶段，让 agent 在动代码前先按本团队的准则说清楚边界和验收条件。

| 团队关注点 | 进入 task contract 的约束 |
|---|---|
| API contract 稳定性 | 先判断 API impact、response shape 和 generator proof；不能先改 handler，最后再补 contract。 |
| 运行控制稳定性 | 复用现有 config、rollout 开关或 limiter path；覆盖 allowed、limited、disabled、invalid-config。 |
| 设计系统一致性 | 映射到已有 component state，说明文案来源，留下 responsive 和 accessibility proof。 |
| 运营效率 | 确认操作员能处理这个状态，表格和筛选不退化，并对齐 runbook、telemetry、audit。 |

这四个团队的 agent 拿到同一个 issue，会写出四份不同的 task contract。Forma 不决定哪种标准是对的，它编译的是你团队已经认可的那套标准。

---

## Forma 生成什么

Forma 生成三类产物：

| 产物 | 说明 |
|---|---|
| `profile` | 团队认可的实践准则，进入版本控制，后续可以 review 和维护。 |
| `workflow bundle / plugin` | 安装到 Codex / Claude Code 的 agent 工作流。 |
| `task contract` | agent 面对具体任务时写下的计划契约，记录到 `plans/issue-<id>/`。 |

默认 workflow 用四个阶段 skill 管住 task contract 的生命周期，并提供一个连续执行入口：

| Skill | 作用 |
|---|---|
| `forma-plan` | 把目标和项目准则对齐，形成可 review 的 proposal；不写文件，不执行任务。 |
| `forma-ground` | 按准则需要的事实取证，只读代码、文档、issue、测试等资料。 |
| `forma-lock` | 把已接受的方案写成 `plan.md` 和 `tasks.md`，锁定 task contract。 |
| `forma-execute` | 执行一个已接受 task，跑验证，记录 proof，需要 review 时停。 |

`forma-showhand` 是连续执行入口：计划已经锁定后，它会沿着剩余 tasks 继续推进，直到遇到阻塞、验证没通过或需要人介入。

团队后续调整 profile，就等于调整 workflow 守护哪些准则；重新生成 bundle 或 plugin 后，agent 会按新的约束规划和执行。

---

## task contract 长什么样

这是 Forma 自己一次真实任务的 `plan.md` 简化片段：

```text
Goal:
  让 Forma CLI help 足够清楚，agent 不需要反复试错，
  就能选择正确 command path。

Scope:
  可以改 root CLI help、no-argument 行为、tests/test_cli.py、
  docs/usage.md 和 docs/usage.zh-CN.md。

Out of scope:
  不改变 create-bundle、create-plugin、install、verify、
  build-creator 或 explain 的运行语义。
  不恢复旧的 forma create，也不加兼容 alias。

Approach:
  `forma` 无参数退出 0，并打印和 `forma --help`
  一致的 agent-facing routing guidance。
  每个 command help 都要说明下一步该运行什么。

Validation:
  uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
  uv run --extra dev forma
  uv run --extra dev forma --help
```

这不是实现完再补的说明，而是 agent 开始改代码前先锁住的任务边界。对应任务清单和执行 proof 记录在 [`plans/issue-cli-agent-facing-help/`](./plans/issue-cli-agent-facing-help/)。

---

## 开始使用

最轻入口是先安装 `forma-creator`，让 agent 从当前项目读规则、生成一套可试用 workflow：

```bash
pipx install beforewave-forma
forma build-creator --target codex --output /tmp/forma-creator
forma verify /tmp/forma-creator/codex/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

然后在 agent 里告诉它：

```text
用 forma-creator 给这个项目定制一套 workflow。
先整理关键规则给我看；确认后生成并按提示安装。
```

生成的 workflow 安装完成后，新开 thread 触发：

```text
Use forma-plan to plan this issue first.

Issue:
<你的任务或 issue>
```

正常的第一步是 proposal，不是 patch。

> **如果 agent 直接改了文件**，说明 workflow 没有加载成功或没有被触发，不是 Forma 在工作。

团队共用或长期维护规则时，走 tracked profile 路径：

```text
用 Forma 从这个项目的文档和代码里提炼工程准则，给我一版 profile 草案。
profile 确认后，基于它生成、验证并安装 Codex workflow。
```

已经有 review 过的 profile 时，可以直接用 `forma create-bundle --profile <profile.yaml>` 或 `forma create-plugin --profile <profile.yaml>` 生成 workflow 产物。完整命令见 [Quick Start](./docs/quick-start.zh-CN.md) 和 [Usage](./docs/usage.zh-CN.md)。

---

## 谁适合

**适合：**

- 高频使用 coding agent 的仓库
- 有生成文件、fixture、migration、公开 API 或敏感数据路径的项目
- 规则多到靠提示词难以稳定执行，或不同任务类型有不同验证要求
- 需要 agent 的计划和执行记录可以被审查的团队
- 希望 agent 在 scope、证据或权限不清楚时停手的场景

**可能不适合：**

- 拼写修复、一次性总结、范围极小的改动

---

## 真实样例和运行记录

仓库里不只有概念文档。

`examples/profiles/` 里有来自真实 workflow 家族、脱敏后的 profile，展示团队如何表达工程准则、来源读取方式、验证深度、proof 和停手条件。

`examples/generated/` 里保留了这些 profile 编译后的 Codex / Claude Code baselines，用来检查生成产物和 drift；它们不证明真实 agent 永远执行正确。

`plans/issue-*/` 是 Forma 自己开发过程留下的任务记录。每个 issue 都有 `plan.md`、`tasks.md` 和 `runs/task-*.md`，记录真实 task contract、验证结果和 proof；判断一次运行是否可信，要看这些记录。

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

Forma 也使用自己的先计划、再执行 workflow 管理开发；这个仓库的 profile 来源位于 [`profiles/forma-self/`](./profiles/forma-self/)。

---

## 文档

**新用户先读：**

| | |
|---|---|
| [Quick Start](./docs/quick-start.zh-CN.md) | 首次运行，从 creator 到 tracked profile 的路径。 |
| [Concepts](./docs/concepts.zh-CN.md) | 项目准则、workflow 产物、task contract 和阶段边界。 |
| [Workflow Contract](./docs/workflow-contract.zh-CN.md) | task contract 如何组织证据、边界、验证和 proof。 |

**参考文档：**

| | |
|---|---|
| [Profile Schema](./docs/profile-schema.zh-CN.md) | 如何把长期工程准则维护成 YAML profile。 |
| [Forma Creator](./docs/forma-creator.zh-CN.md) | 让 agent 辅助梳理准则并生成 workflow。 |
| [Skill Bundle](./docs/skill-bundle.zh-CN.md) | 生成产物结构。 |
| [Verifier](./docs/verifier.zh-CN.md) | 验证检查什么，以及不能证明什么。 |
| [Targets](./docs/targets.zh-CN.md) | Codex 和 Claude Code target 行为。 |
| [Examples](./docs/examples.zh-CN.md) | 脱敏 sample profile、生成基线和真实 tracked runs。 |
| [使用说明](./docs/usage.zh-CN.md) | 命令参考。 |

Apache-2.0 - see [LICENSE](./LICENSE)
