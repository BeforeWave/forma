# Skill Bundle

英文版：[skill-bundle.md](./skill-bundle.md)

Skill bundle 是 Forma 编译后的产物。

Profile 是源码。Forma compiler 把 profile、标准方法和目标环境适配器解析后，生成可以安装到 Codex 或 Claude Code 的 bundle。

## 从源码到产物

```text
workflow profile
+ methodology
+ target adapter
+ optional temporary injection
        |
        v
Forma compiler
        |
        v
target-specific skill bundle
```

同一个 workflow profile 可以生成到多个目标环境，而不需要为每个工具手写一套规则。

## Bundle 结构

一个生成的 Plan-First bundle 通常包含五个阶段技能目录和一个 manifest：

```text
<bundle>/
  <shape-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml        # 仅 Codex target 需要时出现
  <gauge-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  <seal-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  <pour-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  <flow-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  .forma-manifest.json
```

目录名可以被 profile 或一次性注入重命名。Manifest 会记录每个语义阶段对应哪个目录。

不是每个 skill 都一定有每个子目录。只有当 methodology、profile 或一次性注入为某个阶段选择了 references 或 scripts，它们才会出现。

一个已提交的真实 sample 长这样：

```text
examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
  backend-plan-first-plan-issue/
  backend-plan-first-ground-plan/
  backend-plan-first-finalize-plan/
  backend-plan-first-implement-feature/
  backend-plan-first-showhand/
  .forma-manifest.json
```

这些名字来自 sample profile。它们仍然会在 manifest 中映射回 `shape`、`gauge`、`seal`、`pour`、`flow` 这些语义阶段。

## Skill 目录

每个生成技能目录都是目标环境可读取的单元。

`SKILL.md` 包含：

- skill frontmatter；
- 阶段职责；
- workflow 指令；
- 按需加载的 references；
- 该阶段选中的 profile 约束；
- 适用时的验证或证明要求。

`references/` 存放较长、稳定、无需复制进阶段正文的指导。

`scripts/` 存放由 methodology、profile 或一次性注入明确选择的辅助脚本。来源读取器和辅助脚本不是基础能力，只有被 workflow source 选中时才应该出现。

目标环境元数据只在目标环境需要时输出。Codex bundle 可能包含 `agents/openai.yaml`；Claude Code bundle 不应包含 Codex-only metadata。

## Manifest

`.forma-manifest.json` 是 bundle 的溯源记录。

它记录的信息包括：

- 目标环境；
- suite kind 和 mode；
- 生成技能名和目录；
- 方法版本或 digest；
- 解析后的 profile 顺序；
- profile 和 resource hash；
- generator 版本和溯源。

Manifest 让 reviewer 和工具能回答：这个 bundle 由什么来源生成、面向哪个目标环境、输出了哪些技能。

## 生成技能质量

生成 bundle 应该像工作流，而不是复制出来的一堆政策文本。

好的 bundle 通常具备：

- 每个 skill 一个清晰职责；
- 短而明确的触发说明；
- 按阶段分布的长期指令；
- 稳定细节放在 `references/`；
- scripts 只在阶段明确拥有时出现；
- 轻量默认约束；
- route-specific 行为放进 conditional overlays；
- 可执行阶段有明确验证或证明路径。

如果每个 skill 都重复每条规则，通常说明 profile 太全局。应把规则移到阶段约束、references、resources 或 conditional overlays。

## 安装位置

| 目标 | 个人安装 | 项目/团队安装 |
|---|---|---|
| Codex | `$HOME/.agents/skills` | `.agents/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

信任项目或团队 bundle 前先审查内容。Skills 可以包含脚本和目标环境专用工具行为。

## 验证

运行：

```bash
forma verify <generated-suite-dir>
```

验证检查结构和方法规则。它不证明 profile 是正确的产品决策，也不证明生成策略在语义上完整。人工评审仍然必要。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、门禁、边界和证明。
- [Profile Schema](./profile-schema.zh-CN.md)：生成 bundle 的源码格式。
- [使用说明](./usage.zh-CN.md)：命令参考和安装命令。
