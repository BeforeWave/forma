# Forma Creator

英文版：[forma-creator.md](./forma-creator.md)

`forma-creator` 是 Forma 的 Agent 侧 harness 生成入口。

当一个项目需要先做出一套 workflow harness，但还不想写长期 profile YAML 时，用它。它会帮助 Agent 把已经评审过的项目关注点整理成 temporary injection JSON，生成 target 专用 workflow bundle 或 Codex plugin，并在交付前验证。

## 和 `forma create-bundle` 的区别

| 路径 | 适合 | 输入 | 输出 |
|---|---|---|---|
| `forma create-bundle` | 长期项目工作流规则。 | 已评审的 tracked profile YAML。 | 从已提交源码可重复生成的 bundle。 |
| `forma-creator` | 临场塑造项目专属 harness。 | 已评审自然语言关注点，先分类成 temporary injection JSON。 | 面向固定 target 的 verified workflow 产物。 |

`forma create-bundle` 是确定性的 profile 路径。

`forma-creator` 是快速试手感的路径。它适合在项目还不知道哪些规则值得沉淀成长期 profile 前使用。

## 固定目标契约

每个生成出来的 creator 都固定一个 target：

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target claude-code --output /tmp/forma-creator-dist
```

Codex creator 生成 Codex 形态的 skill bundle，也可以在用户要求 plugin 输出时生成 Codex plugin 产物。Claude Code creator 只生成 Claude Code 形态的 skill bundle。不要用一个 target 的 creator 去生成另一个 target 的 bundle。

Creator 只报告输出路径和安装提示，不会把生成产物安装到用户或项目的 skill roots。

## Temporary Injection 生命周期

Temporary injection 只属于一次生成出来的产物。

正常生命周期是：

1. 用户描述项目专属 workflow 关注点。
2. Agent 先分类每条约束，再写 JSON。
3. Creator 写 temporary injection JSON 文件。
4. Creator 生成固定 target contract 允许的 skill bundle 或 Codex plugin 产物。
5. Creator 运行随 bundle 携带的 verifier。
6. 用户或接收方 Agent 安装 verified 产物并试用这些 skills。
7. 只有反复有用的规则才提升到 tracked profile。

Temporary injection 不是 profile。除非用户明确把它提升到 profile，否则不要把它当成已评审的项目规则。

## 约束分类

Creator 应该把约束放到最窄的正确位置：

Temporary injection 的 map 始终使用内部阶段键 `shape`、`gauge`、`seal`、`pour`、`flow`，不要用 `forma-plan` 这类生成后的对外 skill id 当键。

| 目标 | 适合放什么 |
|---|---|
| `constraints.default` | 最轻量、永远成立的底线规则。 |
| `constraints.shape` | 需求澄清、路线选择、范围和未决问题。 |
| `constraints.gauge` | 只读证据收集。 |
| `constraints.seal` | 计划和任务定稿。 |
| `constraints.pour` | 当前任务执行和证明。 |
| `constraints.flow` | 安全继续和停止条件。 |
| `conditional_overlays` | docs-only、migration、generated-baseline、governance、backend、cross-layer 等重场景规则。 |
| `resources` | 工作流明确选中的 references、scripts 或支持文件。 |

不要把 README、AGENTS、issue 原文或治理文档整段复制进 temporary injection。应该提取项目专属约束，并放到对应位置。

## 来源适配器

如果生成的 bundle 需要从 issue tracker、文档导出器、私有来源工具或本地脚本读取规划上下文，把它分类成 source adapter。

Source adapter 不是 Forma 基础能力。只有 profile 或 temporary injection 明确选中它时，才加入生成 bundle。

## 何时提升到 Profile

当一条 temporary injection 规则满足下面条件时，才提升到 tracked profile：

- 多次运行都会用到；
- 已由该项目负责人评审；
- 可以作为长期源码分享；
- 能明确放进阶段约束、resource、validation command 或 conditional overlay。

不要提升私有、试验性、一次性或依赖临时本地路径的规则。

## 验证

`forma-creator` 应该在报告成功前运行验证。验证会检查生成产物的结构和方法规则，但不证明注入规则本身是正确的项目决策。

边界见 [Verifier](./verifier.zh-CN.md)。

## 相关文档

- [快速开始](./quick-start.zh-CN.md)：tracked profile 和 `forma-creator` 的首次跑通路径。
- [Profile Schema](./profile-schema.zh-CN.md)：长期 profile 格式。
- [Targets](./targets.zh-CN.md)：Codex 和 Claude Code 安装行为。
- [Verifier](./verifier.zh-CN.md)：验证会检查什么。
