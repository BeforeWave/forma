"""Composable profile loading and merge rules for generated skill bundles.

Profiles are durable source artifacts. Agents may help draft or refactor them,
but Forma must not treat ad hoc Layer 1 constraints as tracked profile source
unless the user explicitly promotes and reviews the profile file.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Mapping, Sequence, Tuple

import yaml


DEFAULT_ENABLED_KINDS = ("shape", "gauge", "seal", "pour", "flow")
OPTIONAL_KINDS = ("hone", "mend")
KINDS = (*DEFAULT_ENABLED_KINDS, *OPTIONAL_KINDS)
STAGE_KEYS = ("default", *KINDS)

ALLOWED_TOP_LEVEL_KEYS = {
    "profile",
    "includes",
    "bundle",
    "plugin",
    "org",
    "stages",
    "resources",
    "skills",
    "terminology",
    "validation_commands",
    "decision_gate_extras",
    "constraints",
    "workflow_adds",
    "output_adds",
    "conditional_overlays",
}
ALLOWED_PROFILE_KEYS = {"id", "description"}
ALLOWED_BUNDLE_KEYS = {"name", "description"}
ALLOWED_PLUGIN_KEYS = {"display_name"}
ALLOWED_ORG_KEYS = {"name"}
ALLOWED_SKILL_KEYS = set(KINDS)
ALLOWED_SKILL_FIELD_KEYS = {"description"}
ALLOWED_STAGE_KEYS = set(STAGE_KEYS)
ALLOWED_STAGE_CONFIG_KEYS = {
    "enabled",
    "name",
    "directory",
    "display_name",
    "short_description",
    "default_prompt",
}
ALLOWED_RESOURCE_BUCKET_KEYS = {"references", "scripts", "files"}
ALLOWED_RESOURCE_ITEM_KEYS = {"source", "dest", "executable"}
ALLOWED_CONDITIONAL_KEYS = {"decision", "routes", "overlays"}
ALLOWED_CONDITIONAL_DECISION_KEYS = {
    "name",
    "must_record_in_plan",
    "missing_during_execution",
}
ALLOWED_CONDITIONAL_ROUTE_KEYS = {"id", "description", "overlays"}
ALLOWED_CONDITIONAL_OVERLAY_KEYS = {
    "description",
    "constraints",
    "resources",
    "validation_commands",
}


@dataclass(frozen=True)
class StageConfig:
    enabled: bool
    name: str
    directory: str
    display_name: str
    short_description: str
    default_prompt: str


@dataclass(frozen=True)
class ResourceSpec:
    source: Path
    dest: str
    executable: bool
    content: str | None = None


@dataclass(frozen=True)
class ConditionalDecision:
    name: str
    must_record_in_plan: bool
    missing_during_execution: str


@dataclass(frozen=True)
class ConditionalRoute:
    id: str
    description: str
    overlays: Tuple[str, ...]


@dataclass(frozen=True)
class ConditionalOverlay:
    id: str
    description: str
    constraints: Mapping[str, Tuple[str, ...]]
    resources: Mapping[str, Tuple[ResourceSpec, ...]]
    validation_commands: Mapping[str, Tuple[str, ...]]


@dataclass(frozen=True)
class ConditionalOverlays:
    decision: ConditionalDecision
    routes: Tuple[ConditionalRoute, ...]
    overlays: Mapping[str, ConditionalOverlay]


@dataclass(frozen=True)
class ProfileConfig:
    profile_file: Path
    profile_root: Path
    profile_id: str
    top_level_path: str
    resolved_order: Tuple[str, ...]
    resolved_paths: Tuple[Path, ...]
    bundle_name: str
    bundle_description: str
    plugin_display_name: str
    org_name: str
    stages: Mapping[str, StageConfig]
    resources: Mapping[str, Tuple[ResourceSpec, ...]]
    terminology: Mapping[str, str]
    validation_commands: Mapping[str, List[str]]
    decision_gate_extras: List[str]
    constraints: Mapping[str, List[str]]
    workflow_adds: Mapping[str, List[str]]
    output_adds: Mapping[str, List[str]]
    skill_descriptions: Mapping[str, str]
    conditional_overlays: ConditionalOverlays | None


def load_profile(profile_file: Path) -> ProfileConfig:
    """Load a top-level profile and recursively merge its includes."""
    profile_file = profile_file.resolve()
    if not profile_file.is_file():
        raise ValueError(f"missing profile file: {profile_file}")
    profile_root = profile_file.parent
    id_index = _build_profile_id_index(profile_root)
    records = _resolve_profiles(
        profile_file=profile_file,
        profile_root=profile_root,
        id_index=id_index,
        seen=set(),
        stack=[],
    )
    if not records:
        raise ValueError(f"profile did not resolve any files: {profile_file}")

    merged = _empty_merged()
    resolved_order: List[str] = []
    resolved_paths: List[Path] = []
    for path, raw in records:
        profile_id = _profile_id(raw, path)
        resolved_order.append(profile_id)
        resolved_paths.append(path)
        _merge_profile(merged, raw, path)

    top_raw = records[-1][1]
    top_profile_id = _profile_id(top_raw, profile_file)
    return ProfileConfig(
        profile_file=profile_file,
        profile_root=profile_root,
        profile_id=top_profile_id,
        top_level_path=profile_file.relative_to(profile_root).as_posix(),
        resolved_order=tuple(resolved_order),
        resolved_paths=tuple(resolved_paths),
        bundle_name=merged["bundle"].get("name") or top_profile_id,
        bundle_description=merged["bundle"].get("description") or "",
        plugin_display_name=merged["plugin"].get("display_name") or "",
        org_name=merged["org_name"] or "Local Team",
        stages=_build_stage_configs(merged["stages"]),
        resources=_copy_resources(merged["resources"]),
        terminology=dict(merged["terminology"]),
        validation_commands=_copy_stage_mapping(merged["validation_commands"]),
        decision_gate_extras=list(merged["decision_gate_extras"]),
        constraints=_copy_stage_mapping(merged["constraints"]),
        workflow_adds=_copy_stage_mapping(merged["workflow_adds"]),
        output_adds=_copy_stage_mapping(merged["output_adds"]),
        skill_descriptions=dict(merged["skill_descriptions"]),
        conditional_overlays=_build_conditional_overlays(
            merged["conditional_overlays"],
            profile_file,
        ),
    )


def _resolve_profiles(
    profile_file: Path,
    profile_root: Path,
    id_index: Mapping[str, Path],
    seen: set[Path],
    stack: List[Path],
) -> List[Tuple[Path, Mapping[str, Any]]]:
    profile_file = profile_file.resolve()
    if profile_file in stack:
        cycle = " -> ".join(path.name for path in [*stack, profile_file])
        raise ValueError(f"profile include cycle detected: {cycle}")
    if profile_file in seen:
        return []
    raw = _load_profile_file(profile_file)
    stack.append(profile_file)
    records: List[Tuple[Path, Mapping[str, Any]]] = []
    for include in _load_includes(raw.get("includes", []), profile_file):
        include_file = _resolve_include(include, profile_file.parent, profile_root, id_index)
        records.extend(
            _resolve_profiles(
                profile_file=include_file,
                profile_root=profile_root,
                id_index=id_index,
                seen=seen,
                stack=stack,
            )
        )
    stack.pop()
    seen.add(profile_file)
    records.append((profile_file, raw))
    return records


def _build_profile_id_index(profile_root: Path) -> Dict[str, Path]:
    index: Dict[str, Path] = {}
    for path in sorted(profile_root.rglob("*.yaml")):
        raw = _load_yaml_mapping(path)
        profile = raw.get("profile", {})
        if not isinstance(profile, dict):
            continue
        profile_id = profile.get("id")
        if not isinstance(profile_id, str) or not profile_id.strip():
            continue
        profile_id = profile_id.strip()
        if profile_id in index:
            raise ValueError(f"duplicate profile id {profile_id!r}")
        index[profile_id] = path.resolve()
    return index


def _load_profile_file(path: Path) -> Mapping[str, Any]:
    raw = _load_yaml_mapping(path)
    unknown = set(raw) - ALLOWED_TOP_LEVEL_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_rel(path)} has unknown top-level keys: {keys}")
    _profile_id(raw, path)
    _validate_profile_mapping(raw.get("profile", {}), path)
    _load_includes(raw.get("includes", []), path)
    _load_bundle(raw.get("bundle", {}), path)
    _load_plugin(raw.get("plugin", {}), path)
    _load_org(raw.get("org"), path)
    _load_stages(raw.get("stages", {}), path)
    _load_resources(raw.get("resources", {}), path)
    _load_string_mapping(raw.get("terminology", {}), "terminology", path)
    _load_stage_mapping(raw.get("validation_commands", {}), "validation_commands", path)
    _load_string_list(raw.get("decision_gate_extras", []), "decision_gate_extras", path)
    _load_constraints(raw.get("constraints", {}), path)
    _load_stage_mapping(raw.get("workflow_adds", {}), "workflow_adds", path)
    _load_stage_mapping(raw.get("output_adds", {}), "output_adds", path)
    _load_skills(raw.get("skills", {}), path)
    _load_conditional_overlay_fragment(raw.get("conditional_overlays"), path)
    return raw


def _load_yaml_mapping(path: Path) -> Dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        raise ValueError(f"{_rel(path)} must contain a mapping")
    return raw


def _empty_merged() -> Dict[str, Any]:
    return {
        "bundle": {},
        "plugin": {},
        "org_name": "",
        "stages": {},
        "resources": {},
        "terminology": {},
        "validation_commands": {},
        "decision_gate_extras": [],
        "constraints": {},
        "workflow_adds": {},
        "output_adds": {},
        "skill_descriptions": {},
        "conditional_overlays": {
            "used": False,
            "decision": None,
            "route_order": [],
            "routes": {},
            "overlays": {},
        },
    }


def _merge_profile(merged: Dict[str, Any], raw: Mapping[str, Any], path: Path) -> None:
    bundle = _load_bundle(raw.get("bundle", {}), None)
    for key, value in bundle.items():
        merged["bundle"][key] = value

    plugin = _load_plugin(raw.get("plugin", {}), None)
    for key, value in plugin.items():
        merged["plugin"][key] = value

    org_name = _load_org(raw.get("org"), None)
    if org_name:
        merged["org_name"] = org_name

    for kind, stage in _load_stages(raw.get("stages", {}), path).items():
        bucket = merged["stages"].setdefault(kind, {})
        bucket.update(stage)

    _merge_resources(
        merged["resources"],
        _load_resources(raw.get("resources", {}), path),
    )

    merged["terminology"].update(
        _load_string_mapping(raw.get("terminology", {}), "terminology", None)
    )
    _merge_stage_mapping(
        merged["validation_commands"],
        _load_stage_mapping(raw.get("validation_commands", {}), "validation_commands", None),
    )
    _append_unique(
        merged["decision_gate_extras"],
        _load_string_list(raw.get("decision_gate_extras", []), "decision_gate_extras", None),
    )
    _merge_stage_mapping(
        merged["constraints"],
        _load_constraints(raw.get("constraints", {}), None),
    )
    _merge_stage_mapping(
        merged["workflow_adds"],
        _load_stage_mapping(raw.get("workflow_adds", {}), "workflow_adds", None),
    )
    _merge_stage_mapping(
        merged["output_adds"],
        _load_stage_mapping(raw.get("output_adds", {}), "output_adds", None),
    )
    merged["skill_descriptions"].update(_load_skills(raw.get("skills", {}), None))
    _merge_conditional_overlays(
        merged["conditional_overlays"],
        _load_conditional_overlay_fragment(raw.get("conditional_overlays"), path),
    )


def _resolve_include(
    include: str,
    current_dir: Path,
    profile_root: Path,
    id_index: Mapping[str, Path],
) -> Path:
    candidates: List[Path] = []
    include_path = Path(include)
    if include_path.suffix:
        candidates.append((current_dir / include_path).resolve())
        candidates.append((profile_root / include_path).resolve())
    else:
        if include in id_index:
            candidates.append(id_index[include])
        candidates.append((current_dir / f"{include}.yaml").resolve())
        candidates.append((profile_root / f"{include}.yaml").resolve())
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise ValueError(f"missing included profile {include!r}")


def _profile_id(raw: Mapping[str, Any], path: Path) -> str:
    profile = raw.get("profile")
    if not isinstance(profile, dict):
        raise ValueError(f"{_rel(path)} missing profile mapping")
    profile_id = profile.get("id")
    if not isinstance(profile_id, str) or not profile_id.strip():
        raise ValueError(f"{_rel(path)} profile.id must be a non-empty string")
    return profile_id.strip()


def _validate_profile_mapping(value: Any, path: Path | None) -> None:
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}profile must be a mapping")
    unknown = set(value) - ALLOWED_PROFILE_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}profile has unknown keys: {keys}")
    description = value.get("description")
    if description is not None and (
        not isinstance(description, str) or not description.strip()
    ):
        raise ValueError(f"{_prefix(path)}profile.description must be a non-empty string")


def _load_includes(value: Any, path: Path | None) -> List[str]:
    if value is None:
        return []
    return _load_string_list(value, "includes", path)


def _load_bundle(value: Any, path: Path | None) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}bundle must be a mapping")
    unknown = set(value) - ALLOWED_BUNDLE_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}bundle has unknown keys: {keys}")
    return _string_fields(value, "bundle", path)


def _load_plugin(value: Any, path: Path | None) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}plugin must be a mapping")
    unknown = set(value) - ALLOWED_PLUGIN_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}plugin has unknown keys: {keys}")
    return _string_fields(value, "plugin", path)


def _load_org(value: Any, path: Path | None) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        name = value.strip()
        if not name:
            raise ValueError(f"{_prefix(path)}org must not be empty")
        return name
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}org must be a string or mapping")
    unknown = set(value) - ALLOWED_ORG_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}org has unknown keys: {keys}")
    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(f"{_prefix(path)}org.name must be a non-empty string")
    return name.strip()


def _load_skills(value: Any, path: Path | None) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}skills must be a mapping")
    unknown = set(value) - ALLOWED_SKILL_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}skills has unknown keys: {keys}")
    result: Dict[str, str] = {}
    for kind, item in value.items():
        if not isinstance(item, dict):
            raise ValueError(f"{_prefix(path)}skills.{kind} must be a mapping")
        nested_unknown = set(item) - ALLOWED_SKILL_FIELD_KEYS
        if nested_unknown:
            keys = ", ".join(sorted(nested_unknown))
            raise ValueError(f"{_prefix(path)}skills.{kind} has unknown keys: {keys}")
        description = item.get("description")
        if description is not None:
            if not isinstance(description, str) or not description.strip():
                raise ValueError(
                    f"{_prefix(path)}skills.{kind}.description must be a non-empty string"
                )
            result[kind] = description.strip()
    return result


def _load_stages(value: Any, path: Path | None) -> Dict[str, Dict[str, object]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}stages must be a mapping")
    unknown = set(value) - set(KINDS)
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}stages has unknown keys: {keys}")
    result: Dict[str, Dict[str, object]] = {}
    for kind, item in value.items():
        if not isinstance(item, dict):
            raise ValueError(f"{_prefix(path)}stages.{kind} must be a mapping")
        nested_unknown = set(item) - ALLOWED_STAGE_CONFIG_KEYS
        if nested_unknown:
            keys = ", ".join(sorted(nested_unknown))
            raise ValueError(f"{_prefix(path)}stages.{kind} has unknown keys: {keys}")
        stage: Dict[str, object] = {}
        if "enabled" in item:
            if not isinstance(item["enabled"], bool):
                raise ValueError(f"{_prefix(path)}stages.{kind}.enabled must be boolean")
            stage["enabled"] = item["enabled"]
        for key in (
            "name",
            "directory",
            "display_name",
            "short_description",
            "default_prompt",
        ):
            if key not in item:
                continue
            value_item = item[key]
            if not isinstance(value_item, str) or not value_item.strip():
                raise ValueError(
                    f"{_prefix(path)}stages.{kind}.{key} must be a non-empty string"
                )
            value_text = value_item.strip()
            if key in {"name", "directory"}:
                _validate_kebab_component(value_text, f"stages.{kind}.{key}", path)
            stage[key] = value_text
        result[kind] = stage
    return result


def _load_resources(value: Any, path: Path | None) -> Dict[str, List[ResourceSpec]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}resources must be a mapping")
    unknown = set(value) - ALLOWED_STAGE_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}resources has unknown keys: {keys}")
    result: Dict[str, List[ResourceSpec]] = {}
    for stage, buckets in value.items():
        if not isinstance(buckets, dict):
            raise ValueError(f"{_prefix(path)}resources.{stage} must be a mapping")
        bucket_unknown = set(buckets) - ALLOWED_RESOURCE_BUCKET_KEYS
        if bucket_unknown:
            keys = ", ".join(sorted(bucket_unknown))
            raise ValueError(
                f"{_prefix(path)}resources.{stage} has unknown keys: {keys}"
            )
        specs: List[ResourceSpec] = []
        for bucket_name, items in buckets.items():
            if not isinstance(items, list):
                raise ValueError(
                    f"{_prefix(path)}resources.{stage}.{bucket_name} must be a list"
                )
            for index, item in enumerate(items):
                specs.append(
                    _load_resource_item(
                        item,
                        bucket_name,
                        f"resources.{stage}.{bucket_name}[{index}]",
                        path,
                    )
                )
        result[stage] = specs
    return result


def _load_resource_item(
    value: Any,
    bucket_name: str,
    field_name: str,
    path: Path | None,
) -> ResourceSpec:
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}{field_name} must be a mapping")
    unknown = set(value) - ALLOWED_RESOURCE_ITEM_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}{field_name} has unknown keys: {keys}")
    raw_source = value.get("source")
    if not isinstance(raw_source, str) or not raw_source.strip():
        raise ValueError(f"{_prefix(path)}{field_name}.source must be a non-empty string")
    if path is None:
        raise ValueError(f"{field_name}.source cannot be resolved without a profile file")
    source = (path.parent / raw_source.strip()).resolve()
    if not source.is_file():
        raise ValueError(f"{_prefix(path)}{field_name}.source does not exist: {raw_source}")

    raw_dest = value.get("dest")
    if raw_dest is None:
        dest_text = source.name
    elif isinstance(raw_dest, str) and raw_dest.strip():
        dest_text = raw_dest.strip()
    else:
        raise ValueError(f"{_prefix(path)}{field_name}.dest must be a non-empty string")
    dest = _resource_dest(bucket_name, dest_text, field_name, path)

    raw_executable = value.get("executable")
    if raw_executable is None:
        executable = bucket_name == "scripts"
    elif isinstance(raw_executable, bool):
        executable = raw_executable
    else:
        raise ValueError(f"{_prefix(path)}{field_name}.executable must be boolean")

    return ResourceSpec(source=source, dest=dest, executable=executable)


def _resource_dest(
    bucket_name: str,
    dest_text: str,
    field_name: str,
    path: Path | None,
) -> str:
    _validate_relative_resource_path(dest_text, f"{field_name}.dest", path)
    if bucket_name == "references":
        return f"references/{dest_text}"
    if bucket_name == "scripts":
        return f"scripts/{dest_text}"
    return dest_text


def _load_constraints(value: Any, path: Path | None) -> Dict[str, List[str]]:
    if value is None:
        return {}
    if isinstance(value, list):
        return {"default": _load_string_list(value, "constraints", path)}
    return _load_stage_mapping(value, "constraints", path)


def _load_stage_mapping(value: Any, field_name: str, path: Path | None) -> Dict[str, List[str]]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}{field_name} must be a mapping")
    unknown = set(value) - ALLOWED_STAGE_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}{field_name} has unknown keys: {keys}")
    result: Dict[str, List[str]] = {}
    for key, item in value.items():
        result[key] = _load_string_list(item, f"{field_name}.{key}", path)
    return result


def _load_string_mapping(value: Any, field_name: str, path: Path | None) -> Dict[str, str]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}{field_name} must be a mapping")
    result: Dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError(f"{_prefix(path)}{field_name} keys must be non-empty strings")
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"{_prefix(path)}{field_name}.{key} must be a non-empty string"
            )
        result[key.strip()] = item.strip()
    return result


def _load_string_list(value: Any, field_name: str, path: Path | None) -> List[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{_prefix(path)}{field_name} must be a list")
    result: List[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(
                f"{_prefix(path)}{field_name}[{index}] must be a non-empty string"
            )
        result.append(item.strip())
    return result


def _string_fields(value: Mapping[str, Any], field_name: str, path: Path | None) -> Dict[str, str]:
    result: Dict[str, str] = {}
    for key, item in value.items():
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"{_prefix(path)}{field_name}.{key} must be a non-empty string")
        result[key] = item.strip()
    return result


def _merge_stage_mapping(target: Dict[str, List[str]], source: Mapping[str, Sequence[str]]) -> None:
    for key, values in source.items():
        bucket = target.setdefault(key, [])
        _append_unique(bucket, values)


def _merge_resources(
    target: Dict[str, List[ResourceSpec]],
    source: Mapping[str, Sequence[ResourceSpec]],
) -> None:
    for key, values in source.items():
        bucket = target.setdefault(key, [])
        for value in values:
            for index, existing in enumerate(bucket):
                if existing.dest == value.dest:
                    bucket[index] = value
                    break
            else:
                bucket.append(value)


def _append_unique(target: List[str], values: Sequence[str]) -> None:
    for value in values:
        if value not in target:
            target.append(value)


def _copy_stage_mapping(value: Mapping[str, Sequence[str]]) -> Dict[str, List[str]]:
    return {key: list(items) for key, items in value.items()}


def _copy_resources(
    value: Mapping[str, Sequence[ResourceSpec]],
) -> Dict[str, Tuple[ResourceSpec, ...]]:
    return {key: tuple(items) for key, items in value.items()}


def _load_conditional_overlay_fragment(
    value: Any,
    path: Path | None,
) -> Dict[str, Any] | None:
    if value is None:
        return None
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}conditional_overlays must be a mapping")
    unknown = set(value) - ALLOWED_CONDITIONAL_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(f"{_prefix(path)}conditional_overlays has unknown keys: {keys}")
    fragment: Dict[str, Any] = {
        "decision": None,
        "routes": [],
        "overlays": {},
    }
    if "decision" in value:
        fragment["decision"] = _load_conditional_decision(
            value.get("decision"),
            path,
        )
    if "routes" in value:
        fragment["routes"] = _load_conditional_routes(value.get("routes"), path)
    if "overlays" in value:
        fragment["overlays"] = _load_conditional_overlay_specs(
            value.get("overlays"),
            path,
        )
    return fragment


def _load_conditional_decision(value: Any, path: Path | None) -> ConditionalDecision:
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}conditional_overlays.decision must be a mapping")
    unknown = set(value) - ALLOWED_CONDITIONAL_DECISION_KEYS
    if unknown:
        keys = ", ".join(sorted(unknown))
        raise ValueError(
            f"{_prefix(path)}conditional_overlays.decision has unknown keys: {keys}"
        )
    name = value.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError(
            f"{_prefix(path)}conditional_overlays.decision.name must be a non-empty string"
        )
    must_record = value.get("must_record_in_plan", True)
    if not isinstance(must_record, bool):
        raise ValueError(
            f"{_prefix(path)}conditional_overlays.decision.must_record_in_plan must be boolean"
        )
    if not must_record:
        raise ValueError(
            f"{_prefix(path)}conditional_overlays.decision.must_record_in_plan must be true"
        )
    missing = value.get("missing_during_execution", "stop-for-plan-correction")
    if not isinstance(missing, str) or not missing.strip():
        raise ValueError(
            f"{_prefix(path)}conditional_overlays.decision.missing_during_execution must be a non-empty string"
        )
    if missing.strip() != "stop-for-plan-correction":
        raise ValueError(
            f"{_prefix(path)}conditional_overlays.decision.missing_during_execution must be stop-for-plan-correction"
        )
    return ConditionalDecision(
        name=name.strip(),
        must_record_in_plan=must_record,
        missing_during_execution=missing.strip(),
    )


def _load_conditional_routes(
    value: Any,
    path: Path | None,
) -> List[ConditionalRoute]:
    if not isinstance(value, list) or not value:
        raise ValueError(
            f"{_prefix(path)}conditional_overlays.routes must be a non-empty list"
        )
    routes: List[ConditionalRoute] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        field = f"conditional_overlays.routes[{index}]"
        if not isinstance(item, dict):
            raise ValueError(f"{_prefix(path)}{field} must be a mapping")
        unknown = set(item) - ALLOWED_CONDITIONAL_ROUTE_KEYS
        if unknown:
            keys = ", ".join(sorted(unknown))
            raise ValueError(f"{_prefix(path)}{field} has unknown keys: {keys}")
        route_id = item.get("id")
        if not isinstance(route_id, str) or not route_id.strip():
            raise ValueError(f"{_prefix(path)}{field}.id must be a non-empty string")
        route_id = route_id.strip()
        _validate_kebab_component(route_id, f"{field}.id", path)
        if route_id in seen:
            raise ValueError(
                f"{_prefix(path)}conditional_overlays.routes has duplicate id: {route_id}"
            )
        seen.add(route_id)
        description = item.get("description", "")
        if description is not None and not isinstance(description, str):
            raise ValueError(f"{_prefix(path)}{field}.description must be a string")
        overlay_values = item.get("overlays", [])
        if not isinstance(overlay_values, list):
            raise ValueError(f"{_prefix(path)}{field}.overlays must be a list")
        overlays: List[str] = []
        overlay_seen: set[str] = set()
        for overlay_index, overlay_id in enumerate(overlay_values):
            overlay_field = f"{field}.overlays[{overlay_index}]"
            if not isinstance(overlay_id, str) or not overlay_id.strip():
                raise ValueError(f"{_prefix(path)}{overlay_field} must be a non-empty string")
            overlay_id = overlay_id.strip()
            _validate_kebab_component(overlay_id, overlay_field, path)
            if overlay_id in overlay_seen:
                raise ValueError(f"{_prefix(path)}{field}.overlays has duplicate id: {overlay_id}")
            overlay_seen.add(overlay_id)
            overlays.append(overlay_id)
        routes.append(
            ConditionalRoute(
                id=route_id,
                description=(description or "").strip(),
                overlays=tuple(overlays),
            )
        )
    return routes


def _load_conditional_overlay_specs(
    value: Any,
    path: Path | None,
) -> Dict[str, ConditionalOverlay]:
    if value is None:
        return {}
    if not isinstance(value, dict):
        raise ValueError(f"{_prefix(path)}conditional_overlays.overlays must be a mapping")
    overlays: Dict[str, ConditionalOverlay] = {}
    for overlay_id, item in value.items():
        if not isinstance(overlay_id, str) or not overlay_id.strip():
            raise ValueError(
                f"{_prefix(path)}conditional_overlays.overlays keys must be non-empty"
            )
        overlay_id = overlay_id.strip()
        _validate_kebab_component(overlay_id, f"conditional_overlays.overlays.{overlay_id}", path)
        field = f"conditional_overlays.overlays.{overlay_id}"
        if not isinstance(item, dict):
            raise ValueError(f"{_prefix(path)}{field} must be a mapping")
        unknown = set(item) - ALLOWED_CONDITIONAL_OVERLAY_KEYS
        if unknown:
            keys = ", ".join(sorted(unknown))
            raise ValueError(f"{_prefix(path)}{field} has unknown keys: {keys}")
        description = item.get("description", "")
        if description is not None and not isinstance(description, str):
            raise ValueError(f"{_prefix(path)}{field}.description must be a string")
        overlays[overlay_id] = ConditionalOverlay(
            id=overlay_id,
            description=(description or "").strip(),
            constraints=_tuple_stage_mapping(
                _load_constraints(item.get("constraints", {}), path)
            ),
            resources=_copy_resources(_load_resources(item.get("resources", {}), path)),
            validation_commands=_tuple_stage_mapping(
                _load_stage_mapping(
                    item.get("validation_commands", {}),
                    f"{field}.validation_commands",
                    path,
                )
            ),
        )
    return overlays


def _merge_conditional_overlays(
    target: Dict[str, Any],
    fragment: Mapping[str, Any] | None,
) -> None:
    if fragment is None:
        return
    target["used"] = True
    if fragment.get("decision") is not None:
        target["decision"] = fragment["decision"]
    for route in fragment.get("routes", []):
        route_id = route.id
        if route_id not in target["route_order"]:
            target["route_order"].append(route_id)
        target["routes"][route_id] = route
    for overlay_id, overlay in fragment.get("overlays", {}).items():
        existing = target["overlays"].get(overlay_id)
        if existing is None:
            target["overlays"][overlay_id] = overlay
        else:
            target["overlays"][overlay_id] = _merge_conditional_overlay(
                existing,
                overlay,
            )


def _merge_conditional_overlay(
    existing: ConditionalOverlay,
    incoming: ConditionalOverlay,
) -> ConditionalOverlay:
    constraints = _merge_tuple_stage_mapping(existing.constraints, incoming.constraints)
    resources = _merge_tuple_resources(existing.resources, incoming.resources)
    validation_commands = _merge_tuple_stage_mapping(
        existing.validation_commands,
        incoming.validation_commands,
    )
    return ConditionalOverlay(
        id=existing.id,
        description=incoming.description or existing.description,
        constraints=constraints,
        resources=resources,
        validation_commands=validation_commands,
    )


def _build_conditional_overlays(
    merged: Mapping[str, Any],
    path: Path,
) -> ConditionalOverlays | None:
    if not merged.get("used"):
        return None
    decision = merged.get("decision")
    if not isinstance(decision, ConditionalDecision):
        raise ValueError(f"{_prefix(path)}conditional_overlays.decision is required")
    route_order = merged.get("route_order", [])
    routes_by_id = merged.get("routes", {})
    routes = tuple(routes_by_id[route_id] for route_id in route_order)
    if not routes:
        raise ValueError(f"{_prefix(path)}conditional_overlays.routes is required")
    overlays = dict(merged.get("overlays", {}))
    for route in routes:
        for overlay_id in route.overlays:
            if overlay_id not in overlays:
                raise ValueError(
                    f"{_prefix(path)}conditional_overlays route {route.id!r} "
                    f"references missing overlay {overlay_id!r}"
                )
    return ConditionalOverlays(
        decision=decision,
        routes=routes,
        overlays=overlays,
    )


def _tuple_stage_mapping(
    value: Mapping[str, Sequence[str]],
) -> Dict[str, Tuple[str, ...]]:
    return {stage: tuple(items) for stage, items in value.items()}


def _merge_tuple_stage_mapping(
    existing: Mapping[str, Sequence[str]],
    incoming: Mapping[str, Sequence[str]],
) -> Dict[str, Tuple[str, ...]]:
    result: Dict[str, List[str]] = {
        stage: list(items)
        for stage, items in existing.items()
    }
    for stage, items in incoming.items():
        bucket = result.setdefault(stage, [])
        _append_unique(bucket, list(items))
    return {stage: tuple(items) for stage, items in result.items()}


def _merge_tuple_resources(
    existing: Mapping[str, Sequence[ResourceSpec]],
    incoming: Mapping[str, Sequence[ResourceSpec]],
) -> Dict[str, Tuple[ResourceSpec, ...]]:
    result: Dict[str, List[ResourceSpec]] = {
        stage: list(items)
        for stage, items in existing.items()
    }
    _merge_resources(result, incoming)
    return {stage: tuple(items) for stage, items in result.items()}


def _build_stage_configs(raw: Mapping[str, Mapping[str, object]]) -> Dict[str, StageConfig]:
    stages: Dict[str, StageConfig] = {}
    for kind in KINDS:
        item = dict(raw.get(kind, {}))
        enabled_default = kind in DEFAULT_ENABLED_KINDS
        name = str(item.get("name") or kind)
        directory = str(item.get("directory") or name)
        display_name = str(item.get("display_name") or name.replace("-", " ").title())
        stages[kind] = StageConfig(
            enabled=bool(item.get("enabled", enabled_default)),
            name=name,
            directory=directory,
            display_name=display_name,
            short_description=str(item.get("short_description") or ""),
            default_prompt=str(item.get("default_prompt") or ""),
        )
    return stages


def _validate_kebab_component(value: str, field_name: str, path: Path | None) -> None:
    parts = value.split("-")
    if (
        not parts
        or any(not part for part in parts)
        or any(not part.isalnum() for part in parts)
        or "/" in value
        or "." in value
        or value.lower() != value
    ):
        raise ValueError(f"{_prefix(path)}{field_name} must be lower kebab-case")


def _validate_relative_resource_path(
    value: str,
    field_name: str,
    path: Path | None,
) -> None:
    rel = Path(value)
    if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
        raise ValueError(f"{_prefix(path)}{field_name} must be a safe relative path")


def _prefix(path: Path | None) -> str:
    if path is None:
        return ""
    return f"{_rel(path)} "


def _rel(path: Path) -> str:
    return path.as_posix()
