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
sufficient. Do not run the full test suite by default for docs-only or
profile-only edits unless the task contract asks for it.

## Creator Or Verifier Gate

```bash
uv run --extra dev forma verify source/skill-creator/
```

Use this when creator skill source, bundled verifier behavior, or verifier
packaging is in scope. Do not treat it as a universal gate for unrelated docs,
profile, or CLI-only changes.

## Creator Source And Bundled Verifier

```bash
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py
uv run --extra dev forma verify source/skill-creator/
```

Use this for creator skill source, verifier rules, target-layout rules, and agent-side verification behavior.

## Profile Composer And Target Adapters

```bash
uv run --extra dev python -m pytest -p no:cacheprovider tests/test_creator.py tests/test_creator_builder.py
```

Use this for profile loading, composition, emission, manifest provenance, output replacement, target adapters, and creator builder behavior.

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
