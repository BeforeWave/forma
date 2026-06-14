# Examples

英文版：[examples.md](./examples.md)

这一页不再用临时编造的 task contract。仓库里已经有两类更有说服力的材料：

- `examples/profiles/`：来自真实 workflow 家族、脱敏后的 sample profile，展示团队准则如何进入 Forma。
- `plans/issue-*/`：Forma 开发过程自己留下的真实 plan、tasks 和 run proof，展示 workflow 如何在任务里落成 contract。

## 怎么读这些例子

| 材料 | 看什么 |
|---|---|
| sample profile | 团队长期准则如何表达：证据优先级、边界、验证、proof、停手条件、工具和 source adapter。 |
| 本地生成产物 | 自己运行 build 命令后，profile 编译成什么 skill bundle，skill 名字、references、scripts 和 manifest 如何落盘。 |
| tracked run | 具体任务如何留下 `plan.md`、`tasks.md`、`runs/task-*.md`，以及验证 proof。 |

## Sample Software Profile

入口：

```text
examples/profiles/sample-software/sample-software-plan-first.yaml
```

这组 sample 来自一个脱敏的软件 workflow 家族。它不是某个具体私有项目的原文，但准则形态来自真实使用方式。

它展示的团队准则包括：

- plan 阶段只做 chat-level 收敛，不读仓库、不写文件、不实现；
- 进入实现前必须收敛 Goal、Scope、Approach、Validation、Plan Strategy、Impact Profile、Impact Boundary 和 source-of-truth needs；
- 用 Impact Profile 区分 frontend、backend、fullstack 或 generic；
- grounding 只读确认项目规则、source of truth、目标 surface、验证命令和 protected/generated paths；
- `seal` 只有在 decision gate 完成并且 grounding 被 review 后，才写 `plan.md` 和 `tasks.md`；
- `pour` 只执行第一个未完成 task，发现 plan assumptions、source of truth 或 validation model 不成立就停；
- `flow` 只有在 decision、grounding、seal、validation、source-of-truth 和 worktree safety gates 都通过时才自动继续。

它还把长期 references 按阶段分发，例如：

- `software-control-model.md`
- `software-impact-profiles.md`
- `software-artifact-evidence-boundary.md`
- `software-feedback-and-proof.md`
- `software-review-checks.md`

这组 sample 的价值是：它展示一个团队如何把“我们怎么接受 agent 的计划”写成 profile，而不是把每个未来任务的命令写死。

## Sample Backend Profile

入口：

```text
examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml
```

这组 sample 来自脱敏 backend workflow。它叠加了通用 backend 准则、development overlay、Go language overlay 和 GitHub issue source adapter。

它展示的团队准则包括：

- backend 修改要限制在当前 issue 需要的行为范围内；
- 优先修 root cause，保持 backward compatibility，避免通过 logs、errors 或 debug output 泄露敏感信息；
- plan 阶段要先判断请求是否影响 public API behavior、service behavior、stream payloads、persistence 或 data flow；
- 先区分 API / stream contract-visible change 和 internal logic / storage / queue / computation change；
- API 或 stream 变化在 finalizing plan 前需要 approved contract 或 source handoff；
- 实现阶段如果发现 API / stream 变化不在 sealed plan 里，必须停下来 re-plan；
- Go overlay 要求 edited Go files 运行 formatter，优先 module-local Go tests，行为变更要加或更新 Go tests；
- GitHub issue helper 不是基础能力，而是由这个 profile 明确在 `shape` 和 `seal` 阶段选择。

这组 sample 的价值是：同样是 backend 工作，profile 不只是“后端团队规则”，而是把 API/stream impact、source adapter、Go validation 和 stop conditions 分别放到正确阶段。

## 本地生成 sample

sample 的生成产物不再提交。想查看编译后的结构时，在本地生成：

```bash
forma build bundle --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/forma-sample-backend-codex

forma verify /tmp/forma-sample-backend-codex
```

生成结果会体现同样的 profile resource 行为：

- stage skill 目录被 profile 重命名为 `backend-plan-first-*`；
- `shape` / `seal` 阶段带 GitHub issue context script；
- implementation 和 showhand 阶段没有无条件带 GitHub issue helper；
- references 按阶段复制到对应 skill；
- `.forma-manifest.json` 记录 target、生成 skill 名称、profile 顺序和 source hash。

## Real Forma Runs

Forma 自己的开发一直用 `plans/issue-*/` 记录 workflow 过程。这些不是文档示例，而是本项目真实留下的 task contract 和 proof。

可以先看这几个：

| Run | 看点 |
|---|---|
| `plans/issue-workflow-injection-contracts/` | temporary injection classification contract：如何把自然语言规则分类到 default、stage constraints 或 conditional overlays。 |
| `plans/issue-codex-plugin-profile-naming/` | Codex plugin identity、renamed skill propagation、verifier negative proof 和安装边界。 |
| `plans/issue-bundle-plugin-install-surface/` | `build bundle` / `build plugin` / `install` release surface、dist 产物和 docs 更新。 |

每个 issue 里都有：

- `plan.md`：目标、范围、approach、artifact/evidence boundary、constraints、validation；
- `tasks.md`：已接受 task、acceptance、validation、depends、constraints；
- `runs/task-*.md`：每个 task 的 changed files、validation results、risk notes。

例如 `plans/issue-workflow-injection-contracts/plan.md` 明确要求：

- natural-language constraints 先分类，再写 temporary injection JSON；
- `constraints.default` 保持最轻；
- planning/materialization 规则进 `shape`、`gauge` 或 `seal`；
- execution 规则进 `pour` 或 `flow`；
- docs、generated-baseline、migration、governance、coordinated multi-surface 等重规则进 conditional overlays；
- GitHub issue fetching 这类 source adapter 必须由 profile 或 temporary injection 显式选择。

对应 `runs/task-*.md` 记录了实际执行 proof，包括 changed files、通过的 test / verify 命令和风险记录。

## 常见误读

- sample profile 不是 profile schema 教科书；它展示的是脱敏后的真实团队准则形态。
- 本地生成产物不是 runtime 成功证明；它只展示所选 profile 和 target 的 compiler 输出结构。
- `plans/issue-*/runs/` 才是本项目真实任务执行 proof。
- task contract 里的具体命令和文件边界不是 profile 原文；它们是 profile 准则落到当前任务后的结果。

## 相关文档

- [Workflow Contract](./workflow-contract.zh-CN.md)：task contract 如何组织事实、边界、验证和 proof。
- [Profile Schema](./profile-schema.zh-CN.md)：sample profile 的 YAML 格式。
- [Skill Bundle](./skill-bundle.zh-CN.md)：生成产物结构。
- [Verifier](./verifier.zh-CN.md)：验证边界。
