<p align="right">
  <a href="./README.md">English</a> | <a href="./README.zh-CN.md">中文</a>
</p>

# Forma

**一句话定制项目 workflow，让 agent 按团队准则规划、验证和交付。**

Coding agent 在真实项目里出问题，通常不是不会写代码，而是还没把团队的交付规则落到当前任务，就开始实现。

很多团队已经有 agent-facing docs，也会接入通用的“先计划、再执行”工作流。它们能让 agent 读规则、按阶段写计划，但固定流程不等于团队准则；计划仍然可能缺少当前任务可以依赖和验证的约束细节。

Forma 做的就是把这层缺口补上。你可以直接告诉 agent：

```text
请用 Forma 为这个项目定制 workflow，从文档和代码里挖掘工程准则，生成后让我体验。
```

此时 Forma 会先帮团队理清最关切的实践准则，再生成守护这些准则的 workflow。这个 workflow 会盯住 agent 的规划、验证、proof 和停手条件，让当前任务按团队准则推进。

---

## Forma 怎么做

Forma 让 agent 按项目事实梳理准则：权威资料、修改边界、工具要求、验证深度、proof 和停手条件。

先试一套 workflow 时，准则进入本次生成的可试用产物；长期维护时，准则沉淀到团队可 review、可维护的 profile。

任务开始后，workflow 推动 agent 产出 task contract，并在取证、实现、验证和 proof 记录里守住这些准则。

---

## 同一个目标，不同的审查标准

同一个产品目标，通用工作流会让 agent 走相似阶段：理解目标、读取证据、写计划、实现、验证。Forma 改变的是这份计划必须按什么项目准则才算能被接受。

接下来用同一个目标看这种差异：团队最关切的准则不同，agent 动手前必须交代的事实、边界、验证和停手条件也会不同。

```text
Product goal:
Ship rate limiting for the settings experience.
```

### API contract 约束更重的 backend

项目最关切的是：接口事实不能只来自 issue，API 兼容性判断必须早于实现，generated output 必须能追溯到 generator proof。

```text
Task contract 摘录:
  Focus: 先完成 API impact 分类，再进入 handler 实现。
  Evidence: GitHub issue comments / linked commits；contracts/api/v1/settings.yaml.
  Tasks:
    1. contract-impact: 标记 none / additive / breaking，并决定是否更新 contract。
    2. implementation: 在不改变 public response shape 的前提下加入 limiter。
    3. generated-proof: contract 变化时运行 generator，记录 generated diff 来源。
  Boundary: API impact 没分类前，不开始 handler 修改。
  Validate: contract compatibility check；generated output check；focused handler test.
  Stop if: issue comments 和 API contract 冲突；
           generated files 变化但没有 generator proof；
           兼容性判断需要 API/product review。
```

### Runtime behavior 约束更重的 backend

项目最关切的是：限流必须落在已有运行控制里，本地测试能覆盖关键行为，接口同步不能早于行为稳定。

```text
Task contract 摘录:
  Focus: 先把 limiter 放进现有运行控制，再考虑 contract sync。
  Evidence: handler；service config；feature flags；recent settings commits.
  Tasks:
    1. route-selection: 选择现有 config / rollout flag / limiter path。
    2. behavior-coverage: 覆盖 allowed、limited、disabled、invalid-config。
    3. response-stability: 保持 public response shape 稳定。
  Boundary: 优先复用已有运行控制，不先引入新的共享基础设施。
  Validate: service behavior coverage；handler response coverage；config/schema check.
  Stop if: 需要新增共享基础设施；
           本地测试无法覆盖 rollout path；
           response shape 必须变化。
```

同一个目标在两个 backend 准则下，task contract 的入口不同：前者先锁 API 事实、兼容性和 generated proof，后者先锁运行控制、行为覆盖和 response 稳定性。计划没有回答对应入口，就还不能进入实现。

### Design system 约束更重的 frontend

项目最关切的是：用户看到的状态必须来自已有设计系统语义，copy、状态覆盖、响应式和可访问性都要能被验证。

```text
Task contract 摘录:
  Focus: 把 rate-limit response 映射到已有 design-system state。
  Evidence: source design context；API error metadata；design-system docs.
  Tasks:
    1. state-mapping: 选定已有 component state、copy source 和 retry affordance。
    2. ui-change: 不新增 token、primitive 或全新视觉模式。
    3. proof: 记录 mobile、desktop、accessibility proof。
  Boundary: 不新增 token、primitive 或全新视觉模式，除非先 review。
  Validate: component state coverage；browser flow coverage；accessibility check.
  Stop if: 设计系统没有对应状态；
           API 没有稳定错误或 retry metadata；
           需要新增 design-system variant。
```

### Ops console 约束更重的 frontend

项目最关切的是：操作员看到信号后能采取行动，表格效率不能退化，telemetry、audit 和 runbook 必须对得上。

```text
Task contract 摘录:
  Focus: 把 rate-limit signal 放到操作员能行动的位置。
  Evidence: support runbook；admin route；telemetry registry；table/filter behavior.
  Tasks:
    1. placement: 选择 row status / banner / audit log，并绑定 runbook action。
    2. admin-ui: 保持 dense table layout、filters 和既有 operator flow。
    3. telemetry-proof: 使用已注册 event，记录 audit trace 和状态来源。
  Boundary: 保持 dense table layout、filters 和既有 operator flow。
  Validate: admin flow coverage；event registry check；table/filter regression coverage.
  Stop if: runbook 没有定义操作员动作；
           telemetry event 未注册；
           后端不能区分 rate limit 和 generic error。
```

同一个目标在两个 frontend 准则下，task contract 的入口也不同：设计系统先锁状态语义、copy 来源和体验 proof；运营控制台先锁操作员动作、表格效率、telemetry 和 runbook。

这些准则会直接改变 agent 动手前必须写清楚的事实、边界、验证和停手条件。

---

## 产物和运行方式

Forma 把团队准则放进三层载体：

- `profile`：团队认可的实践准则，进入版本控制，后续可以 review 和维护。
- `workflow 产物`：安装到 agent 的工作流，可以是 Codex / Claude Code skill bundle，也可以是 Codex plugin。
- `task contract`：agent 面对具体任务时生成的计划契约，记录到 `plans/issue-<id>/`。

默认 workflow 用四个核心 skills 管住 task contract 的生命周期：

| Skill | 作用 |
|---|---|
| `forma-plan` | 把目标和项目准则对齐，形成可 review 的 proposal；不写文件，不执行任务。 |
| `forma-ground` | 按准则需要的事实取证，只读代码、文档、issue、测试等资料。 |
| `forma-lock` | 把已接受的方案写成 `plan.md` 和 `tasks.md`，锁定 task contract。 |
| `forma-execute` | 执行一个已接受 task，跑验证，记录 proof，需要 review 时停。 |

`forma-showhand` 是 `forma-execute` 的自动驾驶入口：计划已经锁定后，它连续推进剩余 tasks，直到遇到阻塞、验证没通过或需要人介入。

团队后续调整 profile，就等于调整 workflow 守护哪些准则；重新生成 bundle 或 plugin 后，agent 会按新的约束规划和执行。

---

## 开始使用

最快的方式，是先把 `forma-creator` 装给 agent。装好以后，你只需要这样说：

```text
用 forma-creator 给这个项目定制一套 workflow。
从文档和代码里挖掘工程准则，先整理给我看；我确认后再生成 workflow，并按提示安装。
```

这条路径适合临场定制。creator 会从项目事实里提炼准则，等你确认后生成并验证可试用 workflow。后续确实有用、团队认可的规则，再提升成 tracked profile。

如果一开始就想形成长期 profile，也可以直接说：

```text
用 Forma 从这个项目的文档和代码里提炼工程准则，给我一版 profile 草案。
profile 确认后，基于它创建并安装 Codex workflow。
```

这条路径里，agent 会用 `forma explain profile --target codex` 读取编写标准。它会先给 profile 草案；你确认后，再生成、验证并按提示安装 workflow。

```text
Use forma-plan to plan this issue first.

Issue:
<你的任务或 issue>
```

第一次有效回应应该是 proposal，不是 patch。如果 agent 直接改文件，说明 workflow 没有加载成功，或者没有被触发。

Codex skill bundle、Claude Code 和安装位置细节见 [Quick Start](./docs/quick-start.zh-CN.md) 和 [Usage](./docs/usage.zh-CN.md)。

---

## 谁适合

Forma 先从 coding agent 开始，因为软件工作有明确的 source 文件、生成物、测试、diff 和 review proof。

但这套方法不只适用于 coding。只要一类 agent 工作有稳定来源、清楚边界、验证方式和 proof，也可以用 Forma：研究、分析、运营、发布、治理、客户交接或内部流程执行。

如果团队在意这些问题，Forma 会更有价值：

- 哪些资料才是当前任务的权威事实；
- 哪些 artifact、系统、contract、数据路径或决策不能随便碰；
- 什么验证才算证明结果；
- proof 应该记录在哪里；
- 什么情况 agent 必须停下来 review。

如果只是几条本地偏好，或者只需要一个单点能力，一个普通 custom skill 可能就够了。

---

## 真实样例和运行记录

仓库里不只有概念文档。

`examples/profiles/` 里有来自真实 workflow 家族、脱敏后的 profile，展示团队如何表达工程准则、source adapter、验证深度、proof 和停手条件。

`examples/generated/` 里保留了这些 profile 编译后的 Codex / Claude Code baselines，用来检查生成产物和 drift。

`plans/issue-*/` 是 Forma 自己开发过程留下的 workflow track。每个 issue 都有 `plan.md`、`tasks.md` 和 `runs/task-*.md`，记录真实 task contract、验证结果和 proof。

---

## 现状

Forma 还处在早期阶段。

Forma 把团队准则写进 workflow 和 task contract，但不保证模型永远听话。具体任务仍然要看 agent 实际留下的 contract 和 proof。

当前重点是：

- 降低团队梳理项目准则和生成 profile 的成本；
- 让 workflow bundle 和 Codex plugin 更容易安装；
- 改进生成 bundle 的验证；
- 补充展示真实 task contract、execution、validation 和 proof 的例子。

仓库中提交的 generated examples 主要用于检测生成结果 drift；runtime 行为要看具体 agent 执行时留下的 contract 和 proof。

Forma 也使用自己的先计划、再执行 workflow 管理开发；这个仓库的 source profile 位于 [`profiles/forma-self/`](./profiles/forma-self/)。

---

## 文档

| | |
|---|---|
| [Quick Start](./docs/quick-start.zh-CN.md) | 首次运行，从 creator 到 tracked profile 的路径。 |
| [Concepts](./docs/concepts.zh-CN.md) | 项目准则、workflow 产物、task contract 和阶段边界。 |
| [Workflow Contract](./docs/workflow-contract.zh-CN.md) | task contract 如何组织证据、边界、验证和 proof。 |
| [Profile Schema](./docs/profile-schema.zh-CN.md) | 如何把长期工程准则维护成 YAML profile。 |
| [Forma Creator](./docs/forma-creator.zh-CN.md) | 让 agent 辅助梳理准则并生成 workflow。 |
| [Skill Bundle](./docs/skill-bundle.zh-CN.md) | 生成产物结构。 |
| [Verifier](./docs/verifier.zh-CN.md) | 验证检查什么，以及不能证明什么。 |
| [Targets](./docs/targets.zh-CN.md) | Codex 和 Claude Code target 行为。 |
| [Examples](./docs/examples.zh-CN.md) | 脱敏 sample profile、生成基线和真实 tracked runs。 |
| [使用说明](./docs/usage.zh-CN.md) | 命令参考。 |

Apache-2.0 - see [LICENSE](./LICENSE)
