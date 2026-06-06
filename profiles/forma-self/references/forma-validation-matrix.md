# Forma Validation Matrix

Select the narrowest relevant validation first, then run the shared gate before review-ready when source behavior changed.

## Shared Gate

```bash
uv run --extra dev pytest -p no:cacheprovider tests/
uv run --extra dev forma verify source/skill-creator/
git diff --check
```

## Layer 1 And Layer 2

```bash
uv run --extra dev pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py
uv run --extra dev forma verify source/skill-creator/
```

Use this for creator skill source, verifier rules, target-layout rules, and agent-side verification behavior.

## Layer 3 Creator

```bash
uv run --extra dev pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py
```

Use this for profile loading, composition, emission, manifest provenance, output replacement, target adapters, and creator builder behavior.

## Committed Generated Baselines

```bash
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
uv run --extra dev forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
```

When the baseline should match fresh generation, run the relevant `forma create` command into a temporary directory and compare using the existing tests before committing.

## Documentation

```bash
rg -n -e "--inject|\\.plan-first" README.md README.zh-CN.md STRUCTURE.md
git diff --check README.md README.zh-CN.md STRUCTURE.md
```

Use this when documentation or public examples change.
