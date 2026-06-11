# Task Evidence

- Task: [stage-vocabulary-and-lock-policy] Replace legacy stage terminology and unconditional commit policy
- Completed At (UTC): 2026-06-11T07:41:57Z
- Commit Hash: Recorded in the commit that introduces this evidence file.

## Changed Files
- docs/skill-bundle.md
- docs/skill-bundle.zh-CN.md
- plans/issue-forma-workflow-adapter-description-cleanup/implement-notes.md
- source/methodology/fragments/flow/automated-execution-adds.md
- source/methodology/fragments/seal/decision-gate-adds.md
- source/methodology/fragments/seal/entry-gate.md
- source/methodology/fragments/seal/plan-materialization-adds.md
- source/methodology/fragments/shape/artifact-evidence-boundary-adds.md
- source/methodology/fragments/shape/handoff-adds.md
- source/methodology/resources/shape/references/output-format.md
- source/methodology/resources/shape/references/plan-stage-rules.md
- source/methodology/resources/shared/references/execution-rules.md
- source/methodology/resources/shared/references/implement-notes.md
- source/methodology/resources/shared/references/planning-rules.md
- source/methodology/resources/shared/scripts/forma-workflow.sh
- source/methodology/stages/flow.md
- source/methodology/stages/gauge.md
- source/methodology/stages/seal.md
- source/methodology/stages/shape.md
- source/skill-creator/references/canonical-plan-first.md
- source/skill-creator/scripts/create.py
- source/skill-creator/scripts/forma_verifier/rules.py
- tests/test_cli.py
- tests/test_creator.py
- tests/test_runtime_assets.py
- tests/test_verifier.py
- tests/test_workflow_runner.py

## Validation Results
- PASS [task]: if rg -n "finalize-plan|plan-issue|ground-plan|implement-feature" source/methodology source/skill-creator docs tests; then exit 1; fi
- PASS [task]: rg -n "user confirmation|explicit user permission|only after explicit" source/methodology source/skill-creator

## Risks / Unresolved Items
- None recorded.
