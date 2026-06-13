# Examples

Chinese version: [examples.zh-CN.md](./examples.zh-CN.md)

This page is grounded in repository evidence. The repository has two useful
evidence surfaces:

- `examples/profiles/`: sanitized sample profiles derived from real workflow families.
- `plans/issue-*/`: real Forma development plans, accepted tasks, and run proof.

## How To Read These Examples

| Material | What to inspect |
|---|---|
| Sample profile | How long-term team rules are expressed: evidence priority, boundaries, validation, proof, stop conditions, tools, and source adapters. |
| Local generated output | What a compiled skill bundle looks like after you run the build command yourself: skill names, references, scripts, and manifest. |
| Tracked run | How one concrete task records `plan.md`, `tasks.md`, `runs/task-*.md`, and validation proof. |

## Sample Software Profile

Entry point:

```text
examples/profiles/sample-software/sample-software-plan-first.yaml
```

This sample comes from a sanitized software workflow family. It is not a
verbatim private project profile, but the rule shape comes from real usage.

It shows rules such as:

- the planning stage stays chat-level: no repository reads, no file writes, no implementation;
- implementation cannot start until Goal, Scope, Approach, Validation, Plan Strategy, Impact Profile, Impact Boundary, and source-of-truth needs are settled;
- Impact Profile classifies the primary surface as frontend, backend, fullstack, or generic;
- grounding reads project rules, source of truth, target surfaces, validation commands, and protected/generated paths read-only;
- `seal` writes `plan.md` and `tasks.md` only after the decision gate is complete and grounding has been reviewed;
- `pour` executes only the first incomplete task and stops when plan assumptions, source of truth, or the validation model prove wrong;
- `flow` continues automatically only when decision, grounding, seal, validation, source-of-truth, and worktree safety gates all pass.

It also distributes stable references by stage, including:

- `software-control-model.md`
- `software-impact-profiles.md`
- `software-artifact-evidence-boundary.md`
- `software-feedback-and-proof.md`
- `software-review-checks.md`

The point of this sample is to show how a team turns "what makes an agent plan
acceptable here" into profile source without hard-coding commands for every
future task.

## Sample Backend Profile

Entry point:

```text
examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml
```

This sample comes from a sanitized backend workflow. It composes generic backend
rules, a development overlay, a Go language overlay, and a GitHub issue source
adapter.

It shows rules such as:

- backend changes stay scoped to the behavior required by the current issue;
- prefer root-cause fixes, preserve backward compatibility, and avoid leaking sensitive data through logs, errors, or debug output;
- planning must decide whether the request changes public API behavior, service behavior, stream payloads, persistence, or data flow;
- API / stream contract-visible changes are separated from internal logic, storage, queue, or computation changes before proposal-ready;
- API or stream changes need an approved contract or source handoff before finalizing the plan;
- implementation stops and replans if API or stream changes appear outside the sealed plan;
- the Go overlay requires formatting edited Go files, prefers module-local Go tests, and adds or updates tests for behavior changes;
- the GitHub issue helper is not base capability; this profile explicitly selects it for `shape` and `seal`.

The point of this sample is that "backend rules" are not one blob. API/stream
impact, source adapters, Go validation, and stop conditions belong in different
stages.

## Build A Sample Locally

Generated sample outputs are not committed. Build a sample locally when you want
to inspect compiled structure:

```bash
forma build bundle --target codex \
  --profile examples/profiles/sample-backend/sample-backend-go-github-issue-tracked.yaml \
  --output /tmp/forma-sample-backend-codex

forma verify /tmp/forma-sample-backend-codex
```

The generated output will show the same profile resource behavior:

- stage skill directories are renamed to `backend-plan-first-*`;
- `shape` and `seal` include the GitHub issue context script;
- implementation and showhand stages do not include the GitHub helper unconditionally;
- references are copied only into the stages that selected them;
- `.forma-manifest.json` records target, emitted skill names, profile order, and source hashes.

## Real Forma Runs

Forma's own development process is tracked under `plans/issue-*/`. These are
not documentation mockups; they are real task contracts and proof records left
by this project.

Start with:

| Run | What it shows |
|---|---|
| `plans/issue-workflow-injection-contracts/` | The temporary injection classification contract: natural-language rules routed to defaults, stage constraints, or conditional overlays. |
| `plans/issue-codex-plugin-profile-naming/` | Codex plugin identity, renamed skill propagation, verifier negative proof, and install boundaries. |
| `plans/issue-bundle-plugin-install-surface/` | `build bundle`, `build plugin`, `install`, release surface, dist artifacts, and docs updates. |

Each issue contains:

- `plan.md`: goal, scope, approach, artifact/evidence boundary, constraints, and validation;
- `tasks.md`: accepted tasks, acceptance, validation, dependencies, and constraints;
- `runs/task-*.md`: changed files, validation results, and risk notes for each task.

For example, `plans/issue-workflow-injection-contracts/plan.md` requires:

- natural-language constraints are classified before temporary injection JSON is written;
- `constraints.default` stays minimal;
- planning and materialization rules go into `shape`, `gauge`, or `seal`;
- execution rules go into `pour` or `flow`;
- broad docs, generated-baseline, migration, governance, and cross-layer rules go into conditional overlays;
- source adapters such as GitHub issue fetching must be explicitly selected by a profile or temporary injection.

The matching `runs/task-*.md` files record execution proof: changed files,
passing test / verify commands, and risk notes.

## Common Misreads

- A sample profile is not a schema tutorial. It is a sanitized shape of real team rules.
- Locally generated output is not runtime success proof. It only shows compiler output structure for the selected profile and target.
- `plans/issue-*/runs/` is where this project records real task execution proof.
- Exact commands and file boundaries in a task contract are not raw profile text; they are the result of applying profile rules to the current task.

## Related Docs

- [Workflow Contract](./workflow-contract.md): how task contracts organize facts, boundaries, validation, and proof.
- [Profile Schema](./profile-schema.md): YAML format for sample profiles.
- [Skill Bundle](./skill-bundle.md): generated output layout.
- [Verifier](./verifier.md): verification boundary.
