# 快速开始

英文版：[quick-start.md](./quick-start.md)

这页只讲一件事：怎样从现有 profile 生成、验证并安装一套工作流。

不要一上来就设计完美 profile。先用一个小 workflow 试手感，看它是否真的改变 Agent 的行为。

---

## 安装 Forma

在源码仓库里做本地开发安装：

```bash
pip install -e ".[dev]"
forma --help
```

下面的示例都假设 `forma` 已经在 `PATH` 里。

如果已经安装过 Forma，可以这样确认 CLI 可用：

```bash
forma --help
```

---

## 安装位置

生成套件可以安装给当前用户，也可以放进项目：

| 目标 | 个人安装 | 项目/团队安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Codex plugins | `$HOME/.codex/plugins` | `.codex/plugins` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

信任项目或团队技能前先审查内容。技能可以包含脚本，也可能带有 target 专用的工具行为。

---

## 第一次跑通路径

设计大型 profile 前，先跑通一次小路径：

1. 从一个小 sample profile 生成套件。
2. 验证生成结果。
3. 安装到一个目标 Agent。
4. 在这个 Agent 里触发一个 Plan-First 任务。
5. 检查计划、任务契约、验证结果和执行证据。
6. 等工作流证明有用后，再调整 profile。

---

## 路径 1：从长期 profile 生成

适合长期维护的团队或项目规则。规则放在已经评审过的 profile 中。

生成 Codex 工作流：

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

然后在某个仓库里启动 Codex，调用一个生成出来的技能。

对 sample backend profile，可以先试：

```text
Use backend-plan-first-plan-issue to turn this change request into a bounded plan:
make one low-risk docs improvement in this repository.
Do not implement yet.
```

同一个 profile 也可以生成 Claude Code 工作流：

```bash
forma create-bundle \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-claude-code

forma verify /tmp/backend-plan-first-claude-code
```

安装到 Claude Code：

```bash
forma install --target claude-code --scope user /tmp/backend-plan-first-claude-code
```

在 Claude Code 里，可以直接调用对应生成技能，也可以用匹配的自然语言请求。项目级 skills 需要先信任 workspace，技能自带的工具才会生效。

---

## 路径 2：通过 `forma-creator` 生成

适合已经评审过的一次性自然语言约束。

生成的 `forma-creator` 会帮助把这些约束整理成 temporary injection JSON，再生成目标 Agent 专用工作流套件，并在交付前验证输出。

生成 Codex 版 creator：

```bash
forma build-creator \
  --target codex \
  --output /tmp/forma-creator-dist

forma verify /tmp/forma-creator-dist/codex/forma-creator
```

安装到 Codex：

```bash
forma install --target codex --scope user /tmp/forma-creator-dist/codex/forma-creator
```

生成 Claude Code 版 creator：

```bash
forma build-creator \
  --target claude-code \
  --output /tmp/forma-creator-dist

forma verify /tmp/forma-creator-dist/claude-code/forma-creator
```

安装到 Claude Code：

```bash
forma install --target claude-code --scope user /tmp/forma-creator-dist/claude-code/forma-creator
```

每个 `forma-creator` 都固定一个 target。

Codex 版 creator 生成 Codex 形态的 Plan-First 工作流 bundle，也可以在固定 target contract 明确允许时生成 Codex plugin。Claude Code 版 creator 只生成 Claude Code 形态的 bundle。

安装后，可以在 Agent 里快速试工作流想法：

```text
使用 forma-creator，把下面这些工作流想法生成成 Plan-First 套件：
- shape 必须识别权威来源和未决问题；
- gauge 只读取当前范围需要的证据；
- seal 必须把验收条件和验证要求写进每个可执行任务；
- pour 一次只执行一个已接受任务，并记录证明；
- flow 遇到跨层改动时先停下，除非 sealed plan 明确允许继续。

生成前先说明这些规则会如何分类。
生成后验证套件。
```

---

## 路径 3：生成 Codex Plugin

如果接收方 Codex 环境希望安装一个 plugin，并通过这个 plugin 暴露五个默认 Plan-First skills，用这个路径：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma verify /tmp/forma-codex-plugin
forma install --target codex --scope user /tmp/forma-codex-plugin
```

安装后的 plugin 暴露 `forma-plan`、`forma-ground`、`forma-lock`、`forma-execute` 和 `forma-showhand`。Claude Code plugin 不在当前范围内；Claude Code 用 skill bundle。

给 Agent 的交接话术：

```text
安装本地 Forma Codex plugin：/tmp/forma-codex-plugin。
安装前先验证。
然后用 forma-plan 澄清第一个任务；只有计划锁定后才用 forma-showhand。
```

---

## 让 Agent 帮你起草 profile

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

---

## Profile 和注入指南

让 Forma 输出 Agent 可读的编写指南：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

稳定规则放进长期 profile。一次性、不应成为项目长期规则的内容，通过一次性注入进入生成过程。

---

## 第一次跑完后检查什么

第一次成功跑通后，应该能看到一个或多个具体产物：

- 有边界的方案；
- grounding handoff；
- `plan.md` 和 `tasks.md`；
- 任务证明或验证输出；
- 生成 bundle 里的 `.forma-manifest.json`。

第一次用生成工作流跑任务后，检查 Agent 是否：

- 先澄清请求，再进入实现；
- 先收集相关证据，再规划；
- 产出有边界的任务计划；
- 写明验证或证明要求；
- 避免执行无关改动；
- 在工作流要求停止时停下。

如果这些行为不明显，先调整 profile 或生成工作流，不要急着增加更多规则。

## 继续阅读

- [Workflow Contract](./workflow-contract.zh-CN.md)：生成工作流具体约束什么。
- [Skill Bundle](./skill-bundle.zh-CN.md)：Forma 写到磁盘上的产物是什么。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源如何组织。
- [Forma Creator](./forma-creator.zh-CN.md)：一次性生成如何工作。
- [Verifier](./verifier.zh-CN.md)：`forma verify` 检查什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [Examples](./examples.zh-CN.md)：端到端运行应该看见什么。
