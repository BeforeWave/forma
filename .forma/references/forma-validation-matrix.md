# Forma Validation Matrix

Select the narrowest relevant validation first. Run broader gates only when the
change touches the corresponding surface or when the task contract requires a
review-ready shared gate.

## Shared Source Gate

```bash
uv run --extra dev python -m pytest -p no:cacheprovider tests/
git diff --check
```

Use this when source behavior changed broadly enough that focused tests are not
sufficient. Docs-only and profile-only edits default to their narrow gates; run
the full test suite when the task contract asks for it or the change touches
shared behavior.

## Verifier Rules

```bash
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py
```

Use this for verifier rules, target-layout checks, and workflow-output verification behavior.

## Workflow Build And Target Output

```bash
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_build.py
```

Use this for canonical methodology, profile loading, target output, manifest provenance, and output replacement behavior.

## Committed Generated Baselines

Generated example output is not committed by default. When an active issue
explicitly introduces committed generated baselines, run the relevant
`forma build ...` command into a temporary directory, compare against the
committed baseline, and run `forma verify <generated-output>`.

## Documentation

```bash
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
git diff --check README.md README.zh-CN.md STRUCTURE.md AGENTS.md dist/AGENTS.md docs
```

Use this when documentation or public examples change.
