# Skill Bundle

Chinese version: [skill-bundle.zh-CN.md](./skill-bundle.zh-CN.md)

A skill bundle is the workflow output Forma compiles and installs for an agent.

Profiles or temporary injection provide project rules. The Forma compiler
combines those rules with the methodology and target adapter, then emits skills
for Codex or Claude Code. Once installed, those skills make the agent turn a
concrete goal into a task contract: facts, boundaries, tasks, validation, proof,
and stop conditions.

## From Rules To Workflow Output

```text
profile / temporary injection
+ methodology
+ target adapter
        |
        v
Forma compiler
        |
        v
target-specific workflow skill bundle
```

The same workflow profile can be emitted for multiple targets without writing a
separate rule set for each tool. One-off creator output lands in the same bundle
structure.

## Bundle Layout

A generated bundle normally contains four core workflow skills,
`forma-showhand` as the autopilot entrypoint, and one manifest:

```text
<bundle>/
  forma-plan/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml        # Codex target only, when required
  forma-ground/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  forma-lock/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  forma-execute/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  forma-showhand/
    SKILL.md
    references/
    scripts/
    agents/openai.yaml
  .forma-manifest.json
```

Directory names may be renamed by a profile or temporary injection. The
manifest records the final emitted skill names and directories.

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

Those names come from the sample profile. The manifest records the final
emitted skill names and directories.

## Skill Directory

Each generated skill directory is a target-readable unit.

`SKILL.md` contains:

- skill frontmatter;
- stage purpose;
- workflow instructions;
- load-as-needed references;
- project rules selected for that stage;
- validation gate or proof expectations when applicable.

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

A generated bundle should distribute project rules to the right stages instead
of copying a pile of policy into every skill.

Good bundles usually have:

- one clear job per skill;
- short trigger descriptions;
- stage-specific rules;
- stable detail in `references/`;
- scripts only when a stage explicitly owns them;
- light default constraints;
- route-specific behavior in conditional overlays;
- visible validation gates, proof paths, and stop conditions for executable stages.

If every skill repeats every rule, the profile or temporary injection is
probably too global. Move rules into stage constraints, references, resources,
or conditional overlays.

## Install Locations

| Target | Personal install | Project install |
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
profile or on-the-spot rules are good project decisions, and it does not prove
the real task contract will be semantically complete. See
[Verifier](./verifier.md). Human review still matters.

## Related Docs

- [Workflow Contract](./workflow-contract.md): stages, gates, boundaries, and proof.
- [Profile Schema](./profile-schema.md): source format that produces bundles.
- [Targets](./targets.md): install locations and target behavior.
- [Verifier](./verifier.md): verification checks and limits.
- [Usage](./usage.md): command reference and install commands.
