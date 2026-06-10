# 快速开始

英文版：[quick-start.md](./quick-start.md)

这页只讲从零跑通 Forma：先把 `forma-creator` 装给 agent，再让它从项目文档和代码里挖掘工程准则，生成一套可试用 workflow。确认有用后，再把规则长期化成 profile。

## 1. 安装 CLI 和 Creator

先安装 Forma CLI：

```bash
pipx install forma-cli
forma --help
```

以 Codex 为例，生成并安装 creator skill：

```bash
forma build-creator --target codex --output /tmp/forma-creator
forma verify /tmp/forma-creator/codex/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

装好以后，新开 agent thread，直接说：

```text
用 forma-creator 给这个项目定制一套 workflow。
从文档和代码里挖掘工程准则，先整理给我看；我确认后再生成 workflow，并按提示安装。
```

Creator 会让 agent 先从项目事实里提炼准则，例如权威资料、修改边界、验证深度、proof 和停手条件。你确认后，它会生成并验证一套可试用 workflow 产物，并报告输出路径和安装提示。

## 2. 试用生成的 Workflow

安装生成产物后，新开 thread：

```text
Use forma-plan to plan this issue first.

Issue:
<粘贴当前 issue、需求描述、问题背景或任务目标>
```

第一次有效输出应该是 proposal，不是 patch。它应该先把目标、范围、项目准则和验证方式说清楚。

如果需要仓库证据，继续：

```text
Use forma-ground to gather the evidence needed for this plan.
```

证据和方案确认后，锁定 task contract：

```text
Use forma-lock to write the plan and task contract.
```

然后执行一个已接受任务：

```text
Use forma-execute to execute the next accepted task.
```

## 3. 看产物

重点看这些文件：

- `plans/issue-<id>/plan.md`：当前目标、范围、项目准则、证据路径和验证策略。
- `plans/issue-<id>/tasks.md`：有顺序的已接受任务，包括边界、验证和停手条件。
- `plans/issue-<id>/runs/`：执行 proof、验证结果和需要 review 的记录。

这个仓库自己的 Forma plans 在 [`../plans/`](../plans/)。

## 4. 长期化成 Profile

如果一开始就想形成长期 profile，也可以直接让 agent 用 Forma 起草：

```text
用 Forma 从这个项目的文档和代码里提炼工程准则，给我一版 profile 草案。
profile 确认后，基于它生成、验证并安装目标 workflow。
```

agent 会用 `forma explain profile --target codex` 读取 profile 编写标准。流程是：先给 profile 草案；你 review；确认后再生成、验证并按提示安装 workflow。

如果你已经有 review 过的 profile，可以直接确定性生成：

```bash
forma create-bundle --target codex --profile myproject.yaml --output /tmp/bundle
forma verify /tmp/bundle
forma install --target codex --scope project /tmp/bundle
```

同一份 profile 也可以生成 Claude Code skills：

```bash
forma create-bundle --target claude-code --profile myproject.yaml --output /tmp/bundle-cc
forma verify /tmp/bundle-cc
forma install --target claude-code --scope user /tmp/bundle-cc
```

也可以生成 OpenCode skills：

```bash
forma create-bundle --target opencode --profile myproject.yaml --output /tmp/bundle-opencode
forma verify /tmp/bundle-opencode
forma install --target opencode --scope project /tmp/bundle-opencode
```

## 怎么选

| 路径 | 适合 | 产物 |
|---|---|---|
| `forma-creator` | 临场定制，先试一套项目 workflow。 | 已验证的一次性 skill bundle 或 plugin。 |
| `forma explain profile` + agent | 一开始就要可 review、可维护的长期源码。 | tracked profile YAML，再编译成 workflow。 |
| `forma create-bundle` | 已经有 review 过的 profile。 | 从 profile 重复生成的 workflow bundle。 |

## 安装位置

生成的 workflow 可以安装给当前用户，也可以安装到项目：

| 目标 | 个人安装 | 项目安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.agents/skills` |
| OpenCode skills | `$HOME/.config/opencode/skills` | `.opencode/skills` |
| Codex plugins | Codex marketplace / plugin UI | Codex marketplace / plugin UI |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

信任项目 skills 前先审查内容。生成技能可以包含脚本，也可能带有 target 专用工具行为。

## 验证产物

安装、提交或分享生成 bundle / plugin source 前，始终先验证：

```bash
forma verify /tmp/myproject-bundle
```

验证会检查结构和方法规则。它不证明 profile 是正确的项目决策，也不证明 agent 运行时一定遵守。边界见 [Verifier](./verifier.zh-CN.md)。

## 继续阅读

- [核心概念](./concepts.zh-CN.md)：三层模型、定制路径和阶段边界。
- [Workflow Contract](./workflow-contract.zh-CN.md)：生成工作流具体约束什么。
- [Forma Creator](./forma-creator.zh-CN.md)：临场定制和 temporary injection 如何工作。
- [Profile Schema](./profile-schema.zh-CN.md)：长期工作流来源如何组织。
- [Skill Bundle](./skill-bundle.zh-CN.md)：Forma 写到磁盘上的产物是什么。
- [Verifier](./verifier.zh-CN.md)：`forma verify` 检查什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [使用说明](./usage.zh-CN.md)：完整命令参考。
