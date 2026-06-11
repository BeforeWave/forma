"""Candidate profile adoption from same-origin workflow artifacts."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

from forma.adapters import build_creator
from forma.creator import build_bundle
from forma.creator.composer import KINDS
from forma.creator.profiles import STAGE_KEYS
from forma.origin import (
    BASE_ORIGIN_SCHEMA,
    NORMALIZATION_ID,
    normalized_payload_digest,
    normalized_payload_file_hashes,
)
from forma.plugins import build_plugin
from forma_verifier import verify
from forma_verifier.rules import parse_frontmatter


ADOPTION_REPORT_SCHEMA = "forma.profile-adoption.v1"
ARTIFACT_BUNDLE = "skill-bundle"
ARTIFACT_PLUGIN = "codex-plugin"
ARTIFACT_CLAUDE_CODE_PLUGIN = "claude-code-plugin"
PLUGIN_ARTIFACTS = {ARTIFACT_PLUGIN, ARTIFACT_CLAUDE_CODE_PLUGIN}
PROFILE_FILE_NAME = "profile.yaml"
REPORT_FILE_NAME = "adoption-report.json"

VALIDATION_PREFIX = (
    "Apply workflow validation gate when it is relevant to the current task: `"
)
VALIDATION_SUFFIX = "`"
DECISION_PREFIX = "Settle workflow decision-gate dimension before proposal-ready: "


@dataclass(frozen=True)
class AdoptionResult:
    profile_file: Path
    report_file: Path
    report: Mapping[str, object]


@dataclass(frozen=True)
class ArtifactInfo:
    root: Path
    workflow_root: Path
    manifest: Mapping[str, Any]
    target: str
    artifact_kind: str
    plugin_id: str | None
    plugin_description: str | None


def adopt_profile(
    artifact_path: Path,
    output_dir: Path,
    profile_id: str | None = None,
    replace: bool = False,
) -> AdoptionResult:
    """Adopt a same-origin workflow artifact into a candidate profile package."""
    info = _load_artifact_info(artifact_path)
    _assert_adoptable_artifact(info)
    base_origin = _assert_base_origin(info)
    with tempfile.TemporaryDirectory(prefix="forma-adopt-") as temp_root_text:
        temp_root = Path(temp_root_text)
        baseline = _generate_creator_baseline(
            temp_root / "baseline",
            info.target,
            info.artifact_kind,
        )
        expected_digest = base_origin["base_output_digest"]
        actual_base_digest = normalized_payload_digest(baseline)
        if actual_base_digest != expected_digest:
            raise ValueError(
                "base_origin digest does not match the current Forma creator release"
            )

        profile_root = temp_root / "profile"
        selected_profile_id = profile_id or _default_profile_id(info)
        profile_file = _write_candidate_profile(
            info=info,
            baseline=baseline,
            profile_root=profile_root,
            profile_id=selected_profile_id,
        )
        regenerated = temp_root / "regenerated"
        if info.artifact_kind in PLUGIN_ARTIFACTS:
            build_plugin(profile_file, regenerated, info.target)
        else:
            build_bundle(profile_file, regenerated, info.target)
        _assert_exact_payload_match(info.root, regenerated)

        report = _adoption_report(
            info=info,
            profile_id=selected_profile_id,
            base_origin=base_origin,
            profile_file=PROFILE_FILE_NAME,
        )
        _publish_profile_package(profile_root, output_dir, replace)
        report_file = output_dir / REPORT_FILE_NAME
        report_file.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    return AdoptionResult(
        profile_file=output_dir / PROFILE_FILE_NAME,
        report_file=output_dir / REPORT_FILE_NAME,
        report=report,
    )


def _load_artifact_info(artifact_path: Path) -> ArtifactInfo:
    root = artifact_path.resolve()
    manifest = _load_manifest(root)
    if not manifest:
        raise ValueError("artifact is missing .forma-manifest.json")
    target = _required_string(manifest, "target", "manifest.target")
    if target not in {"codex", "claude-code", "opencode"}:
        raise ValueError(f"unsupported artifact target: {target}")
    if (root / ".codex-plugin" / "plugin.json").is_file():
        if target != "codex":
            raise ValueError("Codex plugin adoption requires target codex")
        plugin = _load_json(root / ".codex-plugin" / "plugin.json")
        plugin_id = _required_string(plugin, "id", "plugin.id")
        plugin_description = _optional_string(plugin, "description")
        return ArtifactInfo(
            root=root,
            workflow_root=root / "skills",
            manifest=manifest,
            target=target,
            artifact_kind=ARTIFACT_PLUGIN,
            plugin_id=plugin_id,
            plugin_description=plugin_description,
        )
    if (root / ".claude-plugin" / "plugin.json").is_file():
        if target != "claude-code":
            raise ValueError("Claude Code plugin adoption requires target claude-code")
        plugin = _load_json(root / ".claude-plugin" / "plugin.json")
        plugin_id = _required_string(plugin, "name", "plugin.name")
        plugin_description = _optional_string(plugin, "description")
        return ArtifactInfo(
            root=root,
            workflow_root=root / "skills",
            manifest=manifest,
            target=target,
            artifact_kind=ARTIFACT_CLAUDE_CODE_PLUGIN,
            plugin_id=plugin_id,
            plugin_description=plugin_description,
        )
    return ArtifactInfo(
        root=root,
        workflow_root=root,
        manifest=manifest,
        target=target,
        artifact_kind=ARTIFACT_BUNDLE,
        plugin_id=None,
        plugin_description=None,
    )


def _load_manifest(root: Path) -> Mapping[str, Any]:
    return _load_json(root / ".forma-manifest.json")


def _load_json(path: Path) -> Mapping[str, Any]:
    if not path.is_file():
        return {}
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return raw


def _assert_adoptable_artifact(info: ArtifactInfo) -> None:
    report = verify(info.root)
    if not report.passed:
        raise ValueError(report.format_human())


def _assert_base_origin(info: ArtifactInfo) -> Mapping[str, str]:
    raw = info.manifest.get("base_origin")
    if not isinstance(raw, Mapping):
        raise ValueError("artifact manifest is missing base_origin")
    expected = {
        "schema": BASE_ORIGIN_SCHEMA,
        "target": info.target,
        "artifact_kind": info.artifact_kind,
        "normalization_id": NORMALIZATION_ID,
    }
    for key, value in expected.items():
        if raw.get(key) != value:
            raise ValueError(f"base_origin.{key} does not match this artifact")
    digest = raw.get("base_output_digest")
    if not isinstance(digest, str) or len(digest) != 64:
        raise ValueError("base_origin.base_output_digest must be a sha256 digest")
    return {key: str(value) for key, value in raw.items()}


def _generate_creator_baseline(
    output_dir: Path,
    target: str,
    artifact_kind: str,
) -> Path:
    with tempfile.TemporaryDirectory(prefix="forma-creator-") as creator_root_text:
        creator = build_creator(None, Path(creator_root_text), target)
        args = [
            sys.executable,
            str(creator / "scripts" / "create.py"),
            "--output",
            str(output_dir),
        ]
        if artifact_kind in PLUGIN_ARTIFACTS:
            args.extend(["--artifact", "plugin"])
        result = subprocess.run(
            args,
            text=True,
            capture_output=True,
            check=False,
        )
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or result.stdout.strip())
    return output_dir


def _write_candidate_profile(
    info: ArtifactInfo,
    baseline: Path,
    profile_root: Path,
    profile_id: str,
) -> Path:
    profile_root.mkdir(parents=True, exist_ok=True)
    bundle: dict[str, Any] = {
        "name": info.plugin_id
        or _manifest_profile_string(info, "bundle_name")
        or profile_id
    }
    if info.plugin_description:
        bundle["description"] = info.plugin_description
    profile: dict[str, Any] = {
        "profile": {
            "id": profile_id,
            "description": "Adopted from a same-origin Forma workflow artifact.",
        },
        "bundle": bundle,
    }
    org_name = _manifest_profile_string(info, "org_name")
    if org_name:
        profile["org"] = {"name": org_name}
    profile["stages"] = {}
    profile["skills"] = {}

    artifact_emitted = _emitted_skills(info.manifest)
    baseline_manifest = _load_manifest(baseline)
    baseline_emitted = _emitted_skills(baseline_manifest)
    resource_specs: dict[str, dict[str, list[dict[str, object]]]] = {}
    conditional_resource_dests = _conditional_resource_dests(info.manifest)
    _apply_conditional_overlays(
        profile,
        info,
        profile_root,
        conditional_resource_dests,
    )
    constraints: dict[str, list[str]] = {}
    validation_commands: dict[str, list[str]] = {}
    decision_gate_extras: list[str] = []

    for kind in KINDS:
        if kind not in artifact_emitted:
            profile["stages"][kind] = {"enabled": False}
            continue
        if kind not in baseline_emitted:
            raise ValueError(f"baseline manifest is missing emitted_skills.{kind}")
        artifact_skill_dir = info.workflow_root / artifact_emitted[kind]["directory"]
        baseline_skill_dir = _baseline_workflow_root(baseline, info.artifact_kind) / baseline_emitted[kind]["directory"]
        stage_config, skill_description = _extract_stage_config(
            kind,
            artifact_skill_dir,
            info.target,
        )
        if stage_config.get("short_description") == skill_description:
            stage_config.pop("short_description")
        profile["stages"][kind] = stage_config
        profile["skills"][kind] = {"description": skill_description}
        _extract_requirement_delta(
            kind=kind,
            artifact_skill_dir=artifact_skill_dir,
            baseline_skill_dir=baseline_skill_dir,
            constraints=constraints,
            validation_commands=validation_commands,
            decision_gate_extras=decision_gate_extras,
            conditional_manifest=info.manifest.get("conditional_overlays"),
        )
        _extract_resource_delta(
            kind=kind,
            artifact_skill_dir=artifact_skill_dir,
            baseline_skill_dir=baseline_skill_dir,
            profile_root=profile_root,
            resource_specs=resource_specs,
            conditional_resource_dests=conditional_resource_dests,
        )

    if constraints:
        profile["constraints"] = constraints
    if validation_commands:
        profile["validation_commands"] = validation_commands
    if decision_gate_extras:
        profile["decision_gate_extras"] = decision_gate_extras
    if resource_specs:
        profile["resources"] = resource_specs

    profile_file = profile_root / PROFILE_FILE_NAME
    profile_file.write_text(
        yaml.safe_dump(profile, sort_keys=False, allow_unicode=False),
        encoding="utf-8",
    )
    return profile_file


def _baseline_workflow_root(baseline: Path, artifact_kind: str) -> Path:
    if artifact_kind in PLUGIN_ARTIFACTS:
        return baseline / "skills"
    return baseline


def _emitted_skills(manifest: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    raw = manifest.get("emitted_skills")
    if not isinstance(raw, Mapping):
        raise ValueError("manifest.emitted_skills is required")
    result: dict[str, dict[str, str]] = {}
    for kind, item in raw.items():
        if not isinstance(kind, str) or kind not in KINDS:
            raise ValueError(f"manifest.emitted_skills has unknown stage: {kind}")
        if not isinstance(item, Mapping):
            raise ValueError(f"manifest.emitted_skills.{kind} is required")
        name = _required_string(item, "name", f"manifest.emitted_skills.{kind}.name")
        directory = _required_string(
            item,
            "directory",
            f"manifest.emitted_skills.{kind}.directory",
        )
        result[kind] = {"name": name, "directory": directory}
    if not result:
        raise ValueError("manifest.emitted_skills must not be empty")
    return result


def _extract_stage_config(
    kind: str,
    skill_dir: Path,
    target: str,
) -> tuple[dict[str, str], str]:
    skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(skill_text)
    name = _required_string(frontmatter, "name", f"{kind} frontmatter.name")
    trigger_description = _required_string(
        frontmatter,
        "description",
        f"{kind} frontmatter.description",
    )
    body_description = _body_intro_description(body, trigger_description)
    display_name = _first_h1(body) or name.replace("-", " ").title()
    stage: dict[str, str] = {
        "name": name,
        "directory": skill_dir.name,
        "display_name": display_name,
    }
    if target == "codex":
        interface = _load_openai_interface(skill_dir / "agents" / "openai.yaml")
        if interface.get("display_name") != display_name:
            raise ValueError(
                f"{kind} display_name differs between SKILL.md and agents/openai.yaml"
            )
        openai_short_description = _required_string(
            interface,
            "short_description",
            f"{kind} agents.openai.short_description",
        )
        if openai_short_description != trigger_description:
            raise ValueError(
                f"{kind} short_description differs between SKILL.md and agents/openai.yaml"
            )
        stage["short_description"] = openai_short_description
        stage["default_prompt"] = _required_string(
            interface,
            "default_prompt",
            f"{kind} agents.openai.default_prompt",
        )
    elif trigger_description != body_description:
        stage["short_description"] = trigger_description
    return stage, body_description


def _load_openai_interface(path: Path) -> Mapping[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping) or not isinstance(raw.get("interface"), Mapping):
        raise ValueError(f"{path} must contain interface metadata")
    return raw["interface"]


def _first_h1(body: str) -> str | None:
    for line in body.splitlines():
        if line.startswith("# ") and line[2:].strip():
            return line[2:].strip()
    return None


def _body_intro_description(body: str, fallback: str) -> str:
    lines = body.splitlines()
    start = 0
    for index, line in enumerate(lines):
        if line.startswith("# ") and line[2:].strip():
            start = index + 1
            break
    while start < len(lines) and not lines[start].strip():
        start += 1
    description_lines: list[str] = []
    for line in lines[start:]:
        if line.startswith("## "):
            break
        if not line.strip():
            if description_lines:
                break
            continue
        description_lines.append(line.strip())
    if not description_lines:
        return fallback
    return "\n".join(description_lines)


def _extract_requirement_delta(
    kind: str,
    artifact_skill_dir: Path,
    baseline_skill_dir: Path,
    constraints: dict[str, list[str]],
    validation_commands: dict[str, list[str]],
    decision_gate_extras: list[str],
    conditional_manifest: object,
) -> None:
    artifact_requirements = _requirements(artifact_skill_dir / "SKILL.md")
    baseline_requirements = _requirements(baseline_skill_dir / "SKILL.md")
    extras = _list_delta(artifact_requirements, baseline_requirements)
    missing = _list_delta(baseline_requirements, artifact_requirements)
    if missing:
        raise ValueError(f"{kind} removes baseline workflow requirements")
    decision_name = _conditional_decision_name(conditional_manifest)
    for item in extras:
        if decision_name and f"`{decision_name}`" in item:
            continue
        if item.startswith(VALIDATION_PREFIX) and item.endswith(VALIDATION_SUFFIX):
            command = item[len(VALIDATION_PREFIX) : -len(VALIDATION_SUFFIX)]
            validation_commands.setdefault(kind, []).append(command)
        elif kind == "shape" and item.startswith(DECISION_PREFIX):
            decision_gate_extras.append(item[len(DECISION_PREFIX) :])
        else:
            constraints.setdefault(kind, []).append(item)


def _requirements(skill_file: Path) -> list[str]:
    _frontmatter, body = parse_frontmatter(skill_file.read_text(encoding="utf-8"))
    return [
        line[2:].strip()
        for line in _markdown_section(body, "Requirements")
        if line.startswith("- ") and line[2:].strip()
    ]


def _markdown_section(body: str, heading: str) -> list[str]:
    lines = body.splitlines()
    section: list[str] = []
    in_section = False
    marker = f"## {heading}"
    for line in lines:
        if line == marker:
            in_section = True
            continue
        if in_section and line.startswith("## "):
            break
        if in_section:
            section.append(line)
    return section


def _list_delta(left: Sequence[str], right: Sequence[str]) -> list[str]:
    remaining = list(right)
    result: list[str] = []
    for item in left:
        if item in remaining:
            remaining.remove(item)
        else:
            result.append(item)
    return result


def _extract_resource_delta(
    kind: str,
    artifact_skill_dir: Path,
    baseline_skill_dir: Path,
    profile_root: Path,
    resource_specs: dict[str, dict[str, list[dict[str, object]]]],
    conditional_resource_dests: set[tuple[str, str]],
) -> None:
    artifact_hashes = _skill_payload_hashes(artifact_skill_dir)
    baseline_hashes = _skill_payload_hashes(baseline_skill_dir)
    for rel in baseline_hashes:
        if rel not in artifact_hashes and not _target_metadata_path(rel):
            raise ValueError(f"{kind} removes baseline runtime file: {rel}")
    for rel in _ordered_resource_paths(artifact_skill_dir, artifact_hashes):
        digest = artifact_hashes[rel]
        if _target_metadata_path(rel):
            continue
        if baseline_hashes.get(rel) == digest:
            continue
        if (kind, rel) in conditional_resource_dests:
            continue
        spec = _copy_resource(
            profile_root=profile_root,
            kind=kind,
            source=artifact_skill_dir / rel,
            dest=rel,
        )
        bucket = _resource_bucket(rel)
        resource_specs.setdefault(kind, {}).setdefault(bucket, []).append(spec)


def _skill_payload_hashes(skill_dir: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(skill_dir.rglob("*")):
        if path.is_file():
            rel = path.relative_to(skill_dir).as_posix()
            result[rel] = normalized_payload_file_hashes(skill_dir).get(rel, "")
    return result


def _ordered_resource_paths(
    skill_dir: Path,
    hashes: Mapping[str, str],
) -> list[str]:
    ordered: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if skill_file.is_file():
        text = skill_file.read_text(encoding="utf-8")
        references = []
        for rel in hashes:
            marker = f"`{rel}`"
            index = text.find(marker)
            if rel.startswith("references/") and index >= 0:
                references.append((index, rel))
        ordered.extend(rel for _index, rel in sorted(references))
    ordered.extend(
        rel
        for rel in hashes
        if rel.startswith("scripts/") and rel not in ordered
    )
    ordered.extend(
        rel
        for rel in hashes
        if not rel.startswith("references/")
        and not rel.startswith("scripts/")
        and rel not in ordered
    )
    ordered.extend(rel for rel in hashes if rel not in ordered)
    return ordered


def _target_metadata_path(rel: str) -> bool:
    return rel == "SKILL.md" or rel.startswith("agents/")


def _resource_bucket(dest: str) -> str:
    if dest.startswith("references/"):
        return "references"
    if dest.startswith("scripts/"):
        return "scripts"
    return "files"


def _resource_profile_dest(dest: str) -> str:
    if dest.startswith("references/"):
        return dest[len("references/") :]
    if dest.startswith("scripts/"):
        return dest[len("scripts/") :]
    return dest


def _copy_resource(
    profile_root: Path,
    kind: str,
    source: Path,
    dest: str,
) -> dict[str, object]:
    target = profile_root / "resources" / kind / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    rel_source = target.relative_to(profile_root).as_posix()
    spec: dict[str, object] = {
        "source": rel_source,
        "dest": _resource_profile_dest(dest),
        "executable": bool(source.stat().st_mode & 0o111),
    }
    return spec


def _apply_conditional_overlays(
    profile: dict[str, Any],
    info: ArtifactInfo,
    profile_root: Path,
    conditional_resource_dests: set[tuple[str, str]],
) -> None:
    raw = info.manifest.get("conditional_overlays")
    if not isinstance(raw, Mapping):
        return
    decision = raw.get("decision")
    routes = raw.get("routes")
    overlays = raw.get("overlays")
    if not isinstance(decision, Mapping) or not isinstance(routes, list) or not isinstance(overlays, Mapping):
        raise ValueError("conditional_overlays manifest is malformed")
    profile_overlays: dict[str, Any] = {}
    artifact_emitted = _emitted_skills(info.manifest)
    for overlay_id, overlay in overlays.items():
        if not isinstance(overlay_id, str) or not isinstance(overlay, Mapping):
            raise ValueError("conditional_overlays overlays must be mappings")
        overlay_profile: dict[str, Any] = {}
        for key in ("description", "constraints", "validation_commands"):
            value = overlay.get(key)
            if value:
                overlay_profile[key] = value
        resource_specs: dict[str, dict[str, list[dict[str, object]]]] = {}
        raw_resources = overlay.get("resources")
        if isinstance(raw_resources, Mapping):
            for kind, dests in raw_resources.items():
                if kind not in STAGE_KEYS or not isinstance(dests, list):
                    raise ValueError("conditional overlay resources are malformed")
                for dest in dests:
                    if not isinstance(dest, str):
                        raise ValueError("conditional overlay resource dest is malformed")
                    source = _conditional_resource_source(
                        info=info,
                        artifact_emitted=artifact_emitted,
                        kind=kind,
                        dest=dest,
                    )
                    if source is None:
                        raise ValueError(
                            f"conditional overlay resource references disabled stage: {kind}"
                        )
                    spec = _copy_resource(
                        profile_root=profile_root,
                        kind=f"conditional/{overlay_id}/{kind}",
                        source=source,
                        dest=dest,
                    )
                    bucket = _resource_bucket(dest)
                    resource_specs.setdefault(kind, {}).setdefault(bucket, []).append(spec)
                    for emitted_kind in _conditional_resource_emitted_kinds(
                        info=info,
                        artifact_emitted=artifact_emitted,
                        kind=kind,
                        dest=dest,
                    ):
                        conditional_resource_dests.add((emitted_kind, dest))
        if resource_specs:
            overlay_profile["resources"] = resource_specs
        profile_overlays[overlay_id] = overlay_profile
    profile["conditional_overlays"] = {
        "decision": decision,
        "routes": _profile_conditional_routes(routes),
        "overlays": profile_overlays,
    }


def _conditional_resource_source(
    info: ArtifactInfo,
    artifact_emitted: Mapping[str, Mapping[str, str]],
    kind: str,
    dest: str,
) -> Path | None:
    if kind == "default":
        for emitted_kind in KINDS:
            source = _conditional_resource_source(
                info=info,
                artifact_emitted=artifact_emitted,
                kind=emitted_kind,
                dest=dest,
            )
            if source is not None:
                return source
        return None
    emitted = artifact_emitted.get(kind)
    if emitted is None:
        return None
    source = info.workflow_root / emitted["directory"] / dest
    if not source.is_file():
        raise ValueError(f"conditional overlay resource is missing: {kind}:{dest}")
    return source


def _conditional_resource_emitted_kinds(
    info: ArtifactInfo,
    artifact_emitted: Mapping[str, Mapping[str, str]],
    kind: str,
    dest: str,
) -> list[str]:
    if kind != "default":
        return [kind] if kind in artifact_emitted else []
    result: list[str] = []
    for emitted_kind, emitted in artifact_emitted.items():
        if (info.workflow_root / emitted["directory"] / dest).is_file():
            result.append(emitted_kind)
    return result


def _profile_conditional_routes(routes: list[object]) -> list[dict[str, object]]:
    profile_routes: list[dict[str, object]] = []
    for index, raw_route in enumerate(routes):
        field = f"conditional_overlays.routes[{index}]"
        if not isinstance(raw_route, Mapping):
            raise ValueError(f"{field} must be a mapping")
        route_id = _required_string(raw_route, "id", f"{field}.id")
        route: dict[str, object] = {"id": route_id}
        description = raw_route.get("description")
        if description is not None:
            if not isinstance(description, str):
                raise ValueError(f"{field}.description must be a string")
            route["description"] = description
        overlays = raw_route.get("overlays", [])
        if not isinstance(overlays, list) or not all(
            isinstance(item, str) and item.strip() for item in overlays
        ):
            raise ValueError(f"{field}.overlays must be a list of strings")
        route["overlays"] = [item.strip() for item in overlays]
        profile_routes.append(route)
    return profile_routes


def _conditional_resource_dests(manifest: Mapping[str, Any]) -> set[tuple[str, str]]:
    result: set[tuple[str, str]] = set()
    raw = manifest.get("conditional_overlays")
    if not isinstance(raw, Mapping):
        return result
    overlays = raw.get("overlays")
    if not isinstance(overlays, Mapping):
        return result
    emitted = _emitted_skills(manifest)
    for overlay in overlays.values():
        if not isinstance(overlay, Mapping):
            continue
        resources = overlay.get("resources")
        if not isinstance(resources, Mapping):
            continue
        for kind, dests in resources.items():
            if kind not in STAGE_KEYS or not isinstance(dests, list):
                continue
            for dest in dests:
                if not isinstance(dest, str):
                    continue
                if kind == "default":
                    for emitted_kind in emitted:
                        result.add((emitted_kind, dest))
                else:
                    result.add((kind, dest))
    return result


def _conditional_decision_name(raw: object) -> str | None:
    if not isinstance(raw, Mapping):
        return None
    decision = raw.get("decision")
    if not isinstance(decision, Mapping):
        return None
    name = decision.get("name")
    if isinstance(name, str):
        return name
    return None


def _assert_exact_payload_match(artifact: Path, regenerated: Path) -> None:
    artifact_digest = normalized_payload_digest(artifact)
    regenerated_digest = normalized_payload_digest(regenerated)
    if artifact_digest == regenerated_digest:
        return
    artifact_hashes = normalized_payload_file_hashes(artifact)
    regenerated_hashes = normalized_payload_file_hashes(regenerated)
    diff = sorted(
        set(artifact_hashes).symmetric_difference(regenerated_hashes)
        | {
            key
            for key in set(artifact_hashes) & set(regenerated_hashes)
            if artifact_hashes[key] != regenerated_hashes[key]
        }
    )
    first = diff[0] if diff else "<unknown>"
    raise ValueError(f"residual diff cannot be represented by profile schema: {first}")


def _publish_profile_package(profile_root: Path, output_dir: Path, replace: bool) -> None:
    output_dir = output_dir.resolve()
    if output_dir.exists():
        if any(output_dir.iterdir()):
            if not replace:
                raise ValueError("output directory is not empty; use --replace")
            shutil.rmtree(output_dir)
        else:
            output_dir.rmdir()
    shutil.copytree(profile_root, output_dir)


def _adoption_report(
    info: ArtifactInfo,
    profile_id: str,
    base_origin: Mapping[str, str],
    profile_file: str,
) -> dict[str, object]:
    digest = normalized_payload_digest(info.root)
    return {
        "schema": ADOPTION_REPORT_SCHEMA,
        "status": "adopted",
        "profile_state": "candidate",
        "review_required": True,
        "promotion_required": True,
        "artifact": str(info.root),
        "artifact_kind": info.artifact_kind,
        "target": info.target,
        "profile_id": profile_id,
        "profile_file": profile_file,
        "base_origin": dict(base_origin),
        "normalized_payload_digest": digest,
        "regenerated_payload_digest": digest,
    }


def _default_profile_id(info: ArtifactInfo) -> str:
    manifest_profile_id = _manifest_profile_string(info, "top_level_id")
    if manifest_profile_id:
        return manifest_profile_id
    if info.plugin_id:
        return info.plugin_id
    name = info.root.name.strip().lower()
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in name)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "adopted-forma-profile"


def _manifest_profile_string(info: ArtifactInfo, key: str) -> str | None:
    profile = info.manifest.get("profile")
    if not isinstance(profile, Mapping):
        return None
    value = profile.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _required_string(mapping: Mapping[str, Any], key: str, field: str) -> str:
    value = mapping.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _optional_string(mapping: Mapping[str, Any], key: str) -> str | None:
    value = mapping.get(key)
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None
