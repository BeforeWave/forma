<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**把项目规则变成专属 Agent 工作流。**

Superpowers 和 AGENTS.md 可以给 Agent 提供规则和流程。对轻量项目，这样通常够了。

Forma 把项目规则编排成 Agent 可执行的工作流。处理任务前，Agent 会先说明这些规则如何落实到当前任务：准备做什么、怎么检查结果、什么时候需要停下来让人确认。

规则不是执行时临时套用，而是先变成这次任务的边界；确认后，Agent 再按这个边界执行并留下验证记录。这样你少重复交代，任务也更少跑偏，交付更容易检查。

装好 Forma 后，你可以用一句话让 Agent 从当前项目生成这套工作流。

> **适合：** 规则多、边界多、验证要求高，并且希望计划和执行记录便于检查的仓库。
>
> **不适合：** 只想给 Agent 加几条个人偏好的轻量场景。

---

## 同一个目标，不同计划写法

同样是“给设置模块增加限流”，普通计划可能只写：看代码、加限流器、跑测试。

Forma 的区别是：项目规则会进入工作流，让 Agent 在计划里主动写出不同重点。
这些取舍不用你每次重复提醒。

| 项目规则偏向 | 计划重点会变成 |
|---|---|
| 接口兼容优先 | 哪些接口、字段、生成文件受影响，是否需要 API 评审。 |
| 灰度发布优先 | 用哪个开关，怎么关闭、回滚，异常配置怎么测。 |
| 用户体验优先 | 限流状态怎么展示，文案、组件状态、无障碍怎么验。 |
| 运营处理优先 | 谁会看到这个状态，怎么判断、处理、追踪。 |

这不是一张必做清单。它说明同一个需求，在不同项目规则下，会写出不同的计划边界和验收方式。

---

## Forma 生成什么

日常使用会看到三样东西：

| 名称 | 作用 |
|---|---|
| `profile` | 从项目里提炼出的工程规则说明，写清阶段约束、工具习惯、验证、执行记录和停手条件。 |
| `workflow bundle / plugin` | 按 profile 生成，安装到 Codex、Claude Code 或 OpenCode，让 Agent 按同一套规则工作。 |
| `task contract` | Agent 每次任务开始前写下的计划边界，记录目标、范围、验证方式和执行记录要求。 |

profile 要长期复用时再提交进版本控制。只想试一套工作流时，它可以先作为临时文件使用，不需要提交。

默认工作流用四个阶段管理 task contract，并提供一个连续执行入口：

| 阶段 | 作用 |
|---|---|
| `plan` | 按项目准则检查目标，形成可评审的 proposal；不写文件，不执行任务。 |
| `ground` | 按准则需要的事实取证，只读代码、文档、issue、测试等资料。 |
| `lock` | 把已接受的方案写成 `plan.md` 和 `tasks.md`，锁定 task contract。 |
| `execute` | 执行一个已接受 task，跑验证，记录验证结果，需要评审时停。 |

`showhand` 是连续执行入口：计划已经锁定后，它会沿着剩余任务继续推进，直到遇到阻塞、验证没通过或需要人介入。

安装为 plugin 时，用 `forma:plan` 这类 `forma:*` 触发；安装为 direct skill bundle 时，用 `forma-plan` 这类 `forma-*` skill。

团队后续调整 profile，就会改变这套工作流要求 Agent 执行哪些准则。

---

## task contract 是什么样

这是 Forma 自己一次真实任务的 `plan.md` 简化片段：

```text
Goal:
  让 Forma CLI help 足够清楚，Agent 不需要反复试错，
  就能选择正确命令路径。

Scope:
  可以改根命令 help、无参数行为、tests/test_cli.py、
  docs/usage.md 和 docs/usage.zh-CN.md。

Out of scope:
  不改变 install、verify 或 explain 的运行语义。
  不恢复已经移除的命令 alias。

Approach:
  `forma` 无参数时退出 0，并打印和 `forma --help`
  一致的 Agent 侧命令选择提示。
  每个 command help 都要说明下一步该运行什么。

Validation:
  uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
  uv run --extra dev forma
  uv run --extra dev forma --help
```

这不是实现完再补的说明，而是 Agent 开始改代码前先锁住的任务边界。对应任务清单和执行记录在 [`plans/issue-cli-agent-facing-help/`](./plans/issue-cli-agent-facing-help/)。

---

## 开始使用

最轻入口是让 Agent 先整理项目规则，确认后生成并安装工作流：

```bash
pipx install forma-cli
```

然后告诉 Agent：

```text
用 Forma 把这个项目的工程规则管理成一套 Codex workflow。
先提炼规则并给我看你建议的 profile；我确认后，再 build、verify 并安装这套 workflow。
```

Agent 会自己读取 Forma 的 profile 编写指南，并在你确认规则后生成、验证和安装工作流。

生成的工作流安装完成后，新开一个会话触发：

```text
Use forma:plan to plan this issue first.

Issue:
<你的任务或 issue>
```

如果安装的是 direct skill bundle，而不是 plugin，就使用对应的 `forma-*` skill 触发名。

正常的第一步是提出方案，不是直接改文件。

> **如果 Agent 直接改了文件**，说明工作流没有加载成功或没有被触发，不是 Forma 在工作。

如果这套规则要团队共用或长期维护，再把 profile 放进版本控制。已经有评审过的 profile 时，可以直接用 `forma build bundle --profile <profile.yaml>` 或 `forma build plugin --profile <profile.yaml>` 生成工作流产物。完整命令见 [Quick Start](./docs/quick-start.zh-CN.md) 和 [Usage](./docs/usage.zh-CN.md)。

---

## 谁适合

**适合：**

- 高频使用 coding agent 的仓库
- 有生成文件、fixture、migration、公开 API 或敏感数据路径的项目
- 规则多到靠提示词难以稳定执行，或不同任务类型有不同验证要求
- 需要 Agent 的计划和执行记录便于检查的团队
- 希望 Agent 在范围、证据或权限不清楚时停手的场景

**可能不适合：**

- 拼写修复、一次性总结、范围极小的改动

---

## 真实样例和运行记录

仓库里不只有概念文档。

`examples/profiles/` 里有来自真实工作流家族、脱敏后的 profile，展示团队如何表达工程准则、来源读取方式、验证深度、执行记录和停手条件。

示例生成产物不再提交到仓库里。如果某个 sample profile 有参考价值，可以自己用 `forma build bundle` 或 `forma build plugin` 生成到临时目录或项目指定目录后查看。

`plans/issue-*/` 是 Forma 自己开发过程留下的任务记录。每个 issue 都有 `plan.md`、`tasks.md` 和 `runs/task-*.md`，记录真实 task contract、验证结果和执行记录；判断一次运行是否可信，要看这些记录。

---

## 现状

Forma 还在早期阶段。目前可以为 Codex、Claude Code 和 OpenCode 生成 skill bundle；Codex 和 Claude Code 也支持 plugin source。

Forma 让 Agent 先计划再行动，并在交付后留下证据。每次运行是否可信，仍要看它留下的任务约定和执行记录。

当前重点是：降低 profile 生成成本、让 bundle/plugin 更容易安装、加强验证，并补充更多真实运行记录。

Forma 也使用自己的先计划、再执行工作流管理开发；这个仓库的 profile 来源位于 [`.forma/profile.yaml`](./.forma/profile.yaml)。

---

## 文档

**新用户先读：**

| | |
|---|---|
| [Quick Start](./docs/quick-start.zh-CN.md) | 首次运行、生成、验证和安装工作流。 |
| [Concepts](./docs/concepts.zh-CN.md) | 项目准则、工作流产物、task contract 和阶段边界。 |
| [Workflow Contract](./docs/workflow-contract.zh-CN.md) | task contract 如何组织证据、边界、验证和执行记录。 |

**参考文档：**

| | |
|---|---|
| [Profile Schema](./docs/profile-schema.zh-CN.md) | 需要长期维护时，profile 如何组织。 |
| [Skill Bundle](./docs/skill-bundle.zh-CN.md) | 生成产物结构。 |
| [Verifier](./docs/verifier.zh-CN.md) | 验证检查什么，以及不能证明什么。 |
| [Targets](./docs/targets.zh-CN.md) | Codex、Claude Code 和 OpenCode target 行为。 |
| [Examples](./docs/examples.zh-CN.md) | 脱敏 sample profile、本地生成说明和真实 tracked runs。 |
| [使用说明](./docs/usage.zh-CN.md) | 命令参考。 |

Apache-2.0 - see [LICENSE](./LICENSE)
