# Forma

**给你的 Coding Agent 装上一根主心骨。**

Forma 把团队的工程纪律——规划、证据、边界和验证——变成可安装到 Codex 或 Claude Code 的 Plan-First 工作流。

Agent 先读再动、先计划再改代码、只执行已接受任务，并留下验证证明。

它不是又一个提示词，也不是又一个 Spec 工具。它是面向严肃 AI-assisted engineering 的 workflow compiler。

Forma 是生成器，不是运行时工作流本身。真正被 Codex 或 Claude Code 使用的是生成出来的技能套件。

英文文档：[README.md](./README.md)

## 为什么需要 Forma

AI coding 很强，但没有工作流时，它很容易把上下文、计划、实现和验证压成一个临场步骤。

漂移通常就发生在这里：Agent 读附近刚好可见的材料，顺手改任务外文件，为了方便扩大范围，或者没有证明就声称已经验证。

Forma 把团队本来就在意的工程纪律——规划、证据、边界、验证和评审——变成 Agent 能真正遵守的可复用工作流。

## 工作流

Forma 生成分阶段的 Agent 工作流：

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

每个阶段都有自己的职责：

| 阶段 | 更直白的说法 | 做什么 |
|---|---|---|
| `shape` | 澄清请求 | 把松散需求收敛成有边界的方案。 |
| `gauge` | 先读再动 | 在规划前收集仓库、Spec、文档和相关证据。 |
| `seal` | 锁定计划 | 把方案变成已接受的任务契约。 |
| `pour` | 在边界内执行 | 只实现一个已接受任务，不顺手扩大范围。 |
| `flow` | 安全继续 | 从 sealed plan 继续，或者在缺少证明时停下。 |

不喜欢这些名字？没事。Forma 支持把生成技能改成项目自己的叫法，规则见 [使用说明：重命名生成技能](./docs/usage.zh-CN.md#重命名生成技能)。

## Forma 生成什么

Forma 会组合可复用 profile 来源、标准 Plan-First 方法、目标 Agent 环境和可选的一次性生成约束：

```text
profile YAML
+ 标准方法
+ 目标环境 = codex | claude-code
+ 可选一次性注入
        |
        v
可安装的工作流套件
+ 五个协同技能
+ references 和 scripts
+ .forma-manifest.json 溯源信息
+ 可被 verifier 检查的结构
```

这些生成技能不是零散提示词。它们是一条项目自己的 Agent 工作回路：澄清、取证、定稿、执行，并带着证明继续。

## Forma 增加了什么

Spec 文档、规划模板、静态技能和仓库指令可以帮助 Agent 理解需求。

Forma 做的是更窄、更硬的一件事：打包 workflow contract 本身。

它定义规划前必须收集哪些证据、计划什么时候变成可执行契约、当前哪个任务已被接受、什么验证结果算证明，以及什么时候必须停止继续。

所以 Forma 带来的不只是更好的计划文档，而是一条可安装的工作回路，约束 Agent 如何从需求到证据、从证据到计划、从计划到执行、再从执行到安全继续。

## 什么时候用

当 AI coding 已经是常规开发方式，并且团队希望同一套规划、证据、验证和停止条件能稳定约束多次 Agent 执行时，用 Forma。

如果只是几条仓库规则，用 `AGENTS.md`。如果只是一个可复用能力，用单个自定义技能。如果主要问题是组织需求和 Spec 事实，用 OpenSpec、Spec Kit、Kiro 这类 Spec 工具。

完整的方法论、适用边界和生态位比较放在 [核心概念](./docs/concepts.zh-CN.md)。

## 快速试一下

确认 `forma` 已经在 `PATH` 里之后，生成并验证一个 Codex 工作流套件：

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex

forma verify /tmp/backend-plan-first-codex
```

构建一个目标固定的 `forma-creator`：

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma verify /tmp/forma-creator-dist/codex/forma-creator
```

完整首次跑通路径、安装位置、Claude Code 输出和 profile 编写细节见 [快速开始](./docs/quick-start.zh-CN.md)。

## 两种入口

**从长期 profile 生成。** 适合已经评审并提交为源码的团队或项目规则。

```bash
forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
```

**使用 `forma-creator`。** 适合已经评审过的一次性工作流想法。安装后的 creator 会帮助把已评审的自然语言工作流想法整理成 temporary injection JSON，再生成目标 Agent 专用套件，并在交付前验证。

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

外部 Agent 需要编写规则但不能阅读本源码树时，可以让 Forma 输出指南：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

## Forma 属于哪一层

Forma 位于 Agent workflow 这一层。

- Spec 工具和规划文档定义应该做什么。
- `AGENTS.md` 和仓库文档定义本地上下文和约定。
- 通用技能创建器打包可复用能力。
- Forma 打包项目自己的工作流，约束 Agent 如何澄清、取证、规划、执行、验证，以及如何安全继续。

Forma 不替代这些层，而是约束 Agent 按更稳定的顺序使用它们。

## 文档

- [快速开始](./docs/quick-start.zh-CN.md)：安装、生成工作流、构建 `forma-creator`。
- [核心概念](./docs/concepts.zh-CN.md)：方法论、适用边界、生态位比较、profile 和注入路径。
- [使用说明](./docs/usage.zh-CN.md)：命令参考、仓库检查、安装后行为。
- [STRUCTURE.md](./STRUCTURE.md)：当前源码结构和边界。

## Forma 自身也使用 Forma

Forma 自己的规划和开发，也走 Forma 生成的 workflow。支撑这条回路的 self profiles 在：

- [profiles/forma-self/forma-self-iteration.yaml](./profiles/forma-self/forma-self-iteration.yaml)
- [profiles/forma-self/base.yaml](./profiles/forma-self/base.yaml)
- [profiles/forma-self/iteration-overlays.yaml](./profiles/forma-self/iteration-overlays.yaml)
- [profiles/forma-self/project.yaml](./profiles/forma-self/project.yaml)

## 许可证

Apache-2.0，见 [LICENSE](./LICENSE)。
