# 核心概念

英文版：[concepts.md](./concepts.md)

这页解释 Forma 的心智模型。

建议先读 README，再读本页，最后再写复杂 profile。

Forma 最容易理解成三层：

1. **Forma 本体**：生成器和工具链。
2. **生成套件**：安装到 Codex 或 Claude Code 的工作流技能。
3. **Profile 和一次性注入**：长期规则和一次性规则的输入层。

Forma 不直接执行项目任务。它生成的是 Agent 执行任务时要遵守的工作流。

---

## Forma 的层次

### Forma 本体

Forma 读取 profile、标准 Plan-First 方法、目标环境规则，以及可选的一次性生成约束。

它输出目标环境专用的工作流套件。

### Forma 生成的套件

生成套件才是 Codex 或 Claude Code 实际使用的内容。

一个常规 Plan-First 套件包含五个协同技能，对应同一套工作流阶段：

```text
clarify -> gather evidence -> lock plan -> execute task -> continue safely
shape   -> gauge          -> seal      -> pour         -> flow
```

### Profile 和一次性注入

Profile 保存长期项目规则，应该像源码一样被评审。

一次性注入保存本次生成使用的临时约束，不应该在未经评审时变成长期策略。

---

## Forma 生成什么

Forma 的输出是可安装的工作流套件。

具体技能名和目录名可以被 profile 或一次性注入重命名，但语义阶段保持不变：

| Forma 阶段 | 当前含义 | 更直白的用户叫法 |
|---|---|---|
| `shape` | 有边界的方案 | Plan Issue / 澄清需求 |
| `gauge` | 证据收集 | Ground Plan / 理解现状 |
| `seal` | 执行契约 | Finalize Plan / 锁定验收和验证 |
| `pour` | 带证明的已接受任务 | Implement Feature / 执行一个任务 |
| `flow` | 受控继续 | Continue Work / 只在安全时继续 |

输入和输出可以这样理解：

```text
profile YAML
+ 标准方法
+ 可选一次性注入
+ 目标环境 = codex | claude-code
        |
        v
Forma compiler
        |
        v
目标环境专用工作流套件
+ 协同技能
+ profile 或注入选中的 references 和 scripts
+ .forma-manifest.json 溯源信息
+ 可被 verifier 检查的结构
```

`shape` / `gauge` / `seal` / `pour` / `flow` 是 Forma 的内部阶段隐喻。项目可以重命名生成技能和展示名，但阶段语义不变。

---

## 为什么重要

Forma 的价值不是“帮你写代码”。它不直接写业务任务。

Forma 的价值是把团队反复强调的 AI 工作纪律，变成可版本化、可安装、可验证的 workflow source。

它让 Agent 工作更容易做到：

- **可重复**：长期规则有固定来源和生命周期；
- **分阶段**：澄清、取证、规划、执行和证明不会混成一个提示词；
- **有边界**：实现限制在已接受任务内，不因顺手而扩大范围；
- **可评审**：reviewer 能看到从需求、证据、计划、执行到证明的路径；
- **可迁移**：同一套工作流风格可以生成到支持的目标环境。

---

## 核心资产

Forma 有用，是因为 workflow 被表示成源码，而不是记忆。

### Profiles

Profiles 记录长期项目规则：

- 权威来源预期；
- 验证命令；
- 阶段约束；
- 场景路线；
- 生成技能资源；
- 显式来源适配器。

Profile 应该由人评审和维护。Agent 可以辅助起草，但临时想法不应在未经评审时变成长期 profile source。

### Manifests

生成套件包含 `.forma-manifest.json`。

Manifest 记录目标环境、方法版本或 digest、解析后的 profile stack、profile hash、生成技能和 generator 溯源。

### Verification

`forma verify` 检查生成的 Plan-First 套件和 `forma-creator` 套件是否满足结构和方法一致性。

验证不替代内容评审。它的作用是避免生成结果只是一堆未经检查的 Markdown。

---

## 什么时候不要用 Forma

Forma 比仓库指令文件或单个自定义技能更重。

如果问题只是“让 Agent 记住几条规则”，不要先上 Forma。

可以这样选：

- 仓库级规则够用时，用 `AGENTS.md`；
- 只需要一个可复用能力时，用一个 Codex 或 Claude Code 技能；
- 主要问题是组织需求和 Spec 事实时，用 OpenSpec、Spec Kit、Kiro 这类工具。

当反复出问题的是 Agent 的整条工作回路时，再用 Forma：

- 先澄清什么；
- 必须读什么；
- 如何把证据变成计划；
- 什么时候允许执行；
- 用什么验证结果证明完成；
- 什么时候必须停止继续。

---

## 第一次跑通应该是什么样

最有用的 demo 是一条具体路径：

1. 选择一个小 sample profile。
2. 生成 Codex 或 Claude Code 工作流套件。
3. 验证生成结果。
4. 安装到对应 Agent 的技能目录。
5. 触发一个 Plan-First 任务。
6. 检查计划、任务契约、验证结果和执行证据。
7. 等工作流证明有用后，再调整 profile。

本仓库里的 sample 就是为了支撑这条路径：

- `examples/profiles/sample-software/` 展示通用软件 Plan-First 工作流；
- `examples/profiles/sample-backend/` 展示 Spec / issue 驱动的后端工作流，包括来源读取、规划、验证和执行边界；
- `examples/generated/*-codex/` 和 `examples/generated/*-claude-code/` 展示生成到不同目标环境的技能。

不要一开始就设计完美 profile。先生成一个小工作流，跑一个计划内任务，再把真正有用的规则沉淀进长期 profile。

---

## 谁适合

Forma 主要适合已经经常使用 AI Agent，并且希望 Agent 按稳定流程工作的团队和个人。

最直接的场景是软件工作：

- 个人高频 AI coding 用户沉淀自己的工作习惯；
- 工程团队把 Spec-first、review、testing、migration、generated-baseline、API boundary 等规则写进 profile；
- 研发效能和平台团队用可安装套件产品化团队的 Agent 使用方式；
- 技术负责人和 reviewer 要求 Agent 先给计划、证据和验证路径，再动手；
- 产品经理或 Spec owner 让 Agent 留在需求边界内。

Forma 也可以用于软件之外的重复工作，只要这类工作具备：

- 明确目标或类似 Spec 的输入；
- 必须优先读取的来源；
- 不能越界的边界；
- 可区分的阶段；
- 验证或验收；
- 给 reviewer 留下证明的需求。

例如研究、分析、出版、设计评审、客户交接、治理和运营工作。

但不是所有任务都需要 Forma。如果一件事没有稳定来源、没有边界、没有验收路径，也不需要复用，直接提示词更快。

---

## 软件之外的小例子

一个研究团队可以用 Forma 生成这样的工作流：

- `shape`：先澄清研究问题、受众、范围和引用标准；
- `gauge`：只读指定来源目录、笔记、数据集和历史备忘录；
- `seal`：写出带验收条件、来源覆盖和 caveat 的大纲；
- `pour`：一次只起草一个已接受章节，并记录每个论断由哪些来源支撑；
- `flow`：只有大纲、来源限制和评审规则仍然成立时，才继续推进。

生成技能不会神奇地让 Agent 变成更好的研究员。它做的是把团队已有的研究纪律显式化，让它能被复用、评审和改进。

---

## Spec 工具和 Forma

OpenSpec、Spec Kit、Kiro 和其他 Spec-driven 流程，会让需求层更显式。

它们通常关注需求、提案、设计、差量、任务清单，以及 Spec 和实现的一致性。

Forma 不替代这些材料，也不把它们当成生成器的主要输入。Forma 生成的是 Agent 工作流，让 Agent 按项目规则读取、整理和处理这些材料。

```text
Spec 工具组织需求和事实。
Forma 组织 Agent 围绕这些事实工作的流程。
```

所以 Forma 可以独立工作，也可以和 Spec 工具链一起工作。

---

## 通用技能创建器和 Forma

通用技能创建器创建能力。

例如：

```text
创建一个评审 API 改动的技能。
创建一个撰写发布说明的技能。
创建一个审查安全风险的技能。
```

Forma 围绕工作流组织。它生成的是项目期望 Agent 推进工作的方式：

```text
shape -> gauge -> seal -> pour -> flow
```

差异在归属：

- 通用技能属于某个能力；
- Forma 生成的套件属于某个项目工作流；
- 通用技能说明怎么执行一个动作；
- Forma 生成的套件说明一项工作如何规划、取证、设边界、执行和留证。

---

## AGENTS.md 和 Forma

`AGENTS.md` 是仓库级指令入口。

它适合写：

- 当前仓库的入口规则；
- Agent 应该先读哪些文件；
- 仓库边界；
- 默认命令；
- 当前 checkout 的特殊注意事项。

Forma 不替代 `AGENTS.md`。

Forma 适合处理可复用、可分类、需要进入工作流阶段的规则。

例如，`AGENTS.md` 可以写：

```text
迁移工作必须检查 schema 文件和生成基线，并运行迁移验证。
```

在 Forma 里，它可以进入工作流结构：

- `shape`：识别当前任务是否选择迁移路线；
- `gauge`：收集 schema 和基线证据；
- `seal`：把迁移验证写进任务契约；
- `pour`：执行已接受任务时运行验证；
- `flow`：如果迁移路线不允许自动继续，就停住。

`AGENTS.md` 让 Agent 读到规则。Forma 让规则进入工作流。

---

## Profile

Profile 是项目可维护的工作流来源，不是提示词堆。

它记录长期稳定的规则：

- 权威 Spec 来源；
- 规划证据要求；
- 验证门槛；
- 阶段约束；
- 场景规则；
- 生成技能需要携带的引用材料；
- 显式来源适配器。

Profile 应该由人评审和维护。

---

## 一次性注入

一次性注入是临时规则入口。

适合：

- 本次生成需要的特殊约束；
- 还没稳定到 profile 的规则；
- 私有来源读取器；
- 一次性验证门槛；
- 用户当场给出的有范围指令。

一次性注入不应该直接复制 README、AGENTS、issue 原文或大段项目文档。它应该先分类，再生成 JSON。

---

## 阶段约束

不是所有规则都应该全局生效。

Forma 把规则放进不同工作流阶段：

- `shape`：需求澄清、范围、路线、计划策略；
- `gauge`：收集证据和依据；
- `seal`：计划和任务定稿、验证契约；
- `pour`：单任务执行和证明；
- `flow`：自动继续执行的边界。

这避免所有规则都挤在一个提示词里，让 Agent 每次自己判断。

---

## 生成技能质量

一个生成技能应该只有一个清晰职责。

如果某个 `SKILL.md` 变成大段制度文档，就把稳定细节移到 `references/`，把路线专用规则放到场景规则，或把能力专用指引拆成单独技能。

好的生成套件通常有：

- 短而明确的 skill description；
- 按阶段分布的指令，而不是一个全局规则堆；
- 只在需要时加载的浅层 references；
- 只有 profile 或一次性注入明确拥有时才出现的 scripts 和来源适配器；
- 轻量的 `constraints.default`；
- 每个阶段都有清楚的验证或证明路径。

生成器不应该只是把所有规则贴进所有技能。

---

## 场景规则

某些规则只在特定场景生效。

例如：

- 文档改动；
- 后端改动；
- 迁移；
- 生成基线；
- 治理；
- 跨层改动。

这些规则适合放进场景规则，而不是默认约束。

默认层应该轻。重规则应该按阶段或场景启用。

---

## 来源适配器

来源适配器是显式来源读取器或辅助脚本。

例如：

- issue 读取器；
- 文档导出器；
- 私有知识助手；
- 本地来源查询脚本。

它们不是 Forma 的基础能力。只有 profile 或一次性注入明确拥有它们时，生成套件才应该使用。
