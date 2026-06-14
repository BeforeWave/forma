- [x] [inventory-language-boundaries] Produce the current language-boundary inventory
Accept: Task Type=gate; current terminology residues are classified as public/product explanation, execution-surface pollution, historical/deferred residue, or neutral-but-contaminated wording before source cleanup begins
Validate: python3 -c "from pathlib import Path; p=Path('plans/issue-architecture-language-boundary-cleanup/implement-notes.md'); text=p.read_text(encoding='utf-8'); required=['public/product explanation','execution-surface pollution','historical/deferred residue','neutral-but-contaminated']; missing=[item for item in required if item not in text]; raise SystemExit('missing inventory categories: '+', '.join(missing) if missing else 0)"
Depends: none
Constraint: do not edit source/docs/tests in this task except the active issue implement-notes inventory
Constraint: inventory must include layer and non-layer residues: old numbered architecture terms, polluted cross-layer route, suite wording, stage-key leakage, conditional_overlays wording, same-origin/base_origin agent-facing wording, and bootstrap wording boundary

- [x] [clean-self-profile-source] Clean `.forma` execution source and self-profile references
Accept: Task Type=step; `.forma` self-profile source uses neutral path-level, command-level, and surface-level language, introduces `cross-surface` for coordinated multi-surface work, and no longer emits old numbered architecture or polluted cross-layer route guidance
Validate: rg -n "Layer [123]|Layer impact|Layer Boundaries|Layer 3 profile|Layer 1 temporary|\\bcross-layer\\b|generated suite|temporary generated suites" .forma && exit 1 || exit 0
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_build.py
Use-Check: self-profile-verify
Depends: inventory-language-boundaries
Constraint: keep `.forma` default constraints lightweight; heavy governance/docs/generated-output reads must remain route-specific
Constraint: generated self-profile output must stay under `/tmp`, `/private/tmp`, or `$TMPDIR` and must not be committed to `dist/`

- [x] [clean-runtime-guidance] Clean source and runtime guidance strings
Accept: Task Type=step; `source/agent-guide/`, `source/skill-creator/`, relevant `source/methodology/` text, and `src/forma/` docstrings or generated guidance strings use product/schema/path language at the right boundary without exposing implementation maintenance labels as user or agent protocol
Validate: rg -n "Layer [123]|Layer impact|Layer Boundaries|Layer 3 profile|Layer 1 temporary|\\bcross-layer\\b|generated suite|temporary generated suites" source src && exit 1 || exit 0
Use-Check: creator-source-verify
Depends: clean-self-profile-source
Constraint: do not change creator, verifier, generator, installer, drift, adoption, or doctor behavior except wording/constants/tests required by this cleanup
Constraint: keep schema/API field names such as `conditional_overlays` and `base_origin` where they are actual machine-readable fields; rewrite only inappropriate agent-facing or reader-facing prose

- [x] [clean-docs-examples-structure] Clean reader-facing docs, examples, and structure map
Accept: Task Type=step; `README*`, `docs/`, `examples/`, `STRUCTURE.md`, and `AGENTS.md` separate public product concepts from internal implementation structure, using plain reader language unless a schema/API/source-map term is explicitly being taught
Validate: rg -n "Layer [123]|Layer impact|Layer Boundaries|Layer 3 profile|Layer 1 temporary|\\bcross-layer\\b|generated suite|temporary generated suites" README.md README.zh-CN.md docs examples STRUCTURE.md AGENTS.md && exit 1 || exit 0
Use-Check: docs-links
Depends: clean-runtime-guidance
Constraint: do not remove legitimate schema/API terminology from schema docs; instead explain it as schema where it appears
Constraint: do not refresh or edit `dist/skills/*/forma-creator` in this task

- [ ] [update-current-tests-and-gate] Update tests and terminology gate
Accept: Task Type=step; current tests assert the cleaned terminology, renamed route, renamed dogfood concepts, and a gate that excludes historical `plans/**` plus deferred `dist/skills/*/forma-creator` while checking active source/docs/tests surfaces
Validate: uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_build.py tests/test_docs_links.py
Validate: python3 -c "import pathlib,re,sys; roots=[pathlib.Path(p) for p in ['.forma','source','src','docs','examples','tests','README.md','README.zh-CN.md','STRUCTURE.md','AGENTS.md']]; patterns=[r'Layer [123]',r'Layer impact',r'Layer Boundaries',r'Layer 3 profile',r'Layer 1 temporary',r'\\bcross-layer\\b',r'generated suite',r'temporary generated suites']; offenders=[]; [offenders.append(f'{path}:{i}:{line.strip()}') for root in roots for path in ([root] if root.is_file() else root.rglob('*')) if path.is_file() and '.git' not in path.parts and path.suffix not in {'.pyc'} for i,line in enumerate(path.read_text(encoding='utf-8',errors='ignore').splitlines(),1) if any(re.search(p,line) for p in patterns)]; print('\\n'.join(offenders)); sys.exit(1 if offenders else 0)"
Use-Check: workflow-build-focused
Use-Check: diff-check
Depends: clean-docs-examples-structure
Constraint: rename `tests/test_layer_1_dogfood.py` and related symbols to behavior/path terminology if that file remains in scope
Constraint: terminology gate must not scan historical `plans/**` or deferred `dist/skills/*/forma-creator` as blocking residues
