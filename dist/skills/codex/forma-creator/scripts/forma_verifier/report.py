"""Verifier report data structures + human and JSON formatters."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Dict, List


FAILURE_CLASS_BY_RULE_ID: Dict[str, str] = {
    "R000": "artifact_shape",
    "R001": "skill_metadata",
    "R002": "skill_identity",
    "R002a": "skill_identity",
    "R003": "artifact_shape",
    "R004": "resource_link",
    "R005": "runtime_boundary",
    "R006": "resource_link",
    "R101": "methodology_gate",
    "R102": "methodology_gate",
    "R103": "methodology_gate",
    "R104": "methodology_gate",
    "R106": "methodology_gate",
    "R107": "methodology_gate",
    "R201": "target_contract",
    "R202": "target_contract",
    "R203": "plugin_contract",
    "R301": "conditional_overlay",
}


def failure_class_for_rule(rule_id: str) -> str:
    """Return the stable semantic failure class for a verifier rule id."""
    return FAILURE_CLASS_BY_RULE_ID.get(rule_id, "unknown")


@dataclass
class RuleResult:
    rule_id: str
    skill_path: str
    severity: str  # "error" | "warning" | "info"
    message: str
    failure_class: str = ""

    def __post_init__(self) -> None:
        if not self.failure_class:
            self.failure_class = failure_class_for_rule(self.rule_id)

    def to_dict(self) -> Dict[str, str]:
        return {
            "rule_id": self.rule_id,
            "severity": self.severity,
            "failure_class": self.failure_class,
            "path": self.skill_path,
            "message": self.message,
        }


@dataclass
class Report:
    bundle_path: str
    bundle_kind: str  # "plan-first-bundle" | "creator-skill" | "unknown"
    results: List[RuleResult] = field(default_factory=list)

    @property
    def errors(self) -> List[RuleResult]:
        return [r for r in self.results if r.severity == "error"]

    @property
    def warnings(self) -> List[RuleResult]:
        return [r for r in self.results if r.severity == "warning"]

    @property
    def infos(self) -> List[RuleResult]:
        return [r for r in self.results if r.severity == "info"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def to_dict(self) -> Dict[str, object]:
        return {
            "schema": "forma.verify.report.v1",
            "path": self.bundle_path,
            "bundle_kind": self.bundle_kind,
            "passed": self.passed,
            "summary": {
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "infos": len(self.infos),
                "total": len(self.results),
            },
            "results": [r.to_dict() for r in self.results],
        }

    def format_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, sort_keys=True)

    def format_human(self) -> str:
        lines = [
            f"forma verify: {self.bundle_path}",
            f"  bundle kind: {self.bundle_kind}",
            f"  errors     : {len(self.errors)}",
            f"  warnings   : {len(self.warnings)}",
        ]
        if self.results:
            lines.append("")
            for r in self.results:
                marker = "x" if r.severity == "error" else "!"
                lines.append(f"  [{marker} {r.rule_id}] {r.skill_path}: {r.message}")
        if self.passed and not self.warnings:
            lines.append("")
            lines.append("  ok - all rules passed")
        elif self.passed:
            lines.append("")
            lines.append("  ok - no errors (warnings only)")
        return "\n".join(lines)
