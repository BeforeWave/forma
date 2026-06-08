# Verifier

英文版：[verifier.md](./verifier.md)

`forma verify` 用来检查生成的工作流 bundle、`forma-creator` bundle 和 Codex plugin 产物。

它是让 Forma 不只是文案生成器的工程边界：生成产物必须结构有效、符合 target 契约，并保留预期的 Plan-First workflow 形状。

## 什么时候运行

这些时候运行验证：

- 安装生成 bundle 或 Codex plugin 前；
- 提交生成基线前；
- 修改 profile 后；
- 使用 temporary injection 后；
- 重命名生成技能后；
- 修改方法、target adapter 或 verifier 规则后；
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
- scripts/resources 是否没有跨到相邻 skill 目录取资源；
- plan-first stage 是否存在且身份正确；
- target metadata 规则，例如 Codex bundle 是否按需带有 Codex metadata，Claude Code bundle 是否没有 Codex-only metadata；
- `shape`、`gauge`、`seal`、`pour` 等阶段是否保留核心方法要求。

具体规则在随包提供的 `forma_verifier` package 中，后续会随 Forma 演进。

## 不检查什么

验证不是语义评审。

它不证明：

- profile 是正确的项目决策；
- 生成的 workflow 已经覆盖某个项目的 task contract；
- 每条验证命令、gate 或 proof 路径都充分；
- 外部 source adapter 已完成认证或当前可访问；
- Agent 永远会正确执行；
- 生成示例代表一次真实成功的项目运行；
- temporary injection 应该提升成长期 profile。

人工评审仍然必要。

## 常见失败类型

| 失败 | 常见原因 |
|---|---|
| 缺 frontmatter key | 生成或手写的 `SKILL.md` 不是目标 Agent 可读结构。 |
| name/directory 不一致 | 重命名 skill 后，manifest、目录和 frontmatter 没有同步。 |
| reference 路径断裂 | skill 指向了没有被复制进来的 `references/*.md`。 |
| 跨 skill 借资源 | 生成 skill 访问相邻 skill 的 `references/` 或 `scripts/`。 |
| target metadata 不匹配 | Claude Code bundle 里出现 Codex-only metadata，或 Codex 输出缺少必需 metadata。 |
| 方法规则失败 | 某阶段丢失核心 plan-first 行为，例如只读 grounding 或需要评审门禁的执行。 |

## Manifest 和 Drift

Manifest 记录 compiler 的实际输出：target、mode、输出的 skill 名称和目录、profile 顺序、hash、方法来源和 generator metadata。

验证会使用 manifest 理解 bundle。漂移检查会比较已提交生成基线和当前 compiler 应该生成的结果。

Manifest 是溯源。验证是一致性检查。二者都不能替代对 profile 意图和 task 级执行契约的评审。

## CI 用法

CI 可以用 `forma verify` 保持生成 bundle 结构有效，并发现已提交生成基线是否漂移：

```bash
forma verify source/skill-creator/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
python -m pytest -p no:cacheprovider tests/test_docs_links.py
git diff --check
```

这些检查覆盖结构、target metadata、本地 Markdown 链接、空白问题和生成 bundle 的一致性。它们不能替代对 profile 意图、temporary injection 规则或 Agent 真实运行行为的评审。

## Bundled Verifier

Bundled verifier 代码组织在 `source/skill-creator/` 内部，所以构建出来的 `forma-creator` 可以在不安装开发者 CLI 的情况下验证生成产物。

同一个 verifier package 也被开发者 `forma verify` 命令使用。

## 相关文档

- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Forma Creator](./forma-creator.zh-CN.md)：creator 路径和随包验证。
- [使用说明](./usage.zh-CN.md)：命令参考。
