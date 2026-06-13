# Skill Bundle

英文版：[skill-bundle.md](./skill-bundle.md)

Skill bundle 是 Forma 编译出来、安装给 agent 的 workflow 产物。

Profile 或 temporary injection 提供项目准则；Forma compiler 再结合标准方法和
target adapter，生成可以安装到 Codex、Claude Code 或 OpenCode 的 skills。
安装后，这些 skills 会推动 agent 把具体目标落成 task contract：事实、边界、
任务、验证、proof 和停手条件。

## 从 Profile 到 Workflow 产物

```text
profile / temporary injection
+ methodology
+ target adapter
        |
        v
Forma compiler
        |
        v
target-specific workflow skill bundle
```

同一个 workflow profile 可以生成到多个 target，而不需要为每个工具手写一套准则。Creator 路径生成的一次性产物也会落到同样的 bundle 结构。

## Bundle 结构

一个生成的 direct skill bundle 通常包含四个核心 workflow skill、`showhand` 自动驾驶入口，以及一个 manifest。默认 direct skill 目录使用 `forma-*` 命名模式：

```text
<bundle>/
  forma-<plan-stage>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml        # 仅 Codex target 需要时出现
  forma-<ground-stage>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  forma-<lock-stage>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  forma-<execute-stage>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  forma-<showhand-stage>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  .forma-manifest.json
```

目录名可以被 profile 或 temporary injection 重命名。Manifest 会记录每个生成技能对应哪个目录。

Plugin 和 direct skill bundle 的触发名不同：plugin 用 `forma:*`，direct skill bundle 用 `forma-*`。

不是每个 skill 都一定有每个子目录。只有当 methodology、profile 或 temporary injection 为某个阶段选择了 references 或 scripts，它们才会出现。

本地生成的 sample 可以长这样：

```text
/tmp/forma-sample-backend-codex/
  backend-plan-first-plan/
  backend-plan-first-ground/
  backend-plan-first-lock/
  backend-plan-first-execute/
  backend-plan-first-showhand/
  .forma-manifest.json
```

这些名字来自 sample profile。Manifest 会记录最终输出的技能名和目录。

## Skill 目录

每个生成技能目录都是目标 agent 可以读取的单元。

`SKILL.md` 包含：

- skill frontmatter；
- 阶段职责；
- workflow 指令；
- 按需加载的 references；
- 该阶段选中的项目准则；
- 适用时的验证 gate 或 proof 要求。

`references/` 存放较长、稳定、无需复制进阶段正文的指导。

`scripts/` 存放由 methodology、profile 或 temporary injection 明确选择的辅助脚本。来源读取器和辅助脚本不是基础能力，只有被 workflow source 选中时才应该出现。

Target metadata 只在对应 target 需要时输出。Codex bundle 可能包含 `agents/openai.yaml`；Claude Code bundle 不应包含 Codex-only metadata。

## Manifest

`.forma-manifest.json` 是 bundle 的溯源记录。

它记录的信息包括：

- target；
- bundle kind（`bundle_kind`）和 mode；
- 生成技能名和目录；
- 方法版本或 digest；
- 解析后的 profile 顺序；
- profile 和 resource hash；
- generator 版本和溯源。

Manifest 让评审者和工具能回答：这个 bundle 由什么来源生成、面向哪个 target、输出了哪些技能。

## 生成技能质量

生成 bundle 应该把项目准则分布到正确阶段，而不是复制出一堆规则文本。

好的 bundle 通常具备：

- 每个 skill 一个清晰职责；
- 短而明确的触发说明；
- 按阶段分布的准则；
- 稳定细节放在 `references/`；
- scripts 只在阶段明确拥有时出现；
- 轻量默认约束；
- 路线专用行为放进 conditional overlays；
- 可执行阶段有明确验证 gate、proof 路径和停手条件。

如果每个 skill 都重复每条准则，通常说明 profile 或 temporary injection 太全局。应把准则移到阶段约束、references、resources 或 conditional overlays。

## Target Metadata

生成 bundle 保留同一套 workflow 阶段，但 target metadata 不同：

- Codex bundle 可以在每个 skill 里包含 `agents/openai.yaml`。
- Claude Code bundle 使用 direct skill frontmatter，不包含 Codex metadata。
- OpenCode bundle 使用原生 direct skill frontmatter，包含
  `compatibility: opencode` 和 string-to-string `metadata`；不生成 Codex 或
  Claude Code plugin metadata。

## 安装位置

| 目标 | 个人安装 | 项目安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.agents/skills` |
| OpenCode skills | `$HOME/.config/opencode/skills` | `.opencode/skills` |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

发现规则、target metadata 和信任边界见 [Targets](./targets.zh-CN.md)。

## 验证

运行：

```bash
forma verify <generated-bundle-dir>
```

验证检查结构和方法规则。它不证明 profile 或临场准则是正确的项目决策，也不证明真实运行时的 task contract 在语义上完整。见 [Verifier](./verifier.zh-CN.md)。人工评审仍然必要。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、门禁、边界和证明。
- [Profile Schema](./profile-schema.zh-CN.md)：生成 bundle 的源码格式。
- [Targets](./targets.zh-CN.md)：安装位置和 target 行为。
- [Verifier](./verifier.zh-CN.md)：验证检查和限制。
- [使用说明](./usage.zh-CN.md)：命令参考和安装命令。
