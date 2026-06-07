# Forma

**把项目专属原则编译成 Coding Agent 的运行时 harness。**

Forma 分三层工作：

- **Layer 0：构建 Profile。** 用 profile 定义项目特有的长期工程原则，明确这个项目希望 Agent 长期遵守的边界。
- **Layer 1：生成 Workflow。** Forma 编译 profile，生成融合了这些长期原则的项目专属 Plan-First workflow skill bundle。
- **Layer 2：Runtime harness。** 当具体开发目标出现时，Agent 在这套 workflow 的约束下运行：澄清目标、收集证据、锁定执行契约、有序执行任务、记录证明、等待用户审核，并在边界变化时停下。

Skill bundle 是安装产物；runtime harness 是它在具体开发目标上发挥作用的方式。

英文文档：[README.md](./README.md)

## 安装后得到什么

Forma 安装的是一套项目专属 workflow harness，由这些协同 skills 组成：

| Skill | Harness 职责 |
|---|---|
| `forma-plan` | 按项目原则澄清开发目标：范围、风险、验收标准、推进策略和未决判断。 |
| `forma-ground` | 为这个目标收集真正需要的证据：仓库、文档、Spec、issue 和其他项目来源。 |
| `forma-lock` | 锁定当前执行契约：已接受边界、有序任务、验证方式和 review 预期。 |
| `forma-execute` | 一次执行一个已接受任务，记录证明，并暴露偏差或阻塞。 |

`forma-showhand` 是 `forma-execute` 连续执行的 candy skill，不是独立环节：对自己的 harness 约束有信心？review 完毕、方案固定，然后 show hand，让 Agent 自动驾驶，它会带你到达目的地。

不喜欢这些名字？别担心，可以改。它们只是默认名。真正重要的是生成出来的 workflow：项目原则进入 Agent 实际调用的 skills，并在开发目标出现时约束它怎么工作。

在 Codex 里，同一套 workflow 也可以打成 plugin，一次安装。

## 快速试一下

先安装 Forma CLI：

```bash
pipx install git+https://github.com/BeforeWave/forma.git
```

以 Codex 为例，生成并安装默认 Plan-First plugin：

```bash
forma create-plugin --target codex --output /tmp/forma-codex-plugin
forma install --target codex --scope project /tmp/forma-codex-plugin
```

安装后，先从 planning skill 开始：

> 用 `forma-plan` 先规划这个 issue。

这会给你默认 harness。Codex 不应该从目标直接跳到 patch；它应该先澄清目标、收集证据、锁定执行契约，再带着证明执行任务。

## 可审查产物

每个开发目标推进过程中，runtime harness 应该留下可审查的产物：

- `plans/issue-<id>/plan.md`：澄清后的目标、范围、方案、验证、策略，以及产物和证明边界。
- `plans/issue-<id>/tasks.md`：有顺序的已接受任务，包括交付目标、证明义务、依赖和约束。
- `plans/issue-<id>/runs/`：任务完成时记录下来的执行证据。

这个仓库的实际 plans 可以直接看 [`plans/`](./plans/)。

这就是“Agent 记住了说明”和“workflow 可审查”的区别：你能看到它澄清了什么、锁定了什么、跑过什么、留下了什么证明。

## 塑造 Harness

默认 harness 只是基线。Forma 的重点是把它塑造成这个项目真正需要的样子。

项目原则可以覆盖不同类型的关注点：

- 规划前优先读取哪些来源；
- 生成产物、公共 API、数据路径这类不能随手改的边界；
- 权限、计费、删除、迁移、兼容性这类需要停下来确认的风险点；
- 不同任务类型应该使用什么验证强度；
- 计划偏离、证据不足或需要人判断时如何停下。

想快速做一套项目专属 harness，可以安装 creator skill：

```bash
forma build-creator --target codex --output /tmp/forma-creator
forma install --target codex --scope project /tmp/forma-creator/codex/forma-creator
```

然后像和协作者沟通一样告诉 Codex：

> 针对这个 repo 定制一套 workflow，先看看仓库结构和常见验证方式。我比较在意：生成结果要从源码出，docs-only 改动用轻量检查，改代码前先看附近有没有测试，不确定的判断先列出来让我决定。

长期规则可以写成 profile，再从源码生成 workflow。Claude Code、显式验证、安装位置、profile 编写和完整命令见 [Usage](./docs/usage.zh-CN.md)。

## 什么时候用

当项目的长期原则需要影响 Agent 如何处理开发目标时，用 Forma。尤其是规划、取证、任务边界、验证、评审证明和停止条件不应该只停留在背景说明里的项目。

如果只是改错别字、总结材料，或记住几条简单仓库提醒，Forma 通常太重。直接 prompt、单个自定义 skill 或本地项目说明可能就够了。

## Forma On Forma

Forma 也用自己管理的 Plan-First skills 做自身开发。这个仓库的源码 profile 在 [`profiles/forma-self/`](./profiles/forma-self/)，里面定义了本 repo 的 docs、governance、generated baseline、profile、validation 和证明规则。Forma 自身迭代也走同一套 `plans/issue-<id>/` 里的 plan、task 和证明记录。

## 文档

- [使用说明](./docs/usage.zh-CN.md)：命令、安装位置、验证、target 和自定义生成。
- [快速开始](./docs/quick-start.zh-CN.md)：更完整的首次跑通路径。
- [核心概念](./docs/concepts.zh-CN.md)：心智模型和适用边界。
- [Forma Creator](./docs/forma-creator.zh-CN.md)：临场定制项目专属 skills。
- [Profile Schema](./docs/profile-schema.zh-CN.md)：长期 profile 源码格式。
- [Targets](./docs/targets.zh-CN.md)：Codex 和 Claude Code 行为差异。
- [STRUCTURE.md](./STRUCTURE.md)：源码结构和边界。

## 许可证

Apache-2.0，见 [LICENSE](./LICENSE)。
