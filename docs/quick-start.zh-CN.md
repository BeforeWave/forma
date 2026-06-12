# 快速开始

英文版：[quick-start.md](./quick-start.md)

这页只讲从零跑通 Forma：让 agent 先提炼项目规则，确认后生成、验证并安装一套可试用 workflow。规则需要长期复用时，再把 profile 提交进仓库；只想试用时，profile 可以是临时文件。

## 1. 安装 CLI

先安装 Forma CLI：

```bash
pipx install forma-cli
forma --help
```

然后对 agent 说：

```text
用 Forma 给这个项目生成一套 Codex workflow。
先把你提炼出的项目规则给我看；确认后再生成并安装。
```

agent 会自己调用 Forma 的 profile 编写指南，先把项目规则整理成 profile：阶段约束、工具习惯、验证、proof 和停手条件。你确认后，它可以把 profile 存到临时路径，生成并验证 workflow 产物，再按 target 安装。

如果你要手动复现，Codex direct skill bundle 的命令形状是：

```bash
forma create-bundle --target codex --profile /tmp/myproject-profile.yaml --output /tmp/myproject-workflow
forma verify /tmp/myproject-workflow
forma install --target codex --scope project /tmp/myproject-workflow
```

## 2. 试用生成的 Workflow

安装生成产物后，新开 thread：

```text
Use forma:plan to plan this issue first.

Issue:
<粘贴当前 issue、需求描述、问题背景或任务目标>
```

Plugin 产物使用 `forma:*` 触发；如果安装的是 direct skill bundle，则使用对应的 `forma-*` skill 触发名。

第一次有效输出应该是 proposal，不是 patch。它应该先把目标、范围、项目准则和验证方式说清楚。

如果需要仓库证据，继续：

```text
Use forma:ground to gather the evidence needed for this plan.
```

证据和方案确认后，锁定 task contract：

```text
Use forma:lock to write the plan and task contract.
```

然后执行一个已接受任务：

```text
Use forma:execute to execute the next accepted task.
```

## 3. 看产物

重点看这些文件：

- `plans/issue-<id>/plan.md`：当前目标、范围、项目准则、证据路径和验证策略。
- `plans/issue-<id>/tasks.md`：有顺序的已接受任务，包括边界、验证和停手条件。
- `plans/issue-<id>/runs/`：执行 proof、验证结果和需要 review 的记录。

这个仓库自己的 Forma plans 在 [`../plans/`](../plans/)。

## 4. 复用或长期维护

如果这套规则要团队共用或长期维护，把确认后的 profile 放进版本控制。以后可以直接确定性生成：

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
| `forma explain profile` + agent | 先从项目规则生成一套 workflow，可临时试用，也可长期维护。 | profile + 已验证 workflow bundle 或 plugin。 |
| `forma create-bundle` / `forma create-plugin` | 已经有 review 过的 profile。 | 从 profile 重复生成的 workflow 产物。 |
| `forma-creator` | 可选的临场生成路径，不想先处理 profile 文件时使用。 | 已验证的一次性 skill bundle 或 plugin。 |

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
- [Profile Schema](./profile-schema.zh-CN.md)：profile 如何描述阶段约束、工具习惯、验证和 proof。
- [Forma Creator](./forma-creator.zh-CN.md)：可选临场路径和 temporary injection 如何工作。
- [Skill Bundle](./skill-bundle.zh-CN.md)：Forma 写到磁盘上的产物是什么。
- [Verifier](./verifier.zh-CN.md)：`forma verify` 检查什么。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
- [使用说明](./usage.zh-CN.md)：完整命令参考。
