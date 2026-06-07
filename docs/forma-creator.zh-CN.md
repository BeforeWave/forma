# Forma Creator

英文版：[forma-creator.md](./forma-creator.md)

`forma-creator` 是 Forma 的 Agent 侧生成入口。

当你想先试一个 workflow 想法，但还不想写长期 profile YAML 时，用它。它会帮助 Agent 把已经评审过的自然语言工作流约束整理成 temporary injection JSON，生成 target 专用的 skill bundle，并在交付前验证。

## 和 `forma create` 的区别

| 路径 | 适合 | 输入 | 输出 |
|---|---|---|---|
| `forma create` | 长期团队或项目工作流规则。 | 已评审的 tracked profile YAML。 | 从已提交源码可重复生成的 bundle。 |
| `forma-creator` | 一次性或试验性 workflow 想法。 | 已评审自然语言约束，先分类成 temporary injection JSON。 | 面向固定 target 的一次性生成 bundle。 |

`forma create` 是确定性的 profile 路径。

`forma-creator` 是快速试手感的路径。它适合在团队还不知道哪些规则值得沉淀成长期 profile 前使用。

## 固定目标契约

每个生成出来的 creator 都固定一个 target：

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target claude-code --output /tmp/forma-creator-dist
```

Codex creator 生成 Codex 形态的 workflow bundle。Claude Code creator 生成 Claude Code 形态的 workflow bundle。不要用一个 target 的 creator 去生成另一个 target 的 bundle。

## Temporary Injection 生命周期

Temporary injection 只属于一次生成出来的 bundle。

正常生命周期是：

1. 用户描述 workflow 约束。
2. Agent 先分类每条约束，再写 JSON。
3. Creator 写 temporary injection JSON 文件。
4. Creator 生成 bundle。
5. Creator 运行随 bundle 携带的 verifier。
6. 用户试用这个 workflow。
7. 只有反复有用的规则才提升到 tracked profile。

Temporary injection 不是 profile。除非用户明确把它提升到 profile，否则不要把它当成已评审的团队政策。

## 约束分类

Creator 应该把约束放到最窄的正确位置：

| 目标 | 适合放什么 |
|---|---|
| `constraints.default` | 最轻量、永远成立的底线规则。 |
| `constraints.shape` | 需求澄清、路线选择、范围和未决问题。 |
| `constraints.gauge` | 只读证据收集。 |
| `constraints.seal` | 计划和任务定稿。 |
| `constraints.pour` | 当前任务执行和证明。 |
| `constraints.flow` | 安全继续和停止条件。 |
| `conditional_overlays` | docs-only、migration、generated-baseline、governance、backend、cross-layer 等重场景规则。 |
| `resources` | workflow 明确选中的 references、scripts 或支持文件。 |

不要把 README、AGENTS、issue 原文或治理文档整段复制进 temporary injection。应该提取工作流规则，并放到对应位置。

## 来源适配器

如果生成的 bundle 需要从 issue tracker、文档导出器、私有来源工具或本地脚本读取规划上下文，把它分类成 source adapter。

Source adapter 不是 Forma 基础能力。只有 profile 或 temporary injection 明确选中它时，才加入生成 bundle。

## 何时提升到 Profile

当一条 temporary injection 规则满足下面条件时，才提升到 tracked profile：

- 多次运行都会用到；
- 已由拥有该项目或团队的人评审；
- 可以作为长期源码分享；
- 能明确放进阶段约束、resource、validation command 或 conditional overlay。

不要提升私有、试验性、一次性或依赖临时本地路径的规则。

## 验证

`forma-creator` 应该在报告成功前运行验证。验证会检查生成 bundle 的结构和方法规则，但不证明注入的政策本身是正确的产品决策。

边界见 [Verifier](./verifier.zh-CN.md)。

## 相关文档

- [快速开始](./quick-start.zh-CN.md)：tracked profile 和 `forma-creator` 的首次跑通路径。
- [Profile Schema](./profile-schema.zh-CN.md)：长期 profile 格式。
- [Targets](./targets.zh-CN.md)：Codex 和 Claude Code 安装行为。
- [Verifier](./verifier.zh-CN.md)：验证会检查什么。
