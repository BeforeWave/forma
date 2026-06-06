# Forma

**面向项目专属 Agent 工作流的编译器。**

Forma 把 workflow profile 编译成可安装到 Codex 或 Claude Code 的可移植
skill bundle。

它给 Coding Agent 装上一根主心骨：让 Agent 如何澄清、取证、规划、执行、
验证和继续，变得显式、可版本化、可迁移、可验证。

Forma 不是运行时 Agent，不是通用技能创建器，也不是又一个提示词模板。

Profile 是源码。生成出来的 skill bundle 是部署产物。

英文文档：[README.md](./README.md)

## 为什么需要 Forma

AI coding 改变了项目里什么东西算作重要资产。

代码、测试、文档、issue 和 review comment 仍然重要。但当 coding agent 进入开发流程后，另一个资产变得关键：

> Agent 在改代码之前和改代码过程中遵守的工作流。

团队需要定义：Agent 必须澄清什么、必须收集哪些证据、计划什么时候变成可执行契约、可以改什么、什么时候必须停下，以及验证证明如何记录。

这些规则常常散落在提示词、`AGENTS.md`、自定义技能、review 习惯和团队记忆里。Forma 给它们一个源码格式和一个编译器。

## 心智模型

```text
workflow profile  ->  Forma compiler  ->  skill bundle
源码                  编译器              可安装产物
```

Forma 编译：

```text
profile YAML
+ 标准方法
+ 目标环境适配器
+ 可选一次性注入
        |
        v
目标环境专用 skill bundle
+ 协同阶段技能
+ references 和 scripts
+ .forma-manifest.json 溯源信息
+ 可被 verifier 检查的结构
```

同一个 workflow profile 可以生成到不同 Agent 环境，而不是为每个工具手写一套规则。

## 工作流

一个常见的 Forma 生成套件包含五个协同阶段：

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

| 阶段 | 更直白的说法 | 做什么 |
|---|---|---|
| `shape` | 澄清请求 | 把松散需求收敛成有边界的方案。 |
| `gauge` | 先读再动 | 在规划前收集仓库、Spec、文档和相关证据。 |
| `seal` | 锁定计划 | 把方案变成已接受的任务契约。 |
| `pour` | 在边界内执行 | 只执行一个已接受任务，并记录证明。 |
| `flow` | 安全继续 | 从 sealed plan 继续，或者在缺少证明时停下。 |

这些名字只是默认值，不是产品本身。项目可以重命名生成技能，同时保留底层阶段语义；见 [使用说明：重命名生成技能](./docs/usage.zh-CN.md#重命名生成技能)。

## Forma 增加了什么

Spec 文档、规划模板、静态技能和仓库指令可以帮助 Agent 理解需求。

Forma 做的是更窄、更硬的一件事：打包 workflow contract 本身。

它定义规划前必须收集哪些证据、计划什么时候变成可执行契约、当前哪个任务已被接受、什么验证结果算证明，以及什么时候必须停止继续。

所以 Forma 带来的不只是更好的计划文档，而是一条可安装的工作回路，约束 Agent 如何从需求到证据、从证据到计划、从计划到执行、再从执行到安全继续。

## Forma 属于哪一层

Forma 位于 Agent workflow 这一层。

- Spec 工具和规划文档定义应该做什么。
- `AGENTS.md` 和仓库文档定义本地上下文和约定。
- 通用技能创建器打包可复用能力。
- Forma 把项目专属工作流规则编译成可部署的 skill bundle。

Forma 不替代这些层，而是约束 Agent 按更稳定的顺序使用它们。

## 什么时候用

当 AI coding 已经是常规开发方式，并且团队希望同一套规划、证据、验证和停止条件能稳定约束多次 Agent 执行时，用 Forma。

如果问题只是几条仓库规则、一个孤立的可复用能力，或者基础的需求/Spec 事实组织，通常不需要 Forma。那些场景用 `AGENTS.md`、单个自定义技能或 Spec 工具更合适。

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

## 文档

- [快速开始](./docs/quick-start.zh-CN.md)：安装、生成工作流、构建 `forma-creator`。
- [核心概念](./docs/concepts.zh-CN.md)：心智模型、适用边界、生态位比较、profile 和注入路径。
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
