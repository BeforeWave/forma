# 快速开始

英文版：[quick-start.md](./quick-start.md)

这页只讲从零跑通一套 Forma workflow。先用默认 Codex plugin 看见效果，再决定要不要塑造项目专属 harness。

## 安装 Forma

先安装 CLI：

```bash
pipx install git+https://github.com/BeforeWave/forma.git
forma --help
```

下面的示例都假设 `forma` 已经在 `PATH` 里。

## 第一次跑通：默认 Codex Plugin

生成并安装默认 Plan-First plugin：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma install --target codex --scope project /tmp/forma-codex-plugin
```

然后让 Codex 从规划开始：

```text
用 forma-plan 先规划这个 issue。
```

一次有效的首跑不应该从目标直接跳到 patch。它应该先澄清目标、收集证据、锁定执行契约，再带着证明执行任务。

## 看什么结果

跑完一轮 workflow 后，先看可审查产物：

- `plans/issue-<id>/plan.md`：澄清后的目标、范围、方案、验证、策略，以及产物和证明边界。
- `plans/issue-<id>/tasks.md`：有顺序的已接受任务，包括交付目标、证明义务、依赖和约束。
- `plans/issue-<id>/runs/`：workflow 记录下来的执行证明。

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
使用 forma-creator，针对这个 repo 定制一套 workflow。先看看仓库结构和常见验证方式。我比较在意：生成结果要从源码出，docs-only 改动用轻量检查，改代码前先看附近有没有测试，不确定的判断先列出来让我决定。
```

Creator 应该先分类这些关注点，再生成固定 target contract 允许的 workflow bundle 或 Codex plugin，并在交付前验证输出。

## 从长期 Profile 生成

当项目原则已经稳定到可以作为源码评审时，用 tracked profile。

生成 Codex skills：

```bash
forma create-bundle \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

安装到 Codex：

```bash
forma install --target codex --scope user /tmp/backend-plan-first-codex
```

同一份 profile 也可以生成 Claude Code skills：

```bash
forma create-bundle \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-claude-code

forma verify /tmp/backend-plan-first-claude-code
forma install --target claude-code --scope user /tmp/backend-plan-first-claude-code
```

## 安装位置

生成的 workflow 可以安装给当前用户，也可以放进项目：

| 目标 | 个人安装 | 项目安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | `$HOME/.codex/plugins` | `.codex/plugins` |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |

信任项目 skills 前先审查内容。生成技能可以包含脚本，也可能带有 target 专用工具行为。

## 让 Agent 起草 Profile

在已经安装 Forma 的下游项目里，可以对 Agent 说：

```text
运行：
  forma explain profile --target codex

把命令输出当作 profile 编写标准。
检查当前仓库，并提出一个可长期维护的 Forma profile。
先展示 profile 结构，不要直接写文件。
解释每条约束为什么放在那里，并明确标出未知项。
```

这是起草路径，不是自动提交路径。把 profile 当作长期源码前，需要人工评审。

## 继续阅读

- [核心概念](./concepts.zh-CN.md)：profile、workflow 和 runtime harness 的关系。
- [Workflow Contract](./workflow-contract.zh-CN.md)：生成工作流具体约束什么。
- [Skill Bundle](./skill-bundle.zh-CN.md)：Forma 写到磁盘上的产物是什么。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源如何组织。
- [Forma Creator](./forma-creator.zh-CN.md)：一次性生成如何工作。
- [Verifier](./verifier.zh-CN.md)：`forma verify` 检查什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [使用说明](./usage.zh-CN.md)：命令参考和安装位置。
