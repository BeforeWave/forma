# Script Resource Adapter

Use this reference only when a profile or temporary injection explicitly adds a
stage-local helper script. It is not part of the base plan-first methodology.

## Scope

- Run injected helper scripts only in the stages whose `SKILL.md` constraints
  explicitly cite the generated `scripts/<name>` path.
- Do not infer that a script copied into one stage is available or required in
  any other stage.
- Treat script output as source context or evidence for the current stage, not
  as an automatic planning or implementation decision.
- If the script needs network access, local CLI authentication, private files,
  or other environment-specific state, treat failures as planning blockers and
  ask the user to provide the missing source material or configure the tool.
- If multiple source references are present and the stage-specific constraints
  do not say how to combine them, ask which source is authoritative instead of
  merging them silently.

## Shape

- Use injected source-reader scripts only to make planning context available
  before deciding whether the user's request is sufficiently grounded.
- If the script returns blocked, partial, ambiguous, or conflicting context,
  ask for clarification instead of drafting a plan from guesses.

## Seal

- Use injected source-reader scripts only to confirm source material that the
  final `plan.md` and `tasks.md` depend on.
- If the source material is missing, stale, contradictory, or inaccessible,
  block finalization until the user confirms the authoritative context.

## Execution Stages

- Do not rerun planning source-reader scripts during routine `pour` or `flow`
  unless those stages explicitly received their own injected constraints and
  script resources.
- A source-reader script injected into `shape` or `seal` does not make broad
  source refreshes part of daily task execution.
