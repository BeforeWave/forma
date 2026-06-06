# Forma

为团队和项目构建专属的 Spec Plan-First agent workflow。

Forma 是一个 Python CLI 和 creator skill source，用来把项目的 spec 与可复用工程约束
变成可安装到 Codex 或 Claude Code 的 agent workflow。它不替代 PRD、issue 或
OpenSpec change；这些仍然是需求层。Forma 做的是在需求 spec 之上注入项目自己的通用
约束，并生成一个 plan-first workflow，要求 agent 在实现前证明计划满足这些约束。

英文文档：[README.md](./README.md)

## 项目模型

Forma 只构建一件事：项目专属的 Spec Plan-First agent workflow。

这个 workflow 由四类输入编译出来：

- **Spec source**：PRD、GitHub issue、OpenSpec change、设计文档或 task plan，定义
  要做什么。
- **Plan-first methodology**：`source/methodology/` 下的 canonical workflow。
- **Project profile**：人可维护的 YAML、references 和 scripts，定义这个团队或 repo
  期望 agent 如何规划、读证据、验证和执行。
- **Agent target**：Codex 或 Claude Code。

输出是一个可安装的五段 skill suite，加上 manifest 和 verifier rules。每个 skill 都
对应具体工程动作：

- `shape`：把需求来源变成有边界的 proposal。它澄清 goal、scope、source of truth、
  未决决策，以及本次 work 选择了哪条项目约束路线。
- `gauge`：只读检查 repo 和来源材料，不改代码。它收集证据，确认哪些文件、API、命令、
  docs 或历史计划真正约束这次工作。
- `seal`：写最终 `plan.md` 和 `tasks.md`。它检查需求覆盖、注入的项目约束、acceptance
  criteria、task 边界和 validation path。
- `pour`：只执行 sealed plan 里的一个 accepted task，更新 task evidence，并运行验证。
- `flow`：只有 sealed plan 允许自动执行时，才继续执行剩余 accepted tasks。

## 为什么需要它

Spec 定义的是要改什么。它通常不会完整编码一个项目要求 agent 稳定遵守的工程规则。

这些项目规则经常散落在 README、AGENTS、验证脚本、团队习惯、私有 source reader 和
历史计划决策里。如果它们只是松散 prompt，不同 agent 会对同一个 spec 做出不同规划。

Forma 把这些可复用规则显式化：

- 持久项目规则放进 reviewed profile；
- 一次性规则分类进 temporary injection；
- 重规则通过 conditional overlays 按路线启用；
- 只有 profile 或 injection 拥有的 source reader 才会被注入；
- planning 和 finalization 必须证明选中的约束已经反映到 sealed plan 里。

核心价值不是更好看的 prompt，而是一个稳定的 plan-first workflow：把 spec + 项目约束
变成经过验证的执行路径。

## Profile 是人维护的源

Forma profile 的目标是人可维护。agent 可以帮某个 repo 起草或修改 profile，但最终
结果应该是项目拥有的、可读、可 review 的源文件。

Profile 可以定义：

- 哪些需求来源是 authoritative；
- 必须读取哪些 repository evidence；
- 哪些 validation commands 能证明 work；
- 哪些规则属于 planning、grounding、plan finalization、task execution 或 automatic
  execution；
- docs-only、governance、migration、generated-baseline、backend、frontend、
  cross-layer 等 conditional routes；
- 哪些 references 或 scripts 会复制进生成的 skills。

Forma 通过 CLI 暴露 profile 编写原则，所以 agent 辅助写 profile 时不需要读 Forma
源码：

```bash
uv run --extra dev forma explain profile --target codex
```

## 注入方式

Forma 支持多种注入方式，因为规则的持久性不同。

**Tracked profile**：团队、repo 或 workflow 的持久 workflow source。适合会重复发生、
需要 review 和长期维护的规则。

**Temporary injection**：一次性 JSON。安装后的 `forma-creator` 可以把用户自然语言约束
转成 temporary injection，用于生成一个 suite。agent 在生成前必须输出 injection path
和 classification table。

**Stage constraints**：只作用于某个生命周期阶段的规则，例如 `shape` 的 planning-only
规则、`gauge` 的只读 grounding 规则、`pour` 的执行规则。

**Conditional overlays**：只在 `shape` 把所选场景记录进 `plan.md` 后启用的路线规则。
适合成本高或场景专用的项目行为。

**Source adapters**：用于加载需求或证据的显式 helper scripts / references，例如 issue
tracker、文档导出器、私有知识工具或本地 source reader。它们由 profile 或 temporary
injection 注入，不是 Forma base capability。

Temporary injection 使用同样的分类原则：

```bash
uv run --extra dev forma explain temporary-injection --format json --target codex
```

## 命令流程

从 reviewed profile 生成 Codex workflow：

```bash
uv run --extra dev forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-codex
```

验证生成结果：

```bash
uv run --extra dev forma verify /tmp/backend-plan-first-codex
```

安装到 Codex：

```bash
mkdir -p ~/.codex/skills
cp -R /tmp/backend-plan-first-codex/* ~/.codex/skills/
```

同一个 profile 也可以生成 Claude Code workflow：

```bash
uv run --extra dev forma create \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/backend-plan-first-claude-code

uv run --extra dev forma verify /tmp/backend-plan-first-claude-code
```

## Creator Skill

Forma 也能生成目标固定的 `forma-creator` skill。安装后的 creator 可以让 agent 把
review 过的自然语言约束转换成 temporary injection，生成项目专属 workflow，并在汇报
成功前验证 suite。

```bash
uv run --extra dev forma build-creator \
  --output /tmp/forma-creator-dist \
  --target codex

uv run --extra dev forma verify /tmp/forma-creator-dist/codex/forma-creator
```

Creator bundle 自带 methodology resources 和 verifier。下游项目不需要安装 developer
`forma` package，就能走 agent-side verification。

## 仓库事实

- `source/methodology/`：用于生成 `shape`、`gauge`、`seal`、`pour`、`flow` 的
  canonical plan-first methodology。
- `source/skill-creator/`：Layer 1 `forma-creator` source、随包 references、standalone
  creator script 和 verifier。
- `src/forma/`：developer CLI、profile compiler、runtime asset resolver 和目标专用
  emitters。
- `profiles/forma-self/`：Forma 管理本仓库迭代用的人可维护 profile。
- `examples/profiles/`：sanitized profile examples。
- `examples/generated/`：已提交的 generated baselines，用于 drift checks。
- `tests/`：verifier、profile、creator、runtime asset 和 generated-baseline tests。

详细 source tree 见 [STRUCTURE.md](./STRUCTURE.md)。

## 和 Spec 工具的关系

Spec 工具保存需求变化。Forma 保存 agent 如何把这个 spec 变成受项目约束、证据支撑的
plan 和 execution。

- OpenSpec、PRDs、issues 管 demand。
- Forma profiles 管项目 workflow constraints。
- 生成出来的 Forma skills 管连接二者的 agent behavior。

## 仓库验证

```bash
uv run --extra dev forma verify source/skill-creator/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
uv run --extra dev pytest -p no:cacheprovider tests/
```

## License

MIT - see [LICENSE](./LICENSE).
