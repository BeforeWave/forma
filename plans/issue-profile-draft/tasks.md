- [x] [profile-draft-cli-contract] Add the profile draft command and file boundary
Accept: Task Type=step; `forma profile draft` exists with the settled options, validates source/output/profile-id behavior, writes a three-file draft package, and makes the initial `profile.draft.yaml` pass `load_profile()`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_profile_draft.py -k "cli_contract or source_boundary or output_policy or load_profile_self_check"
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py -k "profile_draft"
Depends: none
Constraint: do not change `create-bundle`, `create-plugin`, `install`, `verify`, or `explain` runtime behavior.
Constraint: do not edit `dist/`, `examples/generated/`, `source/methodology/`, `source/skill-creator/`, or `profiles/forma-self/`.

- [x] [profile-draft-extractor] Classify conservative rules, validation commands, and missing decisions
Accept: Task Type=step; explicit source documents are parsed into high-confidence stage-specific constraints and validation commands while ambiguous, heavy, route-specific, adapter-like, or one-off material is reported in `missing-decisions.md`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_profile_draft.py -k "extractor or classification or validation_commands or missing_decisions or unsupported_source"
Depends: profile-draft-cli-contract
Constraint: keep `constraints.default` minimal and never place broad reading, generated-baseline, governance, adapter, or route-specific requirements there by default.
Constraint: no LLM/API/network call may be part of extraction.

- [ ] [profile-draft-docs-smoke] Document the draft workflow and prove the generated draft can build a bundle
Accept: Task Type=step; English and Chinese docs describe `forma profile draft` as a reviewable candidate-profile package, CLI help routes agents to it, and a smoke draft can feed `forma create-bundle` plus `forma verify`
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_profile_draft.py tests/test_cli.py tests/test_docs_links.py
Validate: tmp_root=/private/tmp/forma-profile-draft-task-smoke; rm -rf "$tmp_root"; mkdir -p "$tmp_root/source"; printf '%s\n' '# Agent Rules' '- Preserve unrelated user work.' '- Clarify scope before implementation.' '- Validate with `python -m pytest tests/`.' > "$tmp_root/source/AGENTS.md"; uv run --extra dev forma profile draft --profile-id task-smoke-profile --source "$tmp_root/source" --output "$tmp_root/draft"; uv run --extra dev forma create-bundle --target codex --profile "$tmp_root/draft/profile.draft.yaml" --output "$tmp_root/bundle"; uv run --extra dev forma verify "$tmp_root/bundle"
Use-Check: cli-focused
Use-Check: docs-links
Depends: profile-draft-extractor
Constraint: docs must state that `profile.draft.yaml` is not durable source until reviewed and moved into the owning profile path.
