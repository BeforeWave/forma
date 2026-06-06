"""Verifier rules — structural + methodology, stdlib-only.

Each rule is a function taking (SkillFile, SuiteContext) and returning a list of
RuleResult. The runner walks all SKILL.md files and applies every rule from
ALL_RULES in order.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Dict, List, Mapping, Optional, Tuple

from forma_verifier.report import RuleResult


# ----- Frontmatter parsing (stdlib-only, limited YAML subset) -----

def parse_frontmatter(text: str) -> Tuple[Dict[str, object], str]:
    """Parse YAML frontmatter at the start of `text`.

    Returns (frontmatter_dict, body). Supports:
    - top-level scalar key/value pairs
    - one level of nested mapping (e.g. `metadata:` followed by indented keys)
    - quoted or unquoted string values
    - line comments starting with `#`

    Anything more complex (flow style, anchors, lists, multi-line scalars) is not
    supported in v1. Skills using such features should be rejected by R001 because
    required keys will appear missing.
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return ({}, text)
    end_idx: Optional[int] = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return ({}, text)
    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1:])
    fm: Dict[str, object] = {}
    current_section: Optional[str] = None
    for line in fm_lines:
        stripped = line.rstrip()
        if not stripped.strip() or stripped.strip().startswith("#"):
            continue
        indent = len(stripped) - len(stripped.lstrip())
        text_part = stripped.lstrip()
        if ":" not in text_part:
            continue
        key, _, value = text_part.partition(":")
        key = key.strip()
        value = value.strip()
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            value = value[1:-1]
        if indent == 0:
            current_section = None
            if value:
                fm[key] = value
            else:
                # nested mapping begins
                current_section = key
                fm[key] = {}
        else:
            if current_section is not None and isinstance(fm.get(current_section), dict):
                fm[current_section][key] = value  # type: ignore[index]
    return (fm, body)


# ----- Skill / suite data model -----

@dataclass
class SkillFile:
    path: Path
    relative_path: str  # relative to suite root, posix-style
    parent_dir_name: str
    frontmatter: Dict[str, object]
    body: str


@dataclass
class SuiteContext:
    root: Path
    skills: List[SkillFile]
    suite_kind: str  # "plan-first-suite" | "creator-skill" | "unknown"
    manifest: Mapping[str, object]


PLAN_FIRST_KINDS = ["shape", "gauge", "seal", "pour", "flow"]
FORMA_STAGE_PREFIX = "forma"


def plan_first_kind_from_name(value: object) -> Optional[str]:
    if not isinstance(value, str):
        return None
    for kind in PLAN_FIRST_KINDS:
        if value == kind or value == f"{FORMA_STAGE_PREFIX}-{kind}":
            return kind
    return None


def skill_kind(skill: SkillFile, ctx: SuiteContext | None = None) -> Optional[str]:
    """Identify which plan-first kind this skill represents, if any.

    Detection order: frontmatter name suffix, then parent directory name.
    """
    if ctx is not None:
        emitted = ctx.manifest.get("emitted_skills")
        if isinstance(emitted, dict):
            name = skill.frontmatter.get("name", "")
            for kind, item in emitted.items():
                if not isinstance(kind, str) or kind not in PLAN_FIRST_KINDS:
                    continue
                if not isinstance(item, dict):
                    continue
                directory = item.get("directory")
                emitted_name = item.get("name")
                if skill.parent_dir_name == directory or name == emitted_name:
                    return kind
    kind = plan_first_kind_from_name(skill.frontmatter.get("name", ""))
    if kind is not None:
        return kind
    return plan_first_kind_from_name(skill.parent_dir_name)


# ----- Regular expressions used by structural rules -----

KEBAB_CASE_RE = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")
SECTION_H2_RE = re.compile(r"^##\s+\S", re.MULTILINE)
SECTION_H2_TITLE_RE = re.compile(r"^##\s+(.+?)\s*$")
# Match a backtick-quoted reference path like `references/decision-gate.md`.
# Also match common markdown link style: `[label](references/foo.md)` and bare references/foo.md.
REFERENCE_INLINE_RE = re.compile(
    r"(?:`|\(|\s|^)(references/[A-Za-z0-9_./-]+\.md)(?:`|\)|\s|$)"
)
BUNDLED_PATH_RE = re.compile(
    r"(?:`|\(|\s|^)((?:scripts|script)/[A-Za-z0-9_./-]+)(?:`|\)|\s|$)"
)
CROSS_SKILL_RE = re.compile(r"\.\./[A-Za-z0-9._-]+/(scripts|references)")


# ----- Structural rules (apply to all suites) -----

def check_frontmatter_valid(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    results: List[RuleResult] = []
    if not skill.frontmatter:
        results.append(RuleResult(
            "R001", skill.relative_path, "error",
            "missing or empty YAML frontmatter (must be enclosed in `---` markers)"
        ))
        return results
    for key in ("name", "description"):
        if key not in skill.frontmatter or not skill.frontmatter.get(key):
            results.append(RuleResult(
                "R001", skill.relative_path, "error",
                f"frontmatter missing required key `{key}`"
            ))
    extra_keys = sorted(set(skill.frontmatter) - {"name", "description"})
    if extra_keys:
        results.append(RuleResult(
            "R001", skill.relative_path, "error",
            f"frontmatter has unsupported keys: {extra_keys}"
        ))
    return results


def check_name_kebab_case(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    name = skill.frontmatter.get("name", "")
    if not isinstance(name, str) or not name:
        return []  # R001 will have caught this already
    if not KEBAB_CASE_RE.match(name):
        return [RuleResult(
            "R002", skill.relative_path, "error",
            f"frontmatter `name` is not kebab-case: {name!r}"
        )]
    return []


def check_name_kind_match(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    """For plan-first suite skills, name must equal the parent skill directory."""
    if ctx.suite_kind != "plan-first-suite":
        return []
    emitted = ctx.manifest.get("emitted_skills")
    if isinstance(emitted, dict):
        for kind, item in emitted.items():
            if not isinstance(kind, str) or not isinstance(item, dict):
                continue
            directory = item.get("directory")
            emitted_name = item.get("name")
            if skill.parent_dir_name == directory:
                name = skill.frontmatter.get("name", "")
                if name != emitted_name:
                    return [RuleResult(
                        "R002a", skill.relative_path, "error",
                        f"frontmatter `name` ({name!r}) must equal emitted "
                        f"skill name `{emitted_name}`"
                    )]
                return []
    if plan_first_kind_from_name(skill.parent_dir_name) is None:
        return []
    name = skill.frontmatter.get("name", "")
    if not isinstance(name, str) or not name:
        return []
    if name != skill.parent_dir_name:
        return [RuleResult(
            "R002a", skill.relative_path, "error",
            f"frontmatter `name` ({name!r}) must equal the parent skill "
            f"directory `{skill.parent_dir_name}`"
        )]
    return []


def check_body_has_sections(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    if not SECTION_H2_RE.search(skill.body):
        return [RuleResult(
            "R003", skill.relative_path, "error",
            "SKILL.md body has no H2 (`##`) section"
        )]
    return []


def check_references_resolve(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    results: List[RuleResult] = []
    seen: set = set()
    for match in REFERENCE_INLINE_RE.finditer(skill.body):
        ref_path = match.group(1)
        if ref_path in seen:
            continue
        seen.add(ref_path)
        full_path = skill.path.parent / ref_path
        if not full_path.exists():
            results.append(RuleResult(
                "R004", skill.relative_path, "error",
                f"referenced file does not exist: {ref_path}"
            ))
    return results


def check_bundled_paths_resolve(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    results: List[RuleResult] = []
    seen: set = set()
    for match in BUNDLED_PATH_RE.finditer(skill.body):
        rel_path = match.group(1)
        if rel_path in seen:
            continue
        seen.add(rel_path)
        full_path = skill.path.parent / rel_path
        if not full_path.exists():
            results.append(RuleResult(
                "R006", skill.relative_path, "error",
                f"referenced bundled file does not exist: {rel_path}"
            ))
    return results


def check_no_cross_skill_borrowing(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    if CROSS_SKILL_RE.search(skill.body):
        return [RuleResult(
            "R005", skill.relative_path, "error",
            "cross-skill borrowing detected (paths like `../<other>/scripts/` "
            "or `../<other>/references/` are forbidden)"
        )]
    return []


# ----- Methodology rules (apply only to plan-first suite skills) -----

def _make_keyword_rule(
    rule_id: str,
    target_kind: str,
    required_keywords: List[object],
    title: str,
) -> Callable[[SkillFile, SuiteContext], List[RuleResult]]:
    def check(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
        if ctx.suite_kind != "plan-first-suite":
            return []
        if skill_kind(skill, ctx) != target_kind:
            return []
        body_lower = skill.body.lower()
        missing = [
            _keyword_label(kw)
            for kw in required_keywords
            if not _keyword_present(body_lower, kw)
        ]
        if missing:
            return [RuleResult(
                rule_id, skill.relative_path, "error",
                f"{title}; missing required keywords: {missing}"
            )]
        return []
    return check


def _keyword_present(body_lower: str, keyword: object) -> bool:
    if isinstance(keyword, tuple):
        return any(str(item).lower() in body_lower for item in keyword)
    return str(keyword).lower() in body_lower


def _keyword_label(keyword: object) -> str:
    if isinstance(keyword, tuple):
        return " or ".join(str(item) for item in keyword)
    return str(keyword)


check_shape_methodology = _make_keyword_rule(
    "R101", "shape",
    [
        "Decision Gate",
        "Goal",
        "Scope",
        "Approach",
        "Validation",
        "Plan Strategy",
        ("chat-only", "chat only"),
    ],
    "shape skill must cite Decision Gate dimensions and chat-only output",
)

check_gauge_methodology = _make_keyword_rule(
    "R102", "gauge",
    ["read-only", "grounding handoff", ("seal", "finalize-plan")],
    "gauge skill must cite read-only inspection and grounding handoff for seal",
)

check_seal_methodology = _make_keyword_rule(
    "R103", "seal",
    ["plan.md", "tasks.md", "forma-workflow"],
    "seal skill must cite plan.md / tasks.md outputs and forma-workflow init",
)

check_pour_methodology = _make_keyword_rule(
    "R104", "pour",
    ["review-ready", "complete"],
    "pour skill must cite review-ready / complete workflow steps",
)


# ----- Conditional overlay rules (mechanism-only; business routes are opaque) -----

def check_conditional_overlays(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    if ctx.suite_kind != "plan-first-suite":
        return []
    raw = ctx.manifest.get("conditional_overlays")
    if raw is None:
        return []
    results: List[RuleResult] = []
    if _is_first_skill(skill, ctx):
        results.extend(_check_conditional_manifest(raw, skill.relative_path))
    if not isinstance(raw, dict):
        return results
    decision_name = _conditional_decision_name(raw)
    if not decision_name:
        return results
    kind = skill_kind(skill, ctx)
    if kind is None:
        return results
    body_lower = skill.body.lower()
    decision_lower = decision_name.lower()
    if decision_lower not in body_lower:
        results.append(RuleResult(
            "R301", skill.relative_path, "error",
            f"conditional overlay skill must mention decision name `{decision_name}`"
        ))
    if kind == "shape" and "settle" not in body_lower:
        results.append(RuleResult(
            "R301", skill.relative_path, "error",
            f"shape must require settling conditional decision `{decision_name}`"
        ))
    if kind == "seal" and "plan.md" not in body_lower:
        results.append(RuleResult(
            "R301", skill.relative_path, "error",
            f"seal must require recording conditional decision `{decision_name}` in plan.md"
        ))
    if kind in {"pour", "flow"}:
        missing_action = _conditional_missing_action(raw)
        required_action = (missing_action or "stop-for-plan-correction").lower()
        if required_action not in body_lower:
            results.append(RuleResult(
                "R301", skill.relative_path, "error",
                f"{kind} must stop for plan correction when `{decision_name}` is missing"
            ))
    sections = _h2_sections(skill.body)
    conditional_section = sections.get("Conditional References", "")
    if "Conditional References" not in sections:
        results.append(RuleResult(
            "R301", skill.relative_path, "error",
            "conditional overlay suite skills must include `## Conditional References`"
        ))
    unconditional_text = "\n".join(
        sections.get(title, "")
        for title in ("Always Load", "Read After Gate", "Load As Needed")
    )
    for ref_path in _conditional_reference_paths_for_kind(raw, kind):
        if ref_path in unconditional_text:
            results.append(RuleResult(
                "R301", skill.relative_path, "error",
                f"overlay reference leaks into an unconditional read section: {ref_path}"
            ))
        if ref_path not in conditional_section:
            results.append(RuleResult(
                "R301", skill.relative_path, "error",
                f"overlay reference is missing from Conditional References: {ref_path}"
            ))
    return results


def _is_first_skill(skill: SkillFile, ctx: SuiteContext) -> bool:
    first = min((item.relative_path for item in ctx.skills), default="")
    return skill.relative_path == first


def _check_conditional_manifest(raw: object, path: str) -> List[RuleResult]:
    if not isinstance(raw, dict):
        return [RuleResult(
            "R301", path, "error",
            "manifest conditional_overlays must be an object"
        )]
    results: List[RuleResult] = []
    decision_name = _conditional_decision_name(raw)
    if not decision_name:
        results.append(RuleResult(
            "R301", path, "error",
            "manifest conditional_overlays.decision.name is required"
        ))
    decision = raw.get("decision")
    if isinstance(decision, dict):
        if decision.get("must_record_in_plan") is not True:
            results.append(RuleResult(
                "R301", path, "error",
                "conditional decision must_record_in_plan must be true"
            ))
        if decision.get("missing_during_execution") != "stop-for-plan-correction":
            results.append(RuleResult(
                "R301", path, "error",
                "conditional decision missing_during_execution must be stop-for-plan-correction"
            ))
    routes = raw.get("routes")
    overlays = raw.get("overlays")
    overlay_ids: set[str] = set()
    if not isinstance(overlays, dict):
        results.append(RuleResult(
            "R301", path, "error",
            "manifest conditional_overlays.overlays must be an object"
        ))
        overlays = {}
    for overlay_id in overlays:
        if not isinstance(overlay_id, str) or not KEBAB_CASE_RE.match(overlay_id):
            results.append(RuleResult(
                "R301", path, "error",
                f"conditional overlay id must be kebab-case: {overlay_id!r}"
            ))
            continue
        overlay_ids.add(overlay_id)
    if not isinstance(routes, list) or not routes:
        results.append(RuleResult(
            "R301", path, "error",
            "manifest conditional_overlays.routes must be a non-empty list"
        ))
        return results
    route_ids: set[str] = set()
    for index, route in enumerate(routes):
        if not isinstance(route, dict):
            results.append(RuleResult(
                "R301", path, "error",
                f"conditional route {index} must be an object"
            ))
            continue
        route_id = route.get("id")
        if not isinstance(route_id, str) or not KEBAB_CASE_RE.match(route_id):
            results.append(RuleResult(
                "R301", path, "error",
                f"conditional route id must be kebab-case: {route_id!r}"
            ))
        elif route_id in route_ids:
            results.append(RuleResult(
                "R301", path, "error",
                f"conditional route id is duplicated: {route_id}"
            ))
        else:
            route_ids.add(route_id)
        route_overlays = route.get("overlays", [])
        if not isinstance(route_overlays, list):
            results.append(RuleResult(
                "R301", path, "error",
                f"conditional route {route_id!r} overlays must be a list"
            ))
            continue
        route_overlay_ids: set[str] = set()
        for overlay_id in route_overlays:
            if not isinstance(overlay_id, str) or not KEBAB_CASE_RE.match(overlay_id):
                results.append(RuleResult(
                    "R301", path, "error",
                    f"conditional route {route_id!r} overlay id must be kebab-case: {overlay_id!r}"
                ))
                continue
            if overlay_id in route_overlay_ids:
                results.append(RuleResult(
                    "R301", path, "error",
                    f"conditional route {route_id!r} repeats overlay {overlay_id!r}"
                ))
            route_overlay_ids.add(overlay_id)
            if overlay_id not in overlay_ids:
                results.append(RuleResult(
                    "R301", path, "error",
                    f"conditional route {route_id!r} references missing overlay {overlay_id!r}"
                ))
    return results


def _conditional_decision_name(raw: Mapping[str, object]) -> str:
    decision = raw.get("decision")
    if not isinstance(decision, dict):
        return ""
    name = decision.get("name")
    if not isinstance(name, str):
        return ""
    return name.strip()


def _conditional_missing_action(raw: Mapping[str, object]) -> str:
    decision = raw.get("decision")
    if not isinstance(decision, dict):
        return ""
    action = decision.get("missing_during_execution")
    if not isinstance(action, str):
        return ""
    return action.strip()


def _conditional_reference_paths_for_kind(
    raw: Mapping[str, object],
    kind: str,
) -> List[str]:
    refs: List[str] = []
    routes = raw.get("routes")
    if not isinstance(routes, list):
        return refs
    for route in routes:
        if not isinstance(route, dict):
            continue
        references = route.get("references")
        if not isinstance(references, dict):
            continue
        values = references.get(kind, [])
        if not isinstance(values, list):
            continue
        for item in values:
            if isinstance(item, str) and item.startswith("references/") and item not in refs:
                refs.append(item)
    return refs


def _h2_sections(body: str) -> Dict[str, str]:
    sections: Dict[str, List[str]] = {}
    current: str | None = None
    for line in body.splitlines():
        match = SECTION_H2_TITLE_RE.match(line)
        if match:
            current = match.group(1).strip()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {
        title: "\n".join(lines)
        for title, lines in sections.items()
    }


# ----- Target rules (apply when .forma-manifest.json records a target) -----

def check_target_metadata(skill: SkillFile, ctx: SuiteContext) -> List[RuleResult]:
    if ctx.suite_kind != "plan-first-suite":
        return []
    kind = skill_kind(skill, ctx)
    if kind is None:
        return []
    target = ctx.manifest.get("target")
    if target is None:
        return []
    if target == "codex":
        return _check_codex_metadata(skill)
    if target == "claude-code":
        return _check_claude_code_metadata(skill)
    return [RuleResult(
        "R201", skill.relative_path, "error",
        f"manifest target is unsupported: {target!r}"
    )]


def _check_codex_metadata(skill: SkillFile) -> List[RuleResult]:
    metadata = skill.path.parent / "agents" / "openai.yaml"
    if not metadata.is_file():
        return [RuleResult(
            "R201", skill.relative_path, "error",
            "codex target requires agents/openai.yaml in every generated skill"
        )]
    text = metadata.read_text(encoding="utf-8")
    required = [
        "interface:",
        "display_name:",
        "short_description:",
        "default_prompt:",
    ]
    missing = [item for item in required if item not in text]
    if missing:
        return [RuleResult(
            "R201", skill.relative_path, "error",
            f"agents/openai.yaml missing required fields: {missing}"
        )]
    return []


def _check_claude_code_metadata(skill: SkillFile) -> List[RuleResult]:
    forbidden = []
    if (skill.path.parent / "agents" / "openai.yaml").exists():
        forbidden.append("agents/openai.yaml")
    if (skill.path.parent / "interfaces" / "codex").exists():
        forbidden.append("interfaces/codex")
    if forbidden:
        return [RuleResult(
            "R202", skill.relative_path, "error",
            f"claude-code target must not include Codex metadata: {forbidden}"
        )]
    return []


# ----- Rule registry -----

ALL_RULES: List[Callable[[SkillFile, SuiteContext], List[RuleResult]]] = [
    check_frontmatter_valid,
    check_name_kebab_case,
    check_name_kind_match,
    check_body_has_sections,
    check_references_resolve,
    check_bundled_paths_resolve,
    check_no_cross_skill_borrowing,
    check_shape_methodology,
    check_gauge_methodology,
    check_seal_methodology,
    check_pour_methodology,
    check_conditional_overlays,
    check_target_metadata,
]
