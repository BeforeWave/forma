# Forma

用可验证的结构生成 plan-first AI skill suite。

英文文档：[README.md](./README.md)

## 这是什么

Forma 是一个 plan-first AI skill 创建工具。它把方法论、验证器和生成器分成三层：

- **Layer 1 — Instruction**：`source/skill-creator/` 是自包含的 `forma-creator` meta skill 源码，包含 `SKILL.md`、引用资料和 agent 侧可直接运行的验证脚本。
- **Layer 2 — Verification**：验证器位于 `source/skill-creator/scripts/forma_verifier/`，使用 Python 标准库实现；开发者 CLI 的 `forma verify` 也复用同一套规则。
- **Layer 3 — Generation**：`src/forma/creator/` 提供 `forma create`，把 `source/methodology/` 和已提交的 profile stack 组合成目标 agent 专用的 Mode-S skill suite。

Forma 的核心方法论是 **plan-first**：实现前先收敛 Goal、Scope、Approach、Validation 和 Plan Strategy；每个 task 都带独立的验收和验证契约；证据放在对应计划旁边。

## 两条作者路径

- **已安装 creator 路径**：安装后的 `forma-creator` 可以在一次 agent 交互中接受用户临时约束，把这些约束注入生成的五段 skill bundle，运行 Layer 2 验证，然后安装或交付生成结果。这类临时约束不会自动成为 Forma 的 tracked source，除非用户明确把它提升为 profile 文件。
- **tracked profile 路径**：`forma create --target ... --profile ...` 读取已提交的 profile 文件和 includes，生成可重复、可 review 的目标 bundle。profile 可以使用 `conditional_overlays` 表达可追踪的路线决策。

Forma 仓库内的示例必须保持 sanitized。真实下游 profile 中的组织 workflow 命令、私有路径、凭证或业务规则应放在拥有这些约束的下游仓库里，不放进 Forma 示例树。

## 安装

推荐开发路径：

```bash
uv run --extra dev forma --help
```

等价 editable install：

```bash
pip install -e ".[dev]"
forma --help
```

`forma` 提供三个命令：

- `forma verify <path>`：对 skill bundle 或生成 suite 运行 Layer 2 验证。
- `forma create --target <agent> --profile <file> --output <dir>`：从 canonical methodology 和 profile stack 生成目标 agent 专用 Mode-S plan-first suite。
- `forma build-creator --source <dir> --output <dir> --target <agent>`：从 meta source 生成 Codex 或 Claude Code 专用的 `forma-creator` 安装包。

## 验证

验证 Layer 1 meta skill source：

```bash
uv run --extra dev forma verify source/skill-creator/
```

验证已提交的 backend 示例输出：

```bash
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-plan-first-claude-code/
```

运行测试：

```bash
uv run --extra dev pytest -p no:cacheprovider tests/
```

## 生成示例

生成 sanitized Go backend suite：

```bash
uv run --extra dev forma create \
  --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go.yaml \
  --output /tmp/sample-backend-go-plan-first-codex
uv run --extra dev forma create \
  --target claude-code \
  --profile examples/profiles/sample-backend/sample-backend-go.yaml \
  --output /tmp/sample-backend-go-plan-first-claude-code
uv run --extra dev forma verify /tmp/sample-backend-go-plan-first-codex
uv run --extra dev forma verify /tmp/sample-backend-go-plan-first-claude-code
```

这组命令对应的 committed drift baseline 位于：

- `examples/generated/sample-backend-go-plan-first-codex/`
- `examples/generated/sample-backend-go-plan-first-claude-code/`

生成 sanitized generic software suite：

```bash
uv run --extra dev forma create \
  --target codex \
  --profile examples/profiles/sample-software/sample-software-plan-first.yaml \
  --output /tmp/sample-software-plan-first-codex
uv run --extra dev forma create \
  --target claude-code \
  --profile examples/profiles/sample-software/sample-software-plan-first.yaml \
  --output /tmp/sample-software-plan-first-claude-code
uv run --extra dev forma verify /tmp/sample-software-plan-first-codex
uv run --extra dev forma verify /tmp/sample-software-plan-first-claude-code
```

`examples/profiles/sample-software/` 当前是 profile-only 示例，用来展示中文协作语气、Impact Profile / Impact Boundary、只读 grounding、sealed plan、review-gated implementation 和 safe showhand gate。本 issue 没有为它提交 generated drift baseline。

## 管理 Forma 自身迭代

Forma 也维护项目自用的 profile，用于管理这个仓库自己的开发迭代：

```bash
uv run --extra dev forma create \
  --target codex \
  --profile profiles/forma-self/forma-self-iteration.yaml \
  --output /tmp/forma-iteration-codex
uv run --extra dev forma create \
  --target claude-code \
  --profile profiles/forma-self/forma-self-iteration.yaml \
  --output /tmp/forma-iteration-claude-code
uv run --extra dev forma verify /tmp/forma-iteration-codex
uv run --extra dev forma verify /tmp/forma-iteration-claude-code
```

`profiles/forma-self/` 不是 public sample，而是 Forma 自己的 tracked self-iteration profile stack。它通过 `Iteration Area` 条件路由区分 docs-only、methodology/verifier、creator/profile、generated-baseline 和 cross-layer 工作，适合生成用于管理 Forma 仓库迭代的 skills。
生成出来的 skill 仍然使用原始 `forma-shape`、`forma-gauge`、`forma-seal`、`forma-pour`、`forma-flow` 名称；self-iteration 是 profile 行为，不是生成 skill 名称前缀。

## 安装 Layer 1 到 Agent

从 meta source 生成目标专用 `forma-creator` 安装包：

```bash
uv run --extra dev forma build-creator \
  --source source/skill-creator \
  --output /tmp/forma-creator-dist \
  --target codex
uv run --extra dev forma build-creator \
  --source source/skill-creator \
  --output /tmp/forma-creator-dist \
  --target claude-code
```

安装到目标 agent skill root：

```bash
mkdir -p ~/.codex/skills ~/.claude/skills
cp -R /tmp/forma-creator-dist/codex/forma-creator ~/.codex/skills/
cp -R /tmp/forma-creator-dist/claude-code/forma-creator ~/.claude/skills/
```

安装后的 creator 使用 `references/agent-target.md` 作为硬输出契约，使用 `resources/plan-first/methodology/` 作为固定 plan-first 来源。它应在汇报成功前运行：

```bash
forma-creator/scripts/verify.py <generated-suite>
```

agent 侧验证路径不需要额外 `pip install`。

## License

MIT — see [LICENSE](./LICENSE).
