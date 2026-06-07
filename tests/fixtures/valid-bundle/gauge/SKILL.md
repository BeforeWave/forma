---
name: gauge
description: Inspect a repository read-only and produce a grounding handoff for seal.
---

# Gauge

## Workflow

`gauge` performs read-only repository inspection. It does not write files or
start execution. Its output is a grounding handoff for `seal`.

## Output

List confirmed facts, disconfirmed facts, open facts, and surfaced facts.
