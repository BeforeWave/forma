# 使用说明

英文版：[usage.md](./usage.md)

这页是 Forma 的命令参考。第一次跑通不要从命令背起，先看 [快速开始](./quick-start.zh-CN.md)：让 agent 提炼项目规则，确认后生成并安装 workflow。

不带子命令运行 `forma` 是一个成功的 discovery 入口。它会以退出码 `0`
打印和 `forma --help` 相同的 agent 路由指南，所以 coding agent 不确定该走哪条
命令路径时，可以先从这里开始。

## Agent 命令路由

| 目标 | 命令路径 | 下一步 |
|---|---|---|
| 选择 agent-facing Forma CLI 路线 | `forma explain agent --format human|agent|json --target codex` | agent 需要只读命令路由指南，并在 profile authoring、stage guidance、temporary injection、doctor/init、build、verify、drift、install、creator 或 profile adoption 之间选路时，先从这里开始。 |
| 阅读或交接 profile 编写规则 | `forma explain profile --format human|agent|json --target codex` | 只在 `forma explain agent` 把任务路由到 profile authoring 后使用。它不检查 repo，也不会自动生成草稿；agent 仍要把这份规则和项目事实结合起来，再提出 profile rules。 |
| 把 candidate rules 和 stage methodology 对照 | `forma explain stage <stage> --format human|agent|json --target codex` | candidate profile rules 已经识别出 touched stages 后、真正写 profile 前使用。base methodology 已经负责的规则要删掉；如果 base contract 弱，则提 methodology 修改。 |
| 从已经 review 的 tracked profile 生成 skill bundle | `forma build bundle --target <target> --profile <profile.yaml> --output <dir>` | 生成 `target` 填 `codex`、`claude-code` 或 `opencode`；human 输出是简洁产物结果。需要给 agent 或工具链交接下一步时，用 `--format agent` 或 `--format json`。 |
| 生成默认 Plan-First skill bundle | `forma build bundle --target <target> --output <dir>` | 生成 `target` 填 `codex`、`claude-code` 或 `opencode`；运行 `forma verify <dir>`，再用匹配的 target 安装。 |
| 生成 plugin source | `forma build plugin --target codex|claude-code --profile <profile.yaml> --output <dir>` | human 输出是简洁产物结果。安装 handoff 用 `--format agent` 或 `--format json`；Codex plugin 通过 Codex 安装，Claude Code plugin root 用 `forma install --target claude-code` 安装。 |
| 诊断 repo 是否 agent 友好 | `forma doctor [path] --format human|agent|json` | 只读检查 agent 入口、source 边界、验证契约、setup 契约、任务状态、human gates、噪音控制和可选 agent integrations。 |
| 从 repo facts 初始化确定性的 Forma 源文件 | `forma init [path] --from-report <report> --format human|agent|json` | 默认 dry-run；用 `--apply` 创建 `.forma/` workflow source 和 report-derived Agent handoff 文件。 |
| 构建可选 creator 临场路径 | `forma build creator --target <target> --output <dir>` | 只在 creator 路径使用；运行 `forma verify <dir>/<target>/forma-creator`，再用匹配的 target 安装。 |
| 给 agent 提供 temporary-injection 规则 | `forma explain temporary-injection --target codex` | 只用于可选 creator / 临场生成路径。 |

已经 review 的 profile 存放目录就是需要检查的 profile directory。如果该目录包含
`reinstall-workflow.sh`，先运行这个 profile-local 脚本，再考虑手动拼
`forma build`、`forma verify`、`forma drift`、`forma install`、marketplace refresh
或 Codex plugin 命令。带 `--profile` 的 `forma build bundle` 和 `forma build plugin`
会通过 `--format agent` 和 `--format json` 暴露 profile-local reinstall 状态和结构化
next actions。默认 `human` 输出保持简洁，方便放进 profile-local 脚本而不打印
agent handoff 文本。如果脚本缺失或仍是 bootstrap-incomplete，agent 必须先和用户确认
install facts，并把它们写进脚本，才能报告 reusable reinstall flow。fixed-fact
reinstall 脚本应固化 artifact kind、target、相关 plugin id、相关 marketplace source、
install selector 和 visibility check。agent 侧关于可复用安装设置和复用这套流程的规则在
`forma explain agent` 里。

使用 `forma build bundle` 或 `forma build plugin`；旧的 `forma create` 命令不再支持。

## 命令

### `forma` / `forma --help`

打印根命令指南和命令列表。不带子命令时，`forma` 返回退出码 `0`，并显示
和 `forma --help` 相同的路由指南。

当 agent 需要判断是打印 authoring guidance、create skill bundle、create plugin、
install verified 本地产物、verify 产物，还是构建可选 creator 时，先用这个命令做 discovery。

### `forma verify <path>`

验证生成的 skill bundle、`forma-creator` bundle、Codex plugin 或 Claude Code plugin：

```bash
forma verify /tmp/settings-workflow-codex
forma verify --json /tmp/settings-workflow-codex
```

安装、提交或分享生成 workflow 产物前，先运行这个命令。

下一步：

- 如果 skill bundle 或 creator 验证通过，用 `forma install` 安装 verified 本地路径。
- 如果 Codex plugin 验证通过，通过 Codex 安装，不要用 `forma install`。
- 如果 Claude Code plugin 验证通过，用 `forma install --target claude-code` 安装 plugin root。
- 如果产物安装路线不清楚，用 build 命令的 `--format agent|json` handoff 和下面的
  install 边界判断；`doctor` 用于诊断 repo 是否 agent-friendly，不再检查生成产物。

`forma verify` 检查结构和方法规则。它不替代 profile 评审，也不替代产品判断。验证边界见 [Verifier](./verifier.zh-CN.md)。

当其他工具或 agent 需要结构化结果时，使用 `--json`。JSON report 保持同样的退出码契约，并为每条 rule result 提供语义 failure class。

对输出结构化 handoff 的命令，例如 `doctor`、`init`、部分 `build` 命令和
`explain`，使用 `--format human|agent|json`。`human` 简洁给人读，并隐藏
agent-only handoff 细节；`agent` 包含可执行 next actions、stop conditions 和
forbidden actions；`json` 给工具链使用。命令外形可以共用，但内容按命令语义区分：
`doctor` 输出 findings 和 evidence，`explain` 输出编写指南和 handoff 规则。

### `forma doctor [path]`

只读诊断一个 repo 是否适合 agent 操作：

```bash
forma doctor
forma doctor --format json /path/to/repo
forma doctor --format agent /path/to/repo
```

默认输出会把 agent 路由到 `forma explain agent`；如果已知消费端 agent target，则使用
`forma explain agent --target codex|claude-code|opencode`。agent 应先读取该指南，再用
`--format agent` 或 `--format json` 继续处理。`needs-agent` 是调查输入，不是最终诊断：
报告前必须给每个非 `contract` 的核心 finding 明确 disposition；只有需要 owner 决策、
所需证据不可用、存在 unsafe blocker，或所有 finding 都已有明确 disposition 时才能停止。

它会回答一个新 Agent 是否能知道先读什么、哪些能改、哪些不能改、怎么验证、
什么时候问人、任务状态和证据放哪里。核心 readiness 来自 repo 的
agent-operability 契约；Forma profile 只是可选 integration，不是 ready 的前提。

Doctor ready 不等于 profile complete。编写长期 profile 前，agent 仍必须归纳 repo
purpose 和 maintenance model：主要交付物、runtime 或 artifact 模型、validation
模型、source/generated/release 边界、相关 compatibility 或 safety risk，以及
review/handoff 预期。只编码 doctor findings 的 profile 应标记为 operability-only，
不能当作 project-ready。

JSON renderer 会输出 repo-doctor schema，包含 `facts`、`findings`、`evidence`、
`confidence`、`programmatic_actions`、`agent_handoffs`、`human_decisions` 和
`unsafe_blockers`。`facts` 里的 adoption guidance 用 `owner_confirmations`
表达 profile 规整、build/verify、install target/scope 和 commit 等确认点。这个
report 可以作为 `forma init --from-report` 的输入。

### `forma init [path]`

为 repo 规划确定性的 remediation：

```bash
forma init
forma init --format agent
forma doctor --format json . > /tmp/forma-doctor.json
forma init --from-report /tmp/forma-doctor.json
forma init --apply
forma init --from-report /tmp/forma-doctor.json --apply
```

默认是 dry-run。加 `--apply` 后，Forma 会在可被 Git 跟踪的 `.forma/` 目录下创建
确定性的 workflow source 文件：`.forma/profile.yaml`、
`.forma/reinstall-workflow.sh`，以及 `.forma/.gitignore`。`.gitignore` 只 ignore
`/state/`，所以 profile source 和 reinstall workflow 仍可被 Git 跟踪，runtime workflow state
放在 `.forma/state/` 下。传入 `--from-report` 时，init 还会生成
`.forma/agent-operability/doctor-report.json`、
`.forma/agent-operability/agent-handoff.md` 和
`.forma/agent-operability/human-decisions.md`。

这些是 draft project workflow source 和 handoff 文件。`forma init` 不会声称
profile 已经 review，不会批准语义 repo 规则，也不会单靠自己把 repo 变成
agent-friendly。Agent 可以结合 report-derived handoff 和 profile-authoring
principles 生成 remediation proposal，但 profile approval、build/verify、install
target/scope 和是否提交 workflow source 都仍然是独立 owner confirmations。生成的
`reinstall-workflow.sh` 在 install facts 被确认并写入 fixed-fact 脚本之前都是
bootstrap-incomplete。如果 profile authoring 过程中生成了 review packet，应询问用户
是否保留；不要默认留在 repo 里。

### `forma build bundle`

把标准方法和解析后的 tracked profile 组合起来，生成 target 专用 workflow bundle：

```bash
forma build bundle --target codex --output /tmp/forma-codex-bundle
```

必需选项：

- `--target codex|claude-code|opencode`
- `--output <dir>`

可选输入：

- `--profile <file>`：顶层 tracked profile。省略时，Forma 会输出 `plan`、`ground`、`lock`、`execute` 和 `showhand` 这些阶段对应的通用 direct skills，skill 名带 `forma-*` 前缀。

开发时可选覆盖：

- `--methodology <dir>`：使用指定的方法目录，而不是打包内置的运行时资源。

下一步：运行 `forma verify <output-dir>`，再用 `forma install` 安装 verified 本地
bundle。对于 profile-backed 输出，默认 `human` 只输出简洁产物结果；需要 agent
继续处理时，用 `--format agent` 查看结构化 next actions。如果 profile 目录包含
`reinstall-workflow.sh`，先运行这个脚本，不要重新拼 build/install 命令；如果缺失，
说明可复用安装路径尚不完整，不应把临时手拼命令当成可复用安装路径。

Profile 格式见 [Profile Schema](./profile-schema.zh-CN.md)。

### `forma build plugin`

从 profile 生成本地 plugin 产物：

```bash
forma build plugin --target codex --output /tmp/forma-codex-plugin
forma build plugin --target claude-code --output /tmp/forma-claude-code-plugin
```

Codex plugin 输出根目录包含 `.codex-plugin/plugin.json`、根 `.forma-manifest.json` 和 `skills/<skill-id>/` 子目录。Claude Code plugin 使用 `.claude-plugin/plugin.json`，同样带根 manifest 和嵌套 `skills/<skill-id>/`。它不会顺带输出 `dist/skill-bundles` 或 sibling bundle。

对 tracked profile 来说，plugin id 来自 profile 的 `bundle.name`。Codex
plugin 展示名默认从这个值 title-case 派生，也可以用 `plugin.display_name`
显式设置。`plugin.json` 指向嵌套的 `./skills/` 目录。如果 generated skill
名称以精确的 `<plugin-id>-` 开头，Forma 会在 plugin-local skill 名称里去掉这个前缀。比如 plugin `forma` 中，默认 local 阶段是 `plan`、`ground`、`lock`、`execute` 和 `showhand`。

Plugin 输出会在 manifest 和 metadata prompt 里记录 `forma:plan` 这类 qualified name。Plugin 用 `forma:*` 触发；direct skill bundle 用 `forma-*`。

必需选项：

- `--target codex|claude-code`
- `--output <dir>`

可选输入：

- `--profile <file>`：顶层 tracked profile。省略时，plugin 会暴露 plugin-local 的 `plan`、`ground`、`lock`、`execute` 和 `showhand` 阶段。

下一步：运行 `forma verify <output-dir>`。对 profile 生成的输出，在任何
postprocess 之前运行 `forma drift <output-dir> --profile <profile.yaml>`。
如果有意对生成产物做 postprocess，postprocess 必须在 drift 之后执行，最终 gate
用 `forma verify <output-dir>`，不要用 drift。

Codex plugin 通过 Codex marketplace/plugin UI 安装，不用 `forma install`。
在补齐可复用安装路径或诊断安装问题时，可以按需检查当前配置的 marketplaces；随后要和用户确认
plugin id、marketplace name、marketplace source、install selector 和 visibility check，
确认 marketplace catalog 指向生成出的 plugin root 后，再用 confirmed
`<plugin-id>@<marketplace>` selector 安装。稳定的 profile-local reinstall 脚本不应列出
marketplaces，也不应在运行时继续开放 plugin id、marketplace、selector 或 source refresh 决策。

Claude Code plugin root 用
`forma install --target claude-code --scope user|project <output-dir>` 安装。

### `forma build creator`

生成 target 专用的可安装 `forma-creator`。这是可选临场路径：不想先处理 profile 文件时，可以让 agent 临场生成 workflow：

```bash
forma build creator --target codex --output /tmp/forma-creator-dist
forma build creator --target opencode --output /tmp/forma-creator-dist
```

必需选项：

- `--target codex|claude-code|opencode`
- `--output <dir>`

开发时可选覆盖：

- `--source <dir>`：使用指定的 `forma-creator` 源目录，而不是打包内置的运行时资源。

每个生成的 `forma-creator` 都固定一个 target。Codex creator 生成 Codex 形态的 skill bundle 和 Codex plugin。Claude Code creator 生成 Claude Code 形态的 skill bundle 和 Claude Code plugin。OpenCode creator 生成 OpenCode 原生 skill bundle，不生成 OpenCode JS/TS runtime plugin。临场定制路径见 [Forma Creator](./forma-creator.zh-CN.md)。

下一步：运行 `forma verify <output-dir>/<target>/forma-creator`，再用 `forma install`
安装这个 verified creator 路径。

### `forma install`

安装已经验证过的本地单个 skill、skill bundle 或 Claude Code plugin root：

```bash
forma install --target codex --scope project /tmp/forma-codex-bundle
forma install --target opencode --scope project /tmp/forma-opencode-bundle
forma install --target claude-code --scope user /tmp/forma-claude-code-bundle
forma install --target claude-code --scope project /tmp/forma-claude-code-plugin
```

必需参数和选项：

- `PATH`：本地产物路径；这个命令故意不做 URL 下载。
- `--target codex|claude-code|opencode`
- `--scope user|project`

覆盖行为：

- 不加 `--replace` 时，如果目标目录已经存在，会拒绝覆盖。
- 加 `--replace` 时，Forma 只替换 verified source 对应的目标产物。
- Codex plugin 安装会明确报错，并提示 Codex marketplace 设置，包括
  `codex plugin marketplace list`、用户选择 marketplace、显式
  `codex plugin add <plugin-id>@<marketplace-name>`，以及安装后新开 thread。
- Claude Code plugin root 会安装到项目级 `.claude/skills/<plugin-name>` 或用户级 `$HOME/.claude/skills/<plugin-name>`。

下一步：安装 skill、skill bundle 或 Claude Code plugin 后，新开 agent thread，让新安装的 skills 被发现。

### `forma explain`

输出 agent-facing 命令指南和更窄的编写指南，让外部 agent 不需要阅读 Forma 源码：

```bash
forma explain agent --target codex
forma explain profile --target codex
forma explain stage shape --target codex
forma explain profile --format agent --target codex
forma explain temporary-injection --format json --target codex
```

`forma explain agent` 是给 agent 使用 Forma 时的只读命令路由指南。agent 需要在
profile authoring、workflow generation、plugin output、可选 creator output、
profile adoption、drift、doctor、init、verify 或 install 之间选路时，应该先读它。
它不检查仓库、不生成 profile 草稿、不构建产物，也不安装 workflow；它解释下一步该走哪条命令路径、需要从仓库或用户那里带入哪些事实，以及这条路径必须在哪里停止。

`forma explain profile` 既可以给人看，也可以给 agent 用，但 renderer 的交接重点不同：

- `--format human` 给出简洁的读者说明，解释哪些内容属于长期 profile，哪些内容应该留在当前任务。
- `--format agent` 给出可执行编写契约：需要收集哪些项目事实，如何区分长期规则和任务规则，可以提出哪些文件，以及什么时候必须停下来让用户 review。
- `--format json` 把同一类指导转成结构化数据，供工具链消费。

`forma explain profile` 不检查 repo，不创建 profile 文件，也不能声称 profile 已经
review。需要确定性 skeleton 时用 `forma init --apply`；之后再把
`forma explain profile` 的规则和项目事实结合起来，起草给人 review 的 profile。

真正写 profile 文件前，对 candidate rules 涉及的每个 stage 运行
`forma explain stage <stage>`。stage guidance 用来把 candidate profile rules 和
base methodology 对照：base stage contract 已经负责的规则不要放进 profile；profile
里只保留长期的项目适配；如果 base contract 本身弱或缺失，就提出 methodology 修改。

当另一个 agent 需要起草 profile 或 temporary injection 时，用这一组命令给它规则。正常 profile-first 路径可以直接说：

```text
用 Forma 给这个项目生成一套 Codex workflow。
先把你提炼出的项目规则给我看；确认后再生成并安装。
```

agent 先用 `forma explain agent --target codex` 判断路线，再用
`forma explain profile --target codex` 读取 profile 编写标准。它把这些规则和项目事实
结合起来后，还要对每个 touched stage 使用 `forma explain stage <stage>`，然后再提出
profile YAML。只有这些规则需要长期复用时，才把 profile 提交进版本控制。

下一步：profile review 通过后，用 `forma build bundle` 生成 skill bundle，或用
`forma build plugin` 生成 plugin source。

## 安装目标

Forma 生成 target 专用 skill bundle。`forma install` 会把 verified 本地 skill 产物写到对应位置：

| 目标 | 个人安装 | 项目安装 |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.agents/skills` |
| OpenCode skills | `$HOME/.config/opencode/skills` | `.opencode/skills` |
| Claude Code skills | `$HOME/.claude/skills` | `.claude/skills` |
| Claude Code plugins | `$HOME/.claude/skills/<plugin-name>` | `.claude/skills/<plugin-name>` |

OpenCode 使用 direct skill bundle。先用 `forma build bundle --target opencode`
生成 OpenCode bundle，验证后用 `forma install --target opencode` 安装。Forma
不生成 OpenCode JS/TS runtime plugin。

Codex plugin 输出是本地 plugin source。Forma 不安装 Codex plugin。在补齐可复用安装路径或诊断安装问题时，
可以按需检查当前配置的 marketplaces；随后和用户确认 plugin id、marketplace name、
marketplace source、install selector 和 visibility check，再运行
`codex plugin add <confirmed-plugin-id>@<confirmed-marketplace>`，或在 Codex plugin UI
里安装。安装后新开 Codex thread，这样 plugin skills 才会被发现。稳定的
profile-local reinstall 脚本应使用 confirmed facts，而不是每次做 marketplace discovery。

Claude Code plugin 输出可以通过 Forma 安装，因为 Claude Code 会从 `.claude/skills/<plugin-name>` 加载 skills-directory plugin。

- [Install a local plugin manually](https://developers.openai.com/codex/plugins/build#install-a-local-plugin-manually)
- [Add a marketplace from the CLI](https://developers.openai.com/codex/plugins/build#add-a-marketplace-from-the-cli)

target 发现规则、metadata 和信任边界见 [Targets](./targets.zh-CN.md)。

## 重命名生成技能

Forma 保留 `shape`、`gauge`、`seal`、`pour`、`flow` 这些语义阶段，但生成技能名可以使用项目自己的语言。

### 长期 profile 命名

Tracked profile 里，设置 `stages.<stage>`：

```yaml
stages:
  shape:
    name: settings-workflow-plan
    directory: settings-workflow-plan
    display_name: Settings Workflow Plan
  gauge:
    name: settings-workflow-ground
    directory: settings-workflow-ground
    display_name: Settings Workflow Ground
```

规则：

- `name` 是 skill frontmatter 里的名字；
- `directory` 是安装目录名；
- `display_name` 是 target 里的展示名；
- `plugin.display_name` 设置 Codex plugin 安装界面的展示名，不改变 plugin id、skill 名称或触发名；
- `name` 和 `directory` 必须是 lower kebab-case；
- 语义阶段键仍然是 `shape`、`gauge`、`seal`、`pour`、`flow`。
- 同一个 profile 用于 `forma build plugin` 时，plugin id 仍然是 `bundle.name`；如果生成名带有这个精确前缀，plugin-local skills 会去掉前缀。Plugin 使用最终的 `<plugin-id>:<local-skill>` 形式触发，默认 Forma plugin 是 `forma:plan` 这类 `forma:*`。

### 一次性 creator 命名

通过 `forma-creator` 临场生成时，用户不需要给 agent 一个 JSON 文件。用自然语言告诉 agent 命名意图；creator 再分类这条要求，并在内部写 temporary injection。

示例话术：

```text
使用 forma-creator 生成这套 workflow，技能名前缀用 `settings-workflow`。
生成前先展示拟定的技能名；我确认后再生成并验证 bundle。
```

规则：

- creator 生成的 injection 应使用 `rename.prefix` 生成 `<prefix>-plan`、`<prefix>-ground`、`<prefix>-lock`、`<prefix>-execute`、`<prefix>-showhand`；
- creator 生成的 injection 只在覆盖单个阶段完整技能名时使用 `rename.stages`；
- 内部 injection map 使用内部阶段键 `shape`、`gauge`、`seal`、`pour`、`flow`，不要用 `plan`、`showhand` 或 `forma-*` direct skill 名这类最终输出名当键；
- 名字必须唯一，必须是 kebab-case，不能直接叫裸阶段名 `shape` 或 `flow`；
- creator 的一次性注入不接受 profile 风格的 `stages.shape.name`。长期命名进 profile，临场命名进 `rename`。
- 通过 `forma-creator` 生成 plugin 时，`rename.prefix` 也会成为 plugin id/name。没有 prefix 时，plugin id/name 保持 `forma`。
- 通过 `forma-creator` 生成 plugin 时，`plugin.display_name` 设置 Codex plugin 安装界面的展示名，不改变 plugin id/name。
- Plugin-local skill 名会在存在精确 plugin-name 前缀时去掉该前缀。Plugin 使用 `<plugin-id>:<local-skill>` 触发，默认 Forma plugin 是 `forma:*`；direct skill bundle 使用 `forma-*`。

改名后验证生成 bundle：

```bash
forma verify <generated-bundle-dir>
```

## 仓库检查

维护 Forma 仓库时，先完成本地开发安装，再从仓库根目录运行主要检查：

```bash
forma verify source/skill-creator/
python -m pytest -p no:cacheprovider tests/
git diff --check
```

## 源码结构

- `source/methodology/`：生成 task 级 workflow skills 的标准方法。
- `source/skill-creator/`：自包含的 `forma-creator` 源码，包含 references、creator script 和 verifier。
- `src/forma/`：Python CLI、profile compiler、runtime asset resolver 和 target emitters。
- `.forma/`：Forma 管理本仓库时使用的 profile。
- `examples/profiles/`：profile 示例。
- sample 生成产物需要时在本地生成，不提交到仓库。
- `tests/`：verifier、creator、runtime asset、profile 和 CLI 行为测试。

详细源码结构见 [仓库结构](../STRUCTURE.md)。

## 安装后的命令行为

打包安装后的 Forma 命令默认使用 `forma.assets` 中的运行时资源。源码路径只作为开发覆盖：

- `forma build bundle` 和 `forma build plugin` 默认使用打包内置的方法，除非提供 `--methodology`。
- `forma install` 只安装 verified 本地产物，不下载 URL。
- `forma build creator` 默认使用打包内置的 creator 源，除非提供 `--source`。
- `forma explain` 从打包内置的 references 渲染编写指南。

因此，通过 `forma-cli` 发行包安装后的命令不依赖 Forma 源码仓库。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：阶段、task 契约、门禁、边界和证明。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构和 manifest。
- [Profile Schema](./profile-schema.zh-CN.md)：profile 如何描述阶段约束、工具习惯、验证和 proof。
- [Forma Creator](./forma-creator.zh-CN.md)：可选临场 workflow 生成路径。
- [Verifier](./verifier.zh-CN.md)：验证检查和限制。
- [Targets](./targets.zh-CN.md)：target 安装和 metadata 行为。
