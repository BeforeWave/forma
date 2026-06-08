# 快速开始

英文版：[quick-start.md](./quick-start.md)

这页只讲从零跑通一套 Forma workflow。先用默认 Codex plugin 看见一次真实任务如何产出 plan、task 边界、验证 gate 和 proof，再决定要不要塑造项目专属 harness。

## 安装 Forma

先安装 CLI：

```bash
pipx install git+https://github.com/BeforeWave/forma.git
forma --help
```

下面的示例都假设 `forma` 已经在 `PATH` 里。

## 第一次跑通：默认 Codex Plugin

生成默认 Plan-First plugin：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
```

然后把这个本地 plugin 加到 Codex marketplace，用
`codex plugin add <plugin>@<marketplace>` 安装，或在 Codex plugin UI 里安装。

把当前 issue 或任务背景发给 Codex，并要求先从规划开始：

```text
Use forma-plan to plan this issue first.

Issue:
<粘贴当前 issue、需求描述、问题背景或任务目标>
```

一次有效的首跑不应该从目标直接跳到 patch。首先应该看到 chat-level proposal 或 handoff，而不是计划文件。它应该收敛目标、范围、方案、验证模型，以及是否需要仓库证据。

如果需要仓库证据，让 Codex 使用 `forma-ground`。

proposal 和 grounding 被接受后，再锁定计划：

```text
Use forma-lock to write the plan and task contract.
```

然后执行下一个已接受任务：

```text
Use forma-execute to execute the next accepted task.
```

## 看什么结果

跑完一轮 workflow 后，先看可审查产物：

- `plans/issue-<id>/plan.md`：澄清后的目标、范围、方案、验证策略，以及必要的 artifact/evidence boundary。
- `plans/issue-<id>/tasks.md`：有顺序的已接受任务，包括交付目标、具体验证命令或共享检查、依赖和约束。
- `plans/issue-<id>/runs/`：workflow 记录下来的 task proof。

这个仓库的真实 Forma plans 在 [`../plans/`](../plans/)。

## 用 `forma-creator` 塑造 Harness

当你想让 Agent 先把项目关注点变成一次性 workflow，但还不想写长期 profile YAML 时，用 `forma-creator`。

生成并安装 Codex creator：

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

Creator 应该先分类这些关注点，再生成固定 target contract 允许的 workflow bundle 或 Codex plugin，并在交付前验证输出。

## 两条轻量定制入口

想让 Agent 帮你塑造项目规则，有两条轻量路径。它们都可以对话式完成，区别在产物：

| 路径 | 输入 | 产物 |
|---|---|---|
| `forma-creator` | 自然语言项目关注点，creator 分类成 temporary injection。 | 已验证的一次性 harness：skill bundle 或 Codex plugin。 |
| `forma explain profile` + Agent | CLI 输出 profile 编写标准，Agent 读仓库并吸收人的补充。 | tracked profile YAML；review 后再用 CLI 稳定生成 harness。 |

## 从长期 Profile 生成

当项目规则已经稳定到可以作为源码评审时，用 tracked profile。

生成 Codex skills：

```bash
forma create-bundle --target codex --profile examples/profiles/sample-software/sample-software-plan-first.yaml --output /tmp/software-plan-first-codex
forma verify /tmp/software-plan-first-codex
```

安装到 Codex：

```bash
forma install --target codex --scope user /tmp/software-plan-first-codex
```

同一份 profile 也可以生成 Claude Code skills：

```bash
forma create-bundle --target claude-code --profile examples/profiles/sample-software/sample-software-plan-first.yaml --output /tmp/software-plan-first-claude-code
forma verify /tmp/software-plan-first-claude-code
forma install --target claude-code --scope user /tmp/software-plan-first-claude-code
```

## 安装位置

生成的 workflow 可以安装给当前用户，也可以放进项目：

| 目标 | 个人安装 | 项目安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | Codex marketplace / plugin UI | Codex marketplace / plugin UI |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |

信任项目 skills 前先审查内容。生成技能可以包含脚本，也可能带有 target 专用工具行为。

## 用 CLI 对话式起草 Profile

在已经安装 Forma 的下游项目里，可以对 Agent 说：

```text
运行：
  forma explain profile --target codex

把命令输出当作 profile 编写标准。
检查当前仓库，并提出一个可长期维护的 Forma profile。
先展示 profile 结构，不要直接写文件。
解释每条约束为什么放在那里，并明确标出未知项。
```

这也是轻量路径，但产物不是一次性 harness，而是可版本化的 profile 源。把 profile 当作长期源码前，需要人工评审。

## 继续阅读

- [核心概念](./concepts.zh-CN.md)：项目规则、workflow harness 和 task 执行模型。
- [Workflow Contract](./workflow-contract.zh-CN.md)：生成工作流具体约束什么。
- [Skill Bundle](./skill-bundle.zh-CN.md)：Forma 写到磁盘上的产物是什么。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源如何组织。
- [Forma Creator](./forma-creator.zh-CN.md)：一次性生成如何工作。
- [Verifier](./verifier.zh-CN.md)：`forma verify` 检查什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [使用说明](./usage.zh-CN.md)：命令参考和安装位置。
