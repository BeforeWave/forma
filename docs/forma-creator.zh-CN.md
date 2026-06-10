# Forma Creator

英文版：[forma-creator.md](./forma-creator.md)

`forma-creator` 是装给 agent 的生成入口。它让 agent 不必先等团队写好 profile，就能从项目文档、代码、测试和现有约定里挖掘工程准则，临场生成一套可试用的 Forma workflow。

最短用法是直接对 agent 说：

```text
用 forma-creator 给这个项目定制一套 workflow。
从文档和代码里挖掘工程准则，先整理给我看；我确认后再生成 workflow，并按提示安装。
```

用户不需要手写 JSON。Creator 会让 agent 先把项目最关切的准则讲清楚：权威资料、修改边界、工具要求、验证深度、proof 位置和停手条件。用户确认后，这些准则进入本次生成的 workflow 产物。

## 和其他路径的区别

| 路径 | 适合 | 输入 | 输出 |
|---|---|---|---|
| `forma-creator` | 临场定制，先试一套项目 workflow。 | 项目事实、用户补充、确认后的准则。 | 已验证的一次性 skill bundle 或 plugin。 |
| `forma explain profile` + agent | 一开始就要长期维护源码。 | profile 编写标准、项目事实、团队 review。 | tracked profile YAML，再编译成 workflow。 |
| `forma create-bundle` / `forma create-plugin` | 已经有 review 过的 profile。 | tracked profile YAML。 | 可重复生成的 workflow bundle 或 plugin。 |

`forma-creator` 走的是“先试用”的路径。反复有用、团队认可的规则，再提升成 profile。`forma explain profile` 走的是“先长期化”的路径，产物是可 review、可维护的 YAML 源码。`forma create-bundle` 和 `forma create-plugin` 是 profile 已经存在后的确定性生成命令。

## 固定目标契约

每个 creator 都固定一个 target：

```bash
forma build-creator --target codex --output /tmp/forma-creator-dist
forma build-creator --target claude-code --output /tmp/forma-creator-dist
forma build-creator --target opencode --output /tmp/forma-creator-dist
```

Codex creator 生成 Codex 形态的 skill bundle；用户要求 plugin 输出时，也可以生成 Codex plugin。Claude Code creator 生成 Claude Code 形态的 skill bundle 和 Claude Code plugin。OpenCode creator 生成 OpenCode 原生 skill bundle，不生成 OpenCode JS/TS runtime plugin。不要用一个 target 的 creator 去生成另一个 target 的产物。

Creator 会报告生成产物的路径、验证结果和安装提示。它不会替用户直接把产物写进 Codex、Claude Code 或 OpenCode 的 skill roots。

## Temporary Injection 是什么

在 creator 路径里，temporary injection 是临场准则进入生成器的内部载体。用户通常不需要写它，也不需要先懂它。

正常生命周期是：

1. 用户让 agent 用 `forma-creator` 定制 workflow。
2. agent 读取项目文档、代码、测试和现有约定。
3. agent 提炼工程准则，拿给用户确认或补充。
4. Creator 把确认后的准则分类，写成 temporary injection。
5. Creator 生成固定 target 允许的 skill bundle 或 plugin。
6. Creator 运行随包 verifier。
7. 用户或 agent 按提示安装 verified 产物并试用。
8. 反复有用、团队认可的规则，再提升成 tracked profile。

Temporary injection 只属于本次生成出来的 workflow 产物。只有用户明确提升后，它才会变成 tracked profile 的来源。

## 约束分类

Creator 会把确认后的准则放到最窄的正确位置：

Temporary injection 的 map 始终使用内部阶段键 `shape`、`gauge`、`seal`、`pour`、`flow`，不要用 `forma-plan` 这类生成后的对外 skill id 当键。

| 目标 | 适合放什么 |
|---|---|
| `constraints.default` | 最轻量、永远成立的底线规则。 |
| `constraints.shape` | 需求澄清、路线选择、范围和未决问题。 |
| `constraints.gauge` | 只读证据收集。 |
| `constraints.seal` | 计划和任务定稿，包括 task 边界、验证 gate 和 proof 要求。 |
| `constraints.pour` | 当前 task 执行、验证 gate 和 proof。 |
| `constraints.flow` | 连续执行时的继续条件和停止条件。 |
| `conditional_overlays` | docs-only、migration、generated-baseline、governance、backend、cross-layer 等场景规则。 |
| `resources` | workflow 明确选中的 references、scripts 或支持文件。 |

不要把 README、AGENTS、issue 原文或治理文档整段复制进 temporary injection。应该提取准则，再放到对应位置。

## 来源适配器

如果生成的 workflow 需要从 issue tracker、文档导出器、私有来源工具或本地脚本读取规划上下文，把它分类成 source adapter。

Source adapter 不是 Forma 基础能力。只有 profile 或 temporary injection 明确选中它时，才加入生成产物。

## 何时提升到 Profile

一条 creator 规则满足下面条件时，才适合提升到 tracked profile：

- 多次运行都会用到；
- 已由项目负责人或团队 review；
- 可以作为长期源码分享；
- 能明确放进阶段约束、resource、validation command 或 conditional overlay。

不要提升私有、试验性、一次性或依赖临时本地路径的规则。

## 验证

`forma-creator` 应该在报告成功前运行验证。验证会检查生成产物的结构和方法规则，但不证明临场准则本身是正确的项目决策。

边界见 [Verifier](./verifier.zh-CN.md)。

## 相关文档

- [快速开始](./quick-start.zh-CN.md)：从 creator 跑通临场定制，再长期化成 profile。
- [Profile Schema](./profile-schema.zh-CN.md)：长期 profile 格式。
- [Targets](./targets.zh-CN.md)：Codex、Claude Code 和 OpenCode 安装行为。
- [Verifier](./verifier.zh-CN.md)：验证会检查什么。
