<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

团队的工程实践不该只停在文档里。
**Forma 为每个项目生成专属 agent harness，让 agent 执行前先声明如何遵守团队规则，再按任务契约交付。**

这份任务契约不是泛泛的“我会按规则做”，也不是普通执行计划。它是团队工程原则在当前任务细节上的具体约束：基于哪些证据、允许触及哪些边界、哪些文件不能改、必须跑哪些验证、proof 记录在哪里、遇到什么情况必须停下来。

也就是说，Forma 让团队原则不只是被 agent 读到，而是在每次执行前变成可审查、可约束、可追溯的具体义务。

---

## Forma 产出什么

Forma 的长期输入是 `profile`，交付给 agent 使用的是 harness，任务开始时落成的是 task contract。

- `profile`：团队工程原则的源码，进入版本控制。
- `skill bundle`：安装到 Codex 或 Claude Code 的 skill 目录。
- `Codex plugin`：把同一套 harness 打包成 Codex plugin。
- `task contract`：agent 面对一次具体任务时写出的承诺，记录到 `plans/issue-<id>/`。

默认 harness 包含五个 skills：

| Skill | 作用 |
|---|---|
| `forma-plan` | 澄清目标、范围、约束、验收标准；只在对话里收敛方案，不写计划文件，不执行任务。 |
| `forma-ground` | 只读取证，收集代码、文档、issue、测试等证据，不写文件，不决定任务。 |
| `forma-lock` | 把已经收敛的方案写成 `plan.md` 和 `tasks.md`，锁定任务契约。 |
| `forma-execute` | 执行一个已接受 task，跑验证，记录 proof，需要 review 时停。 |
| `forma-showhand` | 在已锁定计划内连续执行剩余 tasks，直到遇到阻塞、验证失败或需要人介入。 |

profile 可以改名、加约束、加引用和验证要求；生成出来的 bundle/plugin 会暴露对应的 skills。

---

## 怎么用

从 tracked profile 生成一个 Codex skill bundle，并在安装前验证：

```bash
forma create-bundle \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

安装 verified bundle 后，在 agent thread 里先触发规划：

```text
Use forma-plan to plan this issue first.

Issue:
<你的任务或 issue>
```

后续按任务契约推进：需要仓库证据时用 `forma-ground`，方案确认后用 `forma-lock` 落计划，执行时用 `forma-execute`；计划稳定后可以用 `forma-showhand` 连续推进。

没有 profile 时，用 `forma-creator` 起草；需要 Codex plugin 时，用 `forma create-plugin`。完整安装和 target 细节见 [Quick Start](./docs/quick-start.zh-CN.md) 和 [Usage](./docs/usage.zh-CN.md)。

---

## 现状

Forma 还处在早期阶段。

Forma 给 agent 的是更好的控制界面，不是行为保证。agent 是否真正遵循生成的 skill，仍然取决于模型和宿主环境。把 workflow 写进文件、分成阶段、让 proof 成为流程的一部分，比只靠聊天记忆更可靠，但不是魔法保证。

当前重点是：

- 让 Plan-First agent workflow 更容易安装；
- 让 project-specific workflow profile 更容易编写；
- 改进生成 bundle 的验证；
- 补充展示真实 planning、execution、validation 和 proof 的例子。

仓库中提交的 generated examples 主要用于 drift baseline，不是 runtime agent behavior 的证明。

Forma 也使用自己的 Plan-First workflow 管理开发；这个仓库的 source profile 位于 [`profiles/forma-self/`](./profiles/forma-self/)。

---

## 文档

- [Quick Start](./docs/quick-start.zh-CN.md)
- [Concepts](./docs/concepts.zh-CN.md)
- [Workflow Contract](./docs/workflow-contract.zh-CN.md)
- [Profile Schema](./docs/profile-schema.zh-CN.md)
- [Targets](./docs/targets.zh-CN.md)
- [Usage](./docs/usage.zh-CN.md)

Apache-2.0 - see [LICENSE](./LICENSE)
