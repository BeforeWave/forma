"""Build target-specific installable Forma creator skills."""

from __future__ import annotations

import json
import shutil
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, List, Mapping

from forma.creator.composer import load_stage_sources
from forma.creator.manifest import build_creator_manifest
from forma.creator.profiles import DEFAULT_ENABLED_KINDS
from forma.origin import manifest_with_base_origin
from forma.runtime_assets import runtime_asset_path
from forma_verifier import verify
from forma_verifier.rules import parse_frontmatter


ADAPTER_TARGETS = ("codex", "claude-code", "opencode")
CREATOR_COMMON_ENTRIES = ("SKILL.md", "references", "scripts")
CREATOR_SKILL_NAMES = {
    "shape": "forma-plan",
    "gauge": "forma-ground",
    "seal": "forma-lock",
    "pour": "forma-execute",
    "flow": "forma-showhand",
}


def build_creator(
    source_dir: Path | None,
    output_dir: Path,
    target_agent: str,
) -> Path:
    """Emit target-fixed `forma-creator` bundles from the creator meta source."""
    _assert_target(target_agent)
    output_dir = output_dir.resolve()
    with creator_source_context(source_dir) as resolved_source_dir:
        skill_name = _skill_name(resolved_source_dir)
        target = output_dir / target_agent / skill_name
        _emit_creator_target(
            source_dir=resolved_source_dir,
            target_dir=target,
            target_agent=target_agent,
            skill_name=skill_name,
        )
    report = verify(target)
    if not report.passed:
        raise ValueError(report.format_human())
    return target


@contextmanager
def creator_source_context(source_dir: Path | None = None) -> Iterator[Path]:
    """Yield a creator source path from an override or packaged runtime assets."""
    if source_dir is not None:
        path = source_dir.resolve()
        _assert_creator_source(path)
        yield path
        return
    with runtime_asset_path("source") as source_root:
        path = source_root / "skill-creator"
        _assert_creator_source(path)
        yield path


def _assert_target(target_agent: str) -> None:
    if target_agent not in ADAPTER_TARGETS:
        allowed = ", ".join(ADAPTER_TARGETS)
        raise ValueError(f"unsupported adapter target {target_agent!r}; use {allowed}")


def _assert_creator_source(source_dir: Path) -> None:
    missing = [
        entry for entry in CREATOR_COMMON_ENTRIES if not (source_dir / entry).exists()
    ]
    if missing:
        missing_list = ", ".join(missing)
        raise ValueError(f"invalid creator source; missing {missing_list}")
    codex_interface = source_dir / "interfaces" / "codex" / "openai.yaml"
    if not codex_interface.is_file():
        raise ValueError(
            "invalid creator source; missing interfaces/codex/openai.yaml"
        )
    methodology_dir = _methodology_source(source_dir)
    if not methodology_dir.is_dir():
        raise ValueError(
            "invalid creator source; missing sibling methodology source directory"
        )


def _skill_name(source_dir: Path) -> str:
    text = (source_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, _ = parse_frontmatter(text)
    name = frontmatter.get("name")
    if not isinstance(name, str) or not name:
        raise ValueError("SKILL.md frontmatter must include a non-empty name")
    return name


def _emit_creator_target(
    source_dir: Path,
    target_dir: Path,
    target_agent: str,
    skill_name: str,
) -> None:
    if target_dir.exists():
        shutil.rmtree(target_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    for entry in CREATOR_COMMON_ENTRIES:
        if entry == "SKILL.md":
            _copy_skill_md_with_target(
                source_dir / entry,
                target_dir / entry,
                target_agent,
            )
        else:
            _copy_entry(source_dir / entry, target_dir / entry)
    _copy_methodology_resources(source_dir, target_dir)
    _write_target_reference(source_dir, target_dir, target_agent)
    if target_agent == "codex":
        agents_dir = target_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        shutil.copy2(
            source_dir / "interfaces" / "codex" / "openai.yaml",
            agents_dir / "openai.yaml",
        )
    _write_creator_manifest(source_dir, target_dir, target_agent, skill_name)


def _write_creator_manifest(
    source_dir: Path,
    target_dir: Path,
    target_agent: str,
    skill_name: str,
) -> None:
    manifest = build_creator_manifest(
        creator_source_dir=source_dir,
        methodology_dir=_methodology_source(source_dir),
        target_agent=target_agent,
        skill_name=skill_name,
    )
    manifest = manifest_with_base_origin(
        manifest,
        target_dir,
        target_agent,
        "creator",
    )
    (target_dir / ".forma-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _copy_skill_md_with_target(src: Path, dst: Path, target_agent: str) -> None:
    text = src.read_text(encoding="utf-8")
    if target_agent == "opencode":
        text = _opencode_creator_skill_md(text)
    text = text.rstrip() + "\n\n" + _target_section(target_agent)
    dst.write_text(text, encoding="utf-8")


def _opencode_creator_skill_md(text: str) -> str:
    marker = "---\n\n"
    metadata = "\n".join(
        [
            "compatibility: opencode",
            "metadata:",
            '  forma.kind: "creator"',
            '  forma.target: "opencode"',
        ]
    )
    if marker not in text:
        raise ValueError("creator SKILL.md is missing YAML frontmatter")
    return text.replace(marker, f"{metadata}\n---\n\n", 1)


def _target_section(target_agent: str) -> str:
    label = _target_label(target_agent)
    return "\n".join(
        [
            "## Fixed Agent Target",
            "",
            f"This installed creator is fixed to the {label} target. Before "
            "writing generated plan-first skills, load "
            "`references/agent-target.md` and follow it as a hard output "
            "contract.",
            "",
            "Do not offer another agent format from this installed creator. If "
            "the user needs a different target, they need that target's "
            "`forma-creator` bundle installed instead.",
            "",
        ]
    )


def _write_target_reference(
    source_dir: Path,
    target_dir: Path,
    target_agent: str,
) -> None:
    methodology_dir = _methodology_source(source_dir)
    references_dir = target_dir / "references"
    references_dir.mkdir(parents=True, exist_ok=True)
    (references_dir / "agent-target.md").write_text(
        _target_reference(target_agent, _stage_descriptions(methodology_dir)),
        encoding="utf-8",
    )


def _target_reference(target_agent: str, descriptions: Mapping[str, str]) -> str:
    label = _target_label(target_agent)
    lines = [
        f"# Agent Target: {label}",
        "",
        f"This `forma-creator` bundle is fixed to `{target_agent}`. Its "
        "generated plan-first output must contain exactly five stage skill "
        "directories. Direct bundle defaults use the `forma-*` pattern for:",
        "",
    ]
    for kind in DEFAULT_ENABLED_KINDS:
        stage_name = _creator_skill_name(kind).removeprefix("forma-")
        lines.append(f"- `{stage_name}` - {descriptions[kind]}")
    lines.extend(["", "## Output Contract", ""])
    lines.extend(
        [
            "- Before generating a bundle, load "
            "`references/canonical-plan-first.md` and "
            "`references/profile-authoring-principles.md` and "
            "`references/temporary-injection-generation.md`; preserve the "
            "bundled canonical plan-first semantics and "
            "classify natural-language constraints before writing JSON.",
            "- Convert current-session natural-language injection into a "
            "temporary JSON file and run `python scripts/create.py --artifact "
            "bundle --output <generated-bundle-path> --injection-json "
            "<temporary-injection.json>` for workflow-bundle output; do not "
            "use Layer 3 profiles from this installed creator.",
            "- Copy fixed generated-skill resources from "
            "`resources/plan-first/methodology/resources/shared/` and any "
            "stage-local resource directory into each generated skill "
            "directory according to `references/canonical-plan-first.md`.",
        ]
    )
    if target_agent == "codex":
        lines.extend(_codex_output_contract())
    elif target_agent == "claude-code":
        lines.extend(_claude_output_contract())
    elif target_agent == "opencode":
        lines.extend(_opencode_output_contract())
    else:
        raise ValueError(f"unsupported adapter target {target_agent!r}")
    return "\n".join(lines) + "\n"


def _stage_descriptions(methodology_dir: Path) -> Mapping[str, str]:
    return {
        kind: source.description
        for kind, source in load_stage_sources(methodology_dir).items()
    }


def _interactive_constraint_contract() -> List[str]:
    return [
        "",
        "## Interactive Constraint Handling",
        "",
        "- The user may provide one-off special constraints for the generated "
        "five-skill bundle during this interaction.",
        "- Before writing the temporary JSON, show the default installable skill "
        "names: direct skill bundles use the `forma-*` pattern for "
        "`shape -> plan`, `gauge -> ground`, `seal -> lock`, "
        "`pour -> execute`, and `flow -> showhand`.",
        "- Ask whether the user wants to rename any final installable skill "
        "names. If yes, encode exact kebab-case names under `rename.stages`; "
        "if no, omit `rename` and use the defaults.",
        "- Encode those constraints in a temporary injection JSON when they are "
        "compatible with the plan-first methodology and this target contract.",
        "- Classify every natural-language constraint before writing JSON: "
        "`constraints.default` is only for minimal always-on bottom lines; "
        "planning rules go under `shape` / `gauge` / `seal`; daily execution "
        "rules go under `pour` / `flow`; broad docs, generated-baseline, "
        "migration, governance, or cross-layer rules belong in "
        "`conditional_overlays`.",
        "- Treat issue tracker readers, document exporters, private source "
        "loaders, and similar source-context helper scripts as optional source "
        "adapters. Inject their stage-specific constraints and resources only "
        "when explicitly requested; do not treat them as base capability or "
        "place them in `constraints.default`.",
        "- Output the temporary injection file path plus a short classification "
        "table with user constraint, injection target, rationale, durability, "
        "and whether it should later become a tracked Layer 3 profile.",
        "- Do not copy user docs verbatim, do not put governance/root-doc "
        "reading requirements in `constraints.default`, and do not make "
        "routine `pour` / `flow` read broad docs, all runs, generated "
        "baselines, or full profile stacks by default.",
        "- Do not put `profile`, `includes`, tracked profile ids, or stage "
        "`name` / `directory` overrides in that temporary injection JSON. "
        "Final installable names belong only under `rename.stages`.",
        "- Run `python scripts/create.py --artifact bundle --output "
        "<generated-bundle-path> --injection-json <temporary-injection.json>` "
        "before handing off or reporting success.",
        "- Do not install generated outputs from this creator. Report the "
        "output path and install hint only.",
        "- Do not represent one-off constraints as tracked source. If the user "
        "wants durable tracking, help them promote the constraints into a "
        "Layer 3 profile in the owning repository.",
    ]


def _codex_output_contract() -> List[str]:
    lines = [
        "- Generate a Codex-ready direct skill bundle root containing the five "
        "default `forma-*` stage directories for `plan`, `ground`, `lock`, "
        "`execute`, and `showhand`, or the exact `rename.stages` names "
        "confirmed by the user.",
        "- If the user asks for Codex plugin output, run `python "
        "scripts/create.py --artifact plugin --output <generated-plugin-path> "
        "--injection-json <temporary-injection.json>`.",
        "- Codex plugin output must contain `.codex-plugin/plugin.json`, "
        "root `.forma-manifest.json`, and `skills/<skill-name>/` child skill "
        "directories; it must not emit sibling `skill-bundles/` output.",
        "- Keep temporary injection JSON stage keys as `shape`, `gauge`, "
        "`seal`, `pour`, and `flow`; do not expose those bare stage keys as "
        "installable skill directory names.",
        "- Do not use generated output names such as plugin-local `plan` or "
        "direct skill `forma-*` names as temporary injection JSON keys.",
        "- Every generated skill directory must include `SKILL.md` with "
        "frontmatter containing only `name` and `description`.",
        "- Every generated skill directory must include `agents/openai.yaml` "
        "with `interface.display_name`, `interface.short_description`, "
        "and `interface.default_prompt`.",
        "- Keep bundled references inside each generated skill's own "
        "`references/` directory.",
        "- Do not emit Claude Code-only metadata from this Codex creator.",
        "- `scripts/create.py` runs the verifier before reporting success.",
    ]
    lines.extend(_interactive_constraint_contract())
    return lines


def _claude_output_contract() -> List[str]:
    lines = [
        "- Generate a Claude Code-ready direct skill bundle root containing "
        "the five default `forma-*` stage directories for `plan`, `ground`, "
        "`lock`, `execute`, and `showhand`, or the exact `rename.stages` "
        "names confirmed by the user.",
        "- If the user asks for Claude Code plugin output, run `python "
        "scripts/create.py --artifact plugin --output <generated-plugin-path> "
        "--injection-json <temporary-injection.json>`.",
        "- Claude Code plugin output must contain `.claude-plugin/plugin.json`, "
        "root `.forma-manifest.json`, and `skills/<skill-name>/` child skill "
        "directories; it must not emit sibling `skill-bundles/` output.",
        "- For plugin output, strip the exact plugin-name prefix from generated "
        "skill names when present. For plugin `forma`, generated direct skill "
        "names using the `forma-*` pattern become plugin-local `plan`, "
        "`ground`, `lock`, `execute`, and `showhand` stages.",
        "- Keep temporary injection JSON stage keys as `shape`, `gauge`, "
        "`seal`, `pour`, and `flow`; do not expose those bare stage keys as "
        "installable skill directory names.",
        "- Do not use generated output names such as plugin-local `plan` or "
        "direct skill `forma-*` names as temporary injection JSON keys.",
        "- Every generated skill directory must include `SKILL.md` with "
        "frontmatter containing only `name` and `description`.",
        "- Keep bundled references inside each generated skill's own "
        "`references/` directory.",
        "- Do not emit Codex `agents/openai.yaml` files from this Claude Code "
        "creator.",
        "- `scripts/create.py` runs the verifier before reporting success.",
    ]
    lines.extend(_interactive_constraint_contract())
    return lines


def _opencode_output_contract() -> List[str]:
    lines = [
        "- Generate an OpenCode-native direct skill bundle root containing "
        "the five default `forma-*` stage directories for `plan`, `ground`, "
        "`lock`, `execute`, and `showhand`, or the exact `rename.stages` "
        "names confirmed by the user.",
        "- Do not generate plugin output for OpenCode. OpenCode runtime plugins "
        "are `.opencode/plugins/*.js|ts`, not Forma skill workflow bundles.",
        "- Keep temporary injection JSON stage keys as `shape`, `gauge`, "
        "`seal`, `pour`, and `flow`; do not expose those bare stage keys as "
        "installable skill directory names.",
        "- Do not use generated output names such as plugin-local `plan` or "
        "direct skill `forma-*` names as temporary injection JSON keys.",
        "- Every generated skill directory must include `SKILL.md` with "
        "frontmatter containing `name`, `description`, `compatibility: "
        "opencode`, and string-to-string `metadata`.",
        "- Every generated skill directory's frontmatter `name` must match its "
        "directory name, use lowercase alphanumeric hyphen-separated form, and "
        "have a 1-1024 character `description`.",
        "- Keep bundled references inside each generated skill's own "
        "`references/` directory.",
        "- Do not emit Codex `agents/openai.yaml` files, `.codex-plugin`, or "
        "`.claude-plugin` metadata from this OpenCode creator.",
        "- `scripts/create.py` runs the verifier before reporting success.",
    ]
    lines.extend(_interactive_constraint_contract())
    return lines


def _target_label(target_agent: str) -> str:
    if target_agent == "codex":
        return "Codex"
    if target_agent == "claude-code":
        return "Claude Code"
    if target_agent == "opencode":
        return "OpenCode"
    raise ValueError(f"unsupported adapter target {target_agent!r}")


def _creator_skill_name(kind: str) -> str:
    return CREATOR_SKILL_NAMES[kind]


def _copy_entry(src: Path, dst: Path) -> None:
    if src.is_dir():
        shutil.copytree(
            src,
            dst,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    else:
        shutil.copy2(src, dst)


def _copy_methodology_resources(source_dir: Path, target_dir: Path) -> None:
    methodology_source = _methodology_source(source_dir)
    methodology_target = target_dir / "resources" / "plan-first" / "methodology"
    methodology_target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        methodology_source,
        methodology_target,
        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
    )
    _make_shell_scripts_executable(methodology_target)


def _methodology_source(source_dir: Path) -> Path:
    return source_dir.parent / "methodology"


def _make_shell_scripts_executable(root: Path) -> None:
    for script in root.glob("resources/*/scripts/*.sh"):
        script.chmod(script.stat().st_mode | 0o111)
