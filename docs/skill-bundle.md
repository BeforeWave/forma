# Skill Bundle

Chinese version: [skill-bundle.zh-CN.md](./skill-bundle.zh-CN.md)

A skill bundle is Forma's compiled artifact.

The profile is source. The Forma compiler resolves that source with the
canonical methodology and target adapter, then emits a bundle that can be
installed into Codex or Claude Code.

## Source To Artifact

```text
workflow profile
+ methodology
+ target adapter
+ optional temporary injection
        |
        v
Forma compiler
        |
        v
target-specific skill bundle
```

The same workflow profile can be emitted for multiple targets without
rewriting the workflow rules by hand.

## Bundle Layout

A generated plan-first bundle normally contains five stage skill directories and
one manifest:

```text
<bundle>/
  <shape-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml        # Codex target only, when required
  <gauge-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  <seal-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  <pour-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  <flow-skill>/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  .forma-manifest.json
```

Directory names may be renamed by a profile or temporary injection. The manifest
records which directory implements each semantic stage.

Not every skill has every subdirectory. `references/` and `scripts/` appear only
when methodology, profile, or temporary injection selects them for that stage.

A real committed sample looks like this:

```text
examples/generated/sample-backend-go-github-issue-tracked-plan-first-codex/
  backend-plan-first-plan-issue/
  backend-plan-first-ground-plan/
  backend-plan-first-finalize-plan/
  backend-plan-first-implement-feature/
  backend-plan-first-showhand/
  .forma-manifest.json
```

Those names come from the sample profile. They still map back to the semantic
stages `shape`, `gauge`, `seal`, `pour`, and `flow` in the manifest.

## Skill Directory

Each generated skill directory is a target-readable unit.

`SKILL.md` contains:

- skill frontmatter;
- stage purpose;
- workflow instructions;
- load-as-needed references;
- profile constraints selected for that stage;
- validation or proof expectations when applicable.

`references/` contains larger stable guidance that should not be duplicated into
the stage body.

`scripts/` contains explicit helper scripts selected by methodology, profile, or
temporary injection. Source readers and helper scripts are not base capability;
they should appear only when selected by the workflow source.

Target metadata is emitted only when the target requires it. Codex bundles may
include `agents/openai.yaml`; Claude Code bundles should not contain Codex-only
metadata.

## Manifest

`.forma-manifest.json` is the bundle provenance record.

It records information such as:

- target;
- bundle kind (`bundle_kind`) and mode;
- generated skill names and directories;
- methodology version or digest;
- resolved profile order;
- profile and resource hashes;
- generator version and provenance.

The manifest lets reviewers and tools answer: what source produced this bundle,
for which target, and with which emitted skills?

## Generated Skill Quality

A generated bundle should feel like a workflow, not a pile of copied policy.

Good bundles usually have:

- one clear job per skill;
- short trigger descriptions;
- stage-specific standing instructions;
- stable detail in `references/`;
- scripts only when a stage explicitly owns them;
- light default constraints;
- route-specific behavior in conditional overlays;
- visible validation or proof paths for executable stages.

If every skill repeats every rule, the profile is probably too global. Move
rules into stage constraints, references, resources, or conditional overlays.

## Install Locations

| Target | Personal install | Project/team install |
|---|---|---|
| Codex skills | `$HOME/.codex/skills` | `.codex/skills` |
| Claude Code | `$HOME/.claude/skills` | `.claude/skills` |

See [Targets](./targets.md) for discovery rules, target metadata, and trust
guidance.

## Verification

Run:

```bash
forma verify <generated-bundle-dir>
```

Verification checks structure and methodology rules. It does not prove the
profile is a good product decision or that generated policy is semantically
complete. See [Verifier](./verifier.md). Human review still matters.

## Related Docs

- [Workflow Contract](./workflow-contract.md): stages, gates, boundaries, and proof.
- [Profile Schema](./profile-schema.md): source format that produces bundles.
- [Targets](./targets.md): install locations and target behavior.
- [Verifier](./verifier.md): verification checks and limits.
- [Usage](./usage.md): command reference and install commands.
