# AGENTS

This directory is Forma's canonical methodology source. It defines the base
stage behavior, bundled references, fragments, and runner scripts used to
generate workflow skills.

Do not modify files under this directory casually. Change methodology source
only after the user explicitly accepts that the requested behavior belongs in
the shared generated workflow methodology, not only in one repository profile,
example, documentation page, or local installed artifact.

Prefer narrower surfaces first:

- use a project profile for project-specific workflow rules;
- use profile `workflow_adds` or `output_adds` for project-specific stage
  workflow gates or output fields;
- use documentation changes when only public explanation is wrong;
- use tests or local scripts when only implementation validation is missing.

Before updating methodology files, first organize the existing semantics across
the relevant stage source, fragments, references, and scripts. Decide whether
the behavior is already present, whether the existing wording should be
strengthened, whether the rule belongs in a different methodology surface, or
whether no methodology change is needed.

When a methodology change is needed, edit the owning source of truth instead of
adding a duplicate sentence in another section. Repetition is acceptable only
when separate sections serve different purposes, such as a short interaction
boundary plus a concrete workflow step. Do not repeat the same point merely to
make it louder; duplicated methodology text makes generated skills harder to
scan and easier to drift.
