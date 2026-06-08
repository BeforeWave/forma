# Forma

**一句话启动，把静态项目规则编译成专属任务工作流。**

Forma 编译项目规则，生成项目专属 workflow harness，并在每个开发任务中落成具体边界、验证步骤和 proof。

它分三层工作：

```text
Layer 0 — 项目 Profile
借助 Forma，Agent 帮你把仓库证据和人的输入整理成项目 profile：
规则、边界、验证要求、review 预期、高风险区域和证据来源。

        ↓ 由 Forma 编译

Layer 1 — Workflow Harness
Forma 将这些规则编译成项目专属的 skill bundle 或 plugin。
这个 harness 指导 Agent：
计划 → 取证 → 锁定 → 执行 → 记录 proof

        ↓ 由 Agent 执行

Layer 2 — 任务级执行
对于每一次开发任务，规则会变成本仓库里的具体执行义务：
- 这个任务基于 `File A`、`File B` 和 `Issue C`
- 可以触及 `Module X`，但不能触及 `Generated File Y`
- 只有行为 `Z` 通过路径 `P`，才算完成
- 必须用 `Command M` 和 `Test N` 验证
- 进入下一步前必须记录 `Proof R`
```

**Forma 适合那些不只要最终 patch，还要把项目规则落到具体文件、边界、命令、测试和 proof 里接受审查的开发任务。**

[English](./README.md)

---

## 为什么需要 Forma

Coding Agent 已经能很快生成代码。

更难的是让它在具体项目里按规则工作。

大多数项目本来就有规则：

```text
计划前先阅读相关实现。
行为变更要看附近测试。
保持公开 API 兼容。
高风险修改需要 review。
完成前记录验证证明。
```

这些规则有价值，但它们通常是原则性的。

项目文档、架构说明、`AGENTS.md`、review 规范，更多是在描述“这个项目是什么样的”“做事应该遵守哪些原则”。它们能告诉 Agent 大方向，但不能自动把一次具体改动翻译成：

```text
这次要先看哪个文件。
这个计划项能改到哪里，不能碰哪里。
行为变化要用哪个测试验证。
生成文件应该从哪个 source 重新生成。
什么输出可以作为 proof。
遇到哪种不确定性必须停下来让人决定。
```

结果就是：Agent 读到了原则，但真正动手时仍然会按原则临场发挥。

Forma 要解决的就是这个断层。

它先把项目规则编译成 Plan-First workflow harness，再让这个 harness 在每一次开发任务中，把原则落成具体边界、验证步骤和 proof 要求。

比如，这样一条静态规则：

```text
生成文件不能直接修改。
修改 source 后必须重新生成，并运行相关验证。
```

真正执行时需要变成 task 粒度的契约：

```text
Task 002 — 更新生成 schema 的 source
- Evidence: 先读 `schema/source.yaml`、生成器入口和附近的 schema 测试。
- Boundary: 可以改 `schema/source.yaml` 和对应测试；不能手改 `schema/generated.json`。
- Command: 运行 `make generate-schema` 和记录在 `tasks.md` 里的 schema 验证命令。
- Validation gate: 生成结果必须只来自 source 变更，schema 验证必须通过。
- Proof: 把生成命令、验证输出和 generated diff 写进 `plans/issue-<id>/runs/task-002.md`。
```

Forma 要把静态规则推到的就是这个层级：具体证据、具体边界、具体命令、验证 gate 和 proof。

---

## Forma 安装什么

Forma 安装四个核心 Plan-First workflow skills，并带一个用于连续执行的 `forma-showhand`。

| Skill | 作用 |
|---|---|
| `forma-plan` | 澄清开发目标、范围、风险、验收标准、策略和未决问题。 |
| `forma-ground` | 从代码、文档、issue、测试、fixture 和项目引用中收集仓库证据。 |
| `forma-lock` | 锁定执行契约：具体边界、任务顺序、验证方式和 review 预期。 |
| `forma-execute` | 一次执行一个已接受任务，记录 proof，并暴露偏移或阻塞。 |

`forma-showhand` 是 `forma-execute` 的连续执行 candy skill，不是独立阶段。review 完毕、方案锁定、harness 约束够稳，就可以 show hand，让 Agent 进入自动驾驶模式，按已锁定计划持续推进，并一路留下 proof。

不喜欢这些名字？可以改。它们只是默认值。

真正重要的是生成出来的 workflow：项目原则存在于 Agent 处理开发目标时会调用的 skills 里。

---

## 快速试用

最快体验 Forma 的方式，是让 Agent 对一个真实开发目标先产出计划和 proof，而不是直接写 patch。

### 1. 试用默认 Plan-First workflow

安装 CLI：

```bash
pipx install git+https://github.com/BeforeWave/forma.git
```

创建并安装 Codex plugin：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma install --target codex --scope project /tmp/forma-codex-plugin
```

把当前 issue 或任务背景发给 Agent，并明确要求先走 `forma-plan`：

```text
Use forma-plan to plan this issue first.

Issue:
<粘贴当前 issue、需求描述、问题背景或任务目标>
```

首先应该看到 chat-level proposal 或 handoff，而不是 patch，也不是计划文件。它应该收敛目标、范围、方案、验证模型，以及是否需要仓库证据。

如果需要仓库证据，让 Agent 使用 `forma-ground`。

proposal 和 grounding 被接受后，再锁定计划：

```text
Use forma-lock to write the plan and task contract.
```

这时才应该看到任务级计划：

```text
plans/issue-<id>/plan.md
plans/issue-<id>/tasks.md
```

Forma workflow 会在规划过程中整理、追问或固定必要细节：任务基于哪些文件，哪些内容在边界内或边界外，每个任务如何验收，用什么命令或测试验证，以及继续执行前要记录什么 proof。

然后执行下一个已接受任务：

```text
Use forma-execute to execute the next accepted task.
```

这次执行应该在这里留下 proof：

```text
plans/issue-<id>/runs/<task-id>.md
```

第一次试用的重点，是看 Agent 是否留下计划、边界、验证和 proof，而不是只给 patch。

### 2. 用 forma-creator 对话式塑造项目专属 harness

想快速做一套项目专属 harness，可以安装 creator skill：

```bash
forma build-creator --target codex --output /tmp/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

然后像和协作者沟通一样告诉 Codex：

```text
针对这个 repo 定制一套 workflow。

先看仓库结构、验证方式、生成物和项目约定。

我比较在意：
- 生成结果必须从 source 产出；
- docs-only 改动用轻量检查；
- 行为变更前看附近测试；
- 高风险判断先停下来让我确认。
```

creator skill 会把这段沟通分类成 temporary injection，生成并验证一次性 harness。

需要长期复用的规则写进 tracked profile。`forma explain profile --target codex` 可以给 Agent profile 编写标准；profile 经过版本化和 review 后，再稳定生成 harness。

---

## 什么时候使用 Forma

更具体地说，适合：

- 高频使用 Agent 辅助开发的仓库；
- 有生成文件、fixture、migration、公开 API 或敏感数据路径的项目；
- 需要 Agent 产出可审查计划和 proof 的团队；
- 不同任务类型有不同验证方式的 workflow；
- 希望 Agent 在 scope、证据或权限不清楚时停止的场景。

可能不适合：

- 拼写修复；
- 一次性总结；
- 范围非常明确的小修改；
- 只需要几条静态说明的仓库。

---

## 文档

- [使用说明](./docs/usage.zh-CN.md)：命令、安装位置、验证、targets 和自定义生成。
- [快速开始](./docs/quick-start.zh-CN.md)：首次使用 walkthrough。
- [核心概念](./docs/concepts.zh-CN.md)：心智模型和适用边界。
- [Forma Creator](./docs/forma-creator.zh-CN.md)：生成项目专属 workflow。
- [Profile Schema](./docs/profile-schema.zh-CN.md)：长期维护的 profile 源格式。
- [Targets](./docs/targets.zh-CN.md)：Codex 和 Claude Code 的行为。
- [Project Structure](./STRUCTURE.md)：源码结构和边界。

---

## 状态

Forma 还处在早期阶段。

Forma 给 Agent 的是更好的控制界面，不是行为保证。Agent 是否真正遵循生成的 skill，仍然取决于模型和宿主环境。把 workflow 写进文件、分成阶段、让 proof 成为流程的一部分，比只靠聊天记忆更可靠，但不是魔法保证。

当前重点是：

- 让 Plan-First agent workflow 更容易安装；
- 让 project-specific workflow profile 更容易编写；
- 改进生成 bundle 的验证；
- 补充展示真实 planning、execution、validation 和 proof 的例子。

仓库中提交的 generated examples 主要用于 drift baseline，不是 runtime agent behavior 的证明。

BTW，Forma 也使用自己的 Plan-First workflow 管理开发；这个仓库的 source profile 位于 `profiles/forma-self/`。

---

## License

Apache-2.0. See [LICENSE](./LICENSE).
