# Verifier

Chinese version: [verifier.zh-CN.md](./verifier.zh-CN.md)

`forma verify` checks generated workflow bundles, `forma-creator` bundles, and
Codex / Claude Code plugin outputs.

It is the engineering boundary before installation, commit, or sharing:
generated outputs must have valid structure, match the target contract, and
preserve the workflow shape needed to drive task contracts.

Verification checks the output, not the team rules themselves. On-the-spot rules
extracted by creator, tracked-profile project judgment, and proof sufficiency in
real tasks still need human review.

## When To Run It

Run verification:

- before installing a generated bundle, installing a Claude Code plugin, or
  handing a Codex plugin to Codex;
- before committing a generated baseline;
- after changing a profile;
- after creator on-the-spot generation;
- after temporary injection;
- after renaming generated skills;
- after changing methodology, target adapter, or verifier rules;
- before sharing a `forma-creator` bundle.

```bash
forma verify /tmp/settings-workflow-codex
forma verify --json /tmp/settings-workflow-codex
forma verify source/skill-creator/
```

## What It Checks

Verification currently focuses on deterministic structure and methodology
rules.

It checks areas such as:

- valid `SKILL.md` frontmatter;
- required `name` and `description` keys;
- kebab-case skill names;
- emitted skill names and directories matching the manifest;
- required body sections;
- referenced `references/*.md` files existing inside the same skill;
- script/resource paths not borrowing from sibling skill directories;
- workflow stage presence and stage identity;
- target-specific metadata rules, such as Codex metadata being present for
  Codex bundles and absent from Claude Code bundles when required;
- plugin manifest rules, such as `.codex-plugin/plugin.json` or
  `.claude-plugin/plugin.json` pointing at the nested `skills/` directory;
- methodology-specific expectations for stages such as `shape`, `gauge`,
  `seal`, and `pour`.

The exact rule set lives in the bundled `forma_verifier` package and evolves
with Forma.

Use `forma verify --json <path>` when an agent, CI job, or handoff tool needs
machine-readable results. The JSON report includes the artifact path, bundle
kind, pass/fail summary, rule ids, severities, semantic failure classes, result
paths, and messages. The default human output is unchanged.

The bundled creator verifier supports the same JSON form:

```bash
python scripts/verify.py --json <generated-output>
```

## What It Does Not Check

Verification covers structure and methodology. Semantic review remains outside
the verifier scope.

It does not prove:

- the profile or on-the-spot rules are good project decisions;
- the generated workflow covers every important task contract for a project;
- every validation command, gate, or proof path is sufficient;
- external source adapters are authenticated or reachable;
- the agent will always behave correctly;
- generated examples reflect a real successful project run;
- temporary injection should become durable profile source.

Human review still matters.

## Common Verification Errors

| Error | Usual cause |
|---|---|
| Missing frontmatter keys | A generated or hand-written `SKILL.md` is not target-readable. |
| Name/directory mismatch | A renamed skill did not update manifest, directory, and frontmatter consistently. |
| Broken reference path | A skill points to a `references/*.md` file that was not copied into that skill. |
| Cross-skill borrowing | A generated skill reaches into a sibling skill's `references/` or `scripts/`. |
| Target metadata mismatch | Codex-only metadata appears in a Claude Code bundle, or Codex output lacks required metadata. |
| Methodology rule error | A stage lost core workflow behavior such as read-only grounding or review-gated execution. |

## Manifest And Drift

The manifest records what the compiler emitted: target, mode, emitted skill
names/directories, profile order, hashes, methodology provenance, and generator
metadata.

Verification uses that manifest to understand the bundle. Drift checks compare
committed generated baselines against what the current compiler should emit.

The manifest is provenance. Verification is conformance. Neither replaces
review of profile intent, on-the-spot rules, or real task contracts.

## CI Usage

CI can use `forma verify` to keep generated bundles structurally valid and to
catch drift in committed baselines:

```bash
forma verify source/skill-creator/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
forma verify examples/generated/sample-backend-go-github-issue-tracked-plan-first-claude-code/
python -m pytest -p no:cacheprovider tests/test_docs_links.py
git diff --check
```

These checks cover structure, target metadata, local Markdown links, whitespace,
and generated-bundle conformance. They do not replace review of profile intent,
on-the-spot rules, or runtime agent behavior.

## Bundled Verifier

Bundled verifier code lives organizationally inside `source/skill-creator/` so
a built `forma-creator` can verify generated bundles without requiring the user
to install the developer CLI.

The same verifier package is also used by the developer `forma verify` command.

## Related Docs

- [Skill Bundle](./skill-bundle.md): generated output layout and manifest.
- [Forma Creator](./forma-creator.md): creator path and bundled verification.
- [Usage](./usage.md): command reference.
