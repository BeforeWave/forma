# Rework Ledger

## Rework 001: Forma adoption reader value and wording alignment

Source:
- direct-human-feedback

Feedback:
- The current repo-doctor work correctly moved Forma adoption away from asking whether to keep `.forma`, but the surrounding docs and CLI text need the same product framing.
- Reader-facing docs should follow the reader-ready-docs principle: preserve the existing README opening and product model, then add the direct user value instead of replacing the first screen.
- The direct value should be concrete: fewer repeated reminders, less drift, clearer review evidence, and more consistent validation because project rules enter the agent workflow.
- Old implementation-first wording such as "base configuration", "handoff inputs", weak "optional integration", or "whether to keep `.forma`" should not remain in user-facing surfaces when the intended concept is workflow source and project-rule management.
- JSON and rendered output should use consistent `owner_confirmations` terminology for user approval points.

Classification:
- delivery-revision

Same-Issue Rationale:
- This remains inside the active repo-doctor agent-operability issue because the accepted work changed doctor, init-from-report, explain guidance, and docs for the same user-facing handoff path.
- The correction does not change the issue goal or acceptance model; it tightens the delivered wording and report contract so the Agent can present Forma adoption accurately.
- The rework can be executed as ordinary source, docs, and test updates with the existing validation gates.

User Confirmation:
- confirmed: user requested `forma:rework` for this corrective feedback in the side conversation.

Appended Tasks:
- rework-001-reader-value-docs
- rework-001-cli-adoption-contract
