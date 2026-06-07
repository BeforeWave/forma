"""Verifier report data structures + human-readable formatter."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class RuleResult:
    rule_id: str
    skill_path: str
    severity: str  # "error" | "warning" | "info"
    message: str


@dataclass
class Report:
    suite_path: str
    suite_kind: str  # "plan-first-suite" | "creator-skill" | "unknown"
    results: List[RuleResult] = field(default_factory=list)

    @property
    def errors(self) -> List[RuleResult]:
        return [r for r in self.results if r.severity == "error"]

    @property
    def warnings(self) -> List[RuleResult]:
        return [r for r in self.results if r.severity == "warning"]

    @property
    def passed(self) -> bool:
        return len(self.errors) == 0

    def format_human(self) -> str:
        lines = [
            f"forma verify: {self.suite_path}",
            f"  bundle kind: {self.suite_kind}",
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
