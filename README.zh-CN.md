# Forma

**面向项目专属 Agent 工作流的编译器。**

输入 profile，输出 skill bundle。默认方法是 Plan-First。

Forma 把项目专属 workflow profile 编译成 skill bundle；这些 bundle 可安装到 Codex、Claude Code 这类 Agent 编码环境。

它内置 Plan-First 工程方法：先澄清需求，再收集证据，锁定计划，一次执行一个任务，并且只在明确边界内继续。

英文文档：[README.md](./README.md)

## 为什么需要 Forma

Agent 可以跑得很快。难的是第一句 prompt 之后，怎么让工作不跑偏。

AI coding 改变了项目里什么东西算作重要资产。

代码、测试、文档、issue 和评审意见仍然重要。但当编码 Agent 进入开发流程后，另一个资产变得关键：

> Agent 在改代码之前和改代码过程中遵守的工作流。

团队需要定义：Agent 必须澄清什么、必须收集哪些证据、计划什么时候变成可执行契约、可以改什么、什么时候必须停下，以及验证证明如何记录。

这些规则常常散落在提示词、`AGENTS.md`、自定义技能、评审习惯和团队记忆里。Forma 给它们一个源码格式和一个编译器。

Forma 背后的判断很简单：工作流规则如果只存在于对话里，Agent 很容易忘。

把工作流放进文件。拆成阶段。让证明成为流程的一部分。

这不是魔法保证，但它给团队一个更好用的控制点。

## 心智模型

```text
workflow profile  ->  Forma compiler  ->  skill bundle
工作流源码              编译器              可安装产物
```

Forma 编译：

```text
profile YAML
+ 标准方法
+ target 适配器
+ 可选一次性注入
        |
        v
target 专用 skill bundle
+ 协同阶段技能
+ references 和 scripts
+ .forma-manifest.json 溯源信息
+ 可被 verifier 检查的结构
```

同一个 workflow profile 可以生成到不同 target，而不是为每个工具手写一套规则。

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

不习惯 `shape` / `gauge` / `seal` / `pour` / `flow` 这几个名字？没事。
它们是默认名，不是教条。项目可以重命名生成技能，同时保留底层阶段语义；见 [使用说明：重命名生成技能](./docs/usage.zh-CN.md#重命名生成技能)。

## Forma 增加了什么

Spec 文档、规划模板、静态技能和仓库指令可以帮助 Agent 理解需求。

Forma 增加的是更窄的控制面：

- 工作流源码格式：profiles；
- 编译产物：skill bundles；
- 评审入口：manifest、阶段、验证点和证明。

所以 Forma 带来的不是又一份计划文档，而是一条可安装的工作回路。

## Forma 属于哪一层

Forma 不是又一个提示词模板，也不是又一个 Spec 工具。它位于 Agent 工作流这一层。

- Spec 工具和规划文档定义应该做什么。
- `AGENTS.md` 和仓库文档定义本地上下文和约定。
- 通用技能创建器打包可复用能力。
- Forma 把项目专属工作流规则编译成可以安装的 skill bundle。

Forma 不替代这些层，而是约束 Agent 按更稳定的顺序使用它们。

## 什么时候用

当难点不是某一次改动、起草或分析，而是“这类工作每次应该怎样发生”时，用 Forma。

最直接的场景是 AI coding：Spec、仓库证据、计划、已接受任务、验证和评审证明。但这个模式不只属于写代码。只要一类重复 Agent 工作依赖来源、边界、阶段、审批和证明，Forma 都可能合适。

如果只是让 Agent 改个错别字、总结一页材料，或记住几条仓库规则，Forma 确实太重。那些场景用 `AGENTS.md`、直接 prompt、单个自定义技能或 Spec 工具更合适。

完整适用边界和心智模型见 [核心概念](./docs/concepts.zh-CN.md)。

## 快速试一下

确认 `forma` 已经在 `PATH` 里之后，生成、验证并安装一个 Codex 工作流 bundle：

```bash
forma create-bundle --target codex --output /tmp/forma-codex-bundle
forma verify /tmp/forma-codex-bundle
forma install --target codex --scope project /tmp/forma-codex-bundle
```

或者生成一个 Codex plugin：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma verify /tmp/forma-codex-plugin
forma install --target codex --scope project /tmp/forma-codex-plugin
```

给 Agent 的快速安装话术：

- Codex plugin：「安装 `<artifact-url-or-path>` 里的 Forma Codex plugin，
  先验证，再用 `forma-plan` 做第一轮规划。」
- Skill bundle：「把 `<artifact-url-or-path>` 里的 Forma skill bundle
  安装到 Codex 或 Claude Code，先验证，再在计划阶段用 `forma-plan`，
  计划就绪后用 `forma-showhand`。」
- Creator skill：「安装 `<artifact-url-or-path>` 里的目标专用
  `forma-creator` skill，然后用它生成并验证一次性的 Plan-First workflow bundle。」

已提交的生成示例和 `dist/` 产物是安装入口和漂移检查基线，不是 Agent 真实运行效果的证明。

完整首次跑通路径、安装位置、Claude Code 输出和 profile 编写细节见 [快速开始](./docs/quick-start.zh-CN.md)。

## 两种入口

**从长期 profile 生成。** 适合已经评审并提交为源码的团队或项目规则。

```bash
forma create-bundle \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
```

**使用 `forma-creator`。** 适合已经评审过的一次性工作流想法。安装后的 creator 会帮助把已评审的自然语言工作流想法整理成 temporary injection JSON，再生成目标 Agent 专用套件，并在交付前验证。

还没准备好设计完整 profile？先试手感。真正经得起使用的规则，再沉淀进长期 profile。

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
```

外部 Agent 需要编写规则但不能阅读本源码树时，可以让 Forma 输出指南：

```bash
forma explain profile --target codex
forma explain temporary-injection --format json --target codex
```

## 文档

- 开始使用：[快速开始](./docs/quick-start.zh-CN.md)、[Examples](./docs/examples.zh-CN.md)。
- 理解概念：[核心概念](./docs/concepts.zh-CN.md)、[Workflow Contract](./docs/workflow-contract.zh-CN.md)、[Skill Bundle](./docs/skill-bundle.zh-CN.md)。
- 参考资料：[Profile Schema](./docs/profile-schema.zh-CN.md)、[Forma Creator](./docs/forma-creator.zh-CN.md)、[Verifier](./docs/verifier.zh-CN.md)、[Targets](./docs/targets.zh-CN.md)、[使用说明](./docs/usage.zh-CN.md)。
- [STRUCTURE.md](./STRUCTURE.md)：当前源码结构和边界。

## Forma 编译自己的工作流

Forma 用自己编译出来的工作流，管理 Forma 自己的规划和开发。

支撑这条回路的 self profiles 在：

- [profiles/forma-self/forma-self-iteration.yaml](./profiles/forma-self/forma-self-iteration.yaml)
- [profiles/forma-self/base.yaml](./profiles/forma-self/base.yaml)
- [profiles/forma-self/iteration-overlays.yaml](./profiles/forma-self/iteration-overlays.yaml)
- [profiles/forma-self/project.yaml](./profiles/forma-self/project.yaml)

## 许可证

Apache-2.0，见 [LICENSE](./LICENSE)。
