# 快速开始

这页只讲怎么开始用 Forma。

英文版：[quick-start.md](./quick-start.md)

## 安装 Forma

在源码仓库里做本地开发安装：

```bash
pip install -e ".[dev]"
forma --help
```

安装后可以直接使用 `forma` 命令。下面的示例都假设 `forma` 已经在 `PATH` 里。

如果已经安装过 Forma，可以这样确认 CLI 可用：

```bash
forma --help
```

## 让 Agent 帮你起草 profile

在已经安装 Forma 的下游项目里，直接对 Agent 说：

```text
运行：
  forma explain profile --target codex

把命令输出当作 profile 编写标准。
检查当前仓库，并提出一个可长期维护的 Forma profile。
先展示 profile 结构，不要直接写文件。
解释每条约束为什么放在那里，并明确标出未知项。
```

## 路径 1：从长期 profile 生成

适合长期维护的团队或项目规则。规则放在已经评审过的 profile 中。

生成 Codex 工作流：

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

安装到 Codex：

```bash
mkdir -p ~/.codex/skills
cp -R /tmp/backend-plan-first-codex/* ~/.codex/skills/
```

同一个 profile 也可以生成 Claude Code 工作流：

```bash
forma create \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-claude-code

forma verify /tmp/backend-plan-first-claude-code
```

## 路径 2：通过 `forma-creator` 生成

适合已经评审过的一次性自然语言约束。安装后的 creator 会先分类这些约束，再生成目标 Agent 专用的工作流套件，并在交付前验证输出。

生成 Codex 版创建器：

```bash
forma build-creator \
  --target codex \
  --output /tmp/forma-creator-dist

forma verify /tmp/forma-creator-dist/codex/forma-creator
```

安装到 Codex：

```bash
mkdir -p ~/.codex/skills
cp -R /tmp/forma-creator-dist/codex/forma-creator ~/.codex/skills/
```

生成 Claude Code 版创建器：

```bash
forma build-creator \
  --target claude-code \
  --output /tmp/forma-creator-dist

forma verify /tmp/forma-creator-dist/claude-code/forma-creator
```

每个 `forma-creator` 都固定一个目标界面。Codex 版创建器生成 Codex 形态的工作流套件；Claude Code 版创建器生成 Claude Code 形态的套件。

安装后，可以在 Agent 里快速试工作流想法：

```text
使用 forma-creator，把下面这些工作流想法生成成 Plan-First 套件：
- 规划前先确认权威来源和未决问题；
- 只读取当前范围需要的证据；
- 每个任务都写清验收条件和验证要求；
- 一次只执行一个已接受任务，并记录证明；
- 遇到跨层改动时先停下，除非计划明确允许继续。

生成前先说明这些规则会如何分类。
生成后验证套件。
```

## Profile 和注入指南

让 Forma 输出 Agent 可读的编写指南：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

稳定规则放进长期 profile。一次性、不应成为项目长期来源的规则，通过一次性注入进入生成过程。
