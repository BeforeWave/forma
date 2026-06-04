---
name: flow
description: Execute all remaining tasks automatically after a sealed plan exists.
---

# Flow

## Workflow

`flow` runs after `seal` when the user wants automated execution of every
remaining task. It still honors validation, safety policy, permission gates, and
the immutable `plan.md` contract.

## Output

Report completed tasks, validation results, and evidence paths.
