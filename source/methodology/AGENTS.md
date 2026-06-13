# AGENTS

This directory is Forma's canonical methodology source. It defines the base
stage behavior, bundled references, fragments, and runner scripts used to
generate workflow skills.

Do not modify files under this directory casually. Before changing methodology
source, confirm with the user that the requested behavior should apply to the
shared generated workflow methodology, not only to one repository profile,
example, documentation page, or local installed artifact.

Prefer narrower surfaces first:

- use a project profile for project-specific workflow rules;
- use profile `workflow_adds` or `output_adds` for project-specific stage
  workflow gates or output fields;
- use documentation changes when only public explanation is wrong;
- use tests or local scripts when only implementation validation is missing.

Modify methodology source only after the user explicitly accepts that the change
belongs in the shared methodology layer.
