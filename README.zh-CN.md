# Forma

**把你的 Spec 纪律变成可复用的 Agent workflow。**

Forma 把一个项目长期形成的规划规则、证据要求、验证门槛和执行边界，生成可安装到 Codex 或 Claude Code 的 Spec Plan-First 工作流技能。

它适合已经要求 Agent 按 Spec、计划、证据和验证来工作，而不是只靠一次性提示词的人和团队。

英文文档：[README.md](./README.md)

## 变化

AI coding 之后，项目的一等资产不再只有代码。

Agent 执行的 Spec、遵守的流程约束、规划时读取的证据、定稿后的计划、执行后留下的证明，都会进入项目生命周期。

过去，团队风格主要体现在命名、架构、模块边界、测试习惯和评审标准里。现在，它也会体现在 Agent 如何工作：先读什么、怎么规划、何时停下、怎么验证、如何留证。

不同团队会形成不同的 Spec-driven development 方法、规划习惯、验证预期和流程约束。它们会像过去的代码风格一样，塑造项目的长期质量。

Forma 做的就是让这套风格成形。

## Forma 是什么

Forma 是生成器，不是运行时工作流本身。

它把项目自己的工作流规则、Plan-First 方法、目标 Agent 界面和可选的一次性生成约束组合起来，生成项目专属的 Spec Plan-First 工作流套件。

```text
Forma 组合：
  项目 profile：可复用的工作流规则和约束
  方法论：Plan-First 阶段、门槛和留证要求
  目标界面：Codex 或 Claude Code
  可选一次性注入：本次生成专用的临时约束

生成：
  可安装、目标界面专用的工作流技能
```

这些生成出来的技能，再约束 Agent 如何读取 PRD、issue、spec、任务计划、brief、仓库证据和验证结果。

它关心的不是“多写一个提示词”，而是把规则放到正确位置：默认约束、阶段约束、场景规则、资源文件、来源适配器。

## Forma 生成什么

Forma 生成的套件，才是 Agent 实际使用的工作流。

安装到 Codex 或 Claude Code 后，它通常由五个协同技能组成：

```text
shape -> gauge -> seal -> pour -> flow
```

- `shape`：把需求收敛成有边界的方案；
- `gauge`：只读收集仓库、Spec、文档和历史证据；
- `seal`：把计划和任务固定成可评审、可验证的执行契约；
- `pour`：只执行一个已接受任务，并记录证明；
- `flow`：只有计划允许时才继续推进。

这些技能不是零散提示词。它们是一条项目自己的 Agent 工作回路。

不喜欢这些名字？没事。Forma 支持把生成技能改成项目自己的叫法，规则见 [使用说明：重命名生成技能](./docs/usage.zh-CN.md#重命名生成技能)。

## 为什么重要

Forma 让 Agent 工作变得：

- **可重复**：项目规则有固定位置和生命周期，不只存在于上下文窗口；
- **分阶段**：澄清、取证、定稿、执行、证明不会混成一团；
- **有边界**：执行限制在已接受任务内，降低顺手扩大范围的风险；
- **可评审**：评审者不只看到 diff，还能看到 Agent 如何从 Spec 走到实现；
- **可迁移**：同一套工作流风格可以生成到不同 Agent 界面。

## 谁适合：软件团队？以及不止于此

软件团队是 Forma 最自然的起点。如果你已经把 AI coding 当作常规开发方式，并且反复遇到这些情况，你可能需要 Forma：

- 同一个 Spec，不同 Agent 会读不同材料、漏不同验证；
- 团队有明确的 Spec、规划、验证习惯，但散落在文档、提示词和历史经验里；
- 仓库有多条工作路线，例如后端、迁移、生成基线、文档、治理、跨层改动；
- 你希望 Agent 先形成可评审计划，而不是直接跳到实现；
- 你想让 Codex、Claude Code 或其他 Agent 界面遵守同一套项目工作流。

如果只是偶尔让 Agent 改小文件，`AGENTS.md`、普通提示词或单个技能通常已经够用。

Forma 不只属于软件开发：只要你的工作也依赖“先读什么、怎么计划、谁来验收、留下什么证明”，同一套工作流模式就可能适用。哪些工作适合，见 [核心概念：不只软件开发](./docs/concepts.zh-CN.md#不只软件开发)；不同角色怎么用，见 [不同人怎么用 Forma](./docs/concepts.zh-CN.md#不同人怎么用-forma)。

Forma 面向的是想把工作方式产品化、复用化、可审查化的人。

## Forma 在哪里

Forma 和 OpenSpec、Spec Kit、Kiro 这类 Spec 工具不在同一层。那些工具组织需求和事实；Forma 生成 Agent 读取、整理和处理这些材料时要遵守的工作流。

Forma 也不是 Codex `skill-creator` 或 Claude Code Skill Creator 这类通用技能创建器。那些工具创建能力；Forma 创建项目工作流。

Forma 也不替代 `AGENTS.md`。`AGENTS.md` 让 Agent 读到规则；Forma 让可复用规则进入分阶段工作流。

```text
Spec 工具组织需求和事实。
通用技能创建器创建能力。
AGENTS.md 给出仓库级指引。
Forma 把你的 Spec 纪律变成可复用的 Agent workflow。
```

## 文档

- [快速开始](./docs/quick-start.zh-CN.md)：安装、生成工作流、构建 `forma-creator`。
- [核心概念](./docs/concepts.zh-CN.md)：核心概念、生态位比较、profile 和注入路径。
- [使用说明](./docs/usage.zh-CN.md)：命令参考、仓库检查、安装后行为。
- [STRUCTURE.md](./STRUCTURE.md)：当前源码结构和边界。

## 两种入口

Forma 有两种常见入口。

### 让 Agent 帮你写 profile

想把某个项目的长期工作流规则沉淀下来，就在项目里对 Agent 说：

```text
运行：
  forma explain profile --target codex

把命令输出当作 profile 编写标准。
检查当前仓库，并提出一个可提交、可维护的 Forma profile 方案。

请找出：
- 权威需求来源；
- 规划和取证要求；
- 验证命令和证明要求；
- 只属于特定阶段的约束；
- 反复出现的工作路线和场景规则；
- 应该显式声明的来源读取脚本或辅助脚本。

先不要写文件。
先展示建议的 profile 结构，解释每条约束应该放在哪里，
并标出需要人确认的未知项。
```

这条路适合把真实存在的团队习惯沉淀成长期 profile。

### 用 `forma-creator` 快速试工作流想法

不想先设计完整 profile？装好目标 Agent 专用的 `forma-creator`，然后把想法直接交给 Agent：

```text
使用 forma-creator，把下面这些工作流想法生成成本仓库的 Plan-First 套件。

我想试的规则：
- 规划前先确认真正的权威来源；
- 只读取当前范围需要的证据；
- 每个任务都写清验收条件和验证要求；
- 一次只执行一个已接受任务；
- 遇到 API、数据库、生成基线或跨层改动时先停下，除非计划明确允许继续。

生成前先说明这些规则会如何分类。
生成后验证套件。
```

这条路适合快速试手感。好用的规则，再沉淀进长期 profile。

## 快速试一下

确认 `forma` 已经在 `PATH` 里之后，生成并验证一个工作流套件：

```bash
forma --help
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
forma verify /tmp/backend-plan-first-codex
```

构建一个目标固定的 `forma-creator`：

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

安装路径、Claude Code 输出和 profile 编写细节见 [快速开始](./docs/quick-start.zh-CN.md)。

## Forma 管理 Forma

btw：Forma 自己的规划和开发，也走 Forma 生成的 workflow。支撑这条回路的 self profiles 在：

- [profiles/forma-self/forma-self-iteration.yaml](./profiles/forma-self/forma-self-iteration.yaml)
- [profiles/forma-self/base.yaml](./profiles/forma-self/base.yaml)
- [profiles/forma-self/iteration-overlays.yaml](./profiles/forma-self/iteration-overlays.yaml)
- [profiles/forma-self/project.yaml](./profiles/forma-self/project.yaml)

## 许可证

Apache-2.0，见 [LICENSE](./LICENSE)。
