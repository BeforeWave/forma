# Verifier

英文版：[verifier.md](./verifier.md)

`forma verify` 用来检查生成的 workflow bundle 和 `forma-creator` bundle。

它是 Forma 不只是“prompt generator”的关键边界：生成产物必须结构有效、符合 target 契约，并保留预期的方法形状。

## 什么时候运行

这些时候运行验证：

- 安装生成 bundle 前；
- 提交生成基线前；
- 修改 profile 后；
- 使用 temporary injection 后；
- 重命名生成技能后；
- 修改 methodology、target adapter 或 verifier rules 后；
- 分享 `forma-creator` bundle 前。

```bash
forma verify /tmp/backend-plan-first-codex
forma verify source/skill-creator/
```

## 检查什么

验证目前聚焦确定性的结构和方法规则。

它检查的内容包括：

- `SKILL.md` frontmatter 是否有效；
- 是否有必需的 `name` 和 `description`；
- skill name 是否是 kebab-case；
- emitted skill name、目录和 manifest 是否一致；
- body 是否有必需章节；
- 引用的 `references/*.md` 是否存在于同一个 skill 内；
- scripts/resources 是否没有借用 sibling skill 目录；
- plan-first stage 是否存在且身份正确；
- target metadata 规则，例如 Codex bundle 是否有 Codex metadata，Claude Code bundle 是否没有 Codex-only metadata；
- `shape`、`gauge`、`seal`、`pour` 等阶段是否保留核心方法要求。

具体规则在 bundled `forma_verifier` package 中，后续会随 Forma 演进。

## 不检查什么

验证不是语义评审。

它不证明：

- profile 是正确的产品决策；
- 生成 workflow 对某个组织已经完整；
- 每个验证命令都充分；
- 外部 source adapter 已认证或可访问；
- Agent 永远会正确执行；
- 生成 examples 代表一次真实成功项目运行；
- temporary injection 应该提升成长期 profile。

人工评审仍然必要。

## 常见失败类型

| 失败 | 常见原因 |
|---|---|
| 缺 frontmatter key | 生成或手写的 `SKILL.md` 不是 target 可读结构。 |
| name/directory 不一致 | 重命名 skill 后，manifest、目录和 frontmatter 没有同步。 |
| reference 路径断裂 | skill 指向了没有被复制进来的 `references/*.md`。 |
| 跨 skill 借资源 | 生成 skill 访问 sibling skill 的 `references/` 或 `scripts/`。 |
| target metadata 不匹配 | Claude Code bundle 里出现 Codex-only metadata，或 Codex 输出缺少必需 metadata。 |
| 方法规则失败 | 某阶段丢失核心 plan-first 行为，例如只读 grounding 或 review-gated execution。 |

## Manifest 和 Drift

Manifest 记录 compiler 实际生成了什么：target、mode、emitted skill names/directories、profile order、hash、methodology provenance 和 generator metadata。

验证会使用 manifest 理解 bundle。Drift check 则比较已提交生成基线和当前 compiler 应该生成的结果。

Manifest 是溯源。验证是一致性检查。二者都不能替代对 profile 意图的评审。

## Bundled Verifier

Layer 2 verifier 代码组织在 `source/skill-creator/` 内部，所以构建出来的 `forma-creator` 可以在不安装 developer CLI 的情况下验证生成 suites。

同一个 verifier package 也被 developer `forma verify` 命令使用。

## 相关文档

- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Forma Creator](./forma-creator.zh-CN.md)：creator 路径和随包验证。
- [使用说明](./usage.zh-CN.md)：命令参考。
