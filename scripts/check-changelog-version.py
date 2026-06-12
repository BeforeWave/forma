#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHANGELOG = ROOT / "CHANGELOG.md"
PYPROJECT = ROOT / "pyproject.toml"


@dataclass(frozen=True)
class ChangelogSection:
    version: str
    heading: str
    heading_suffix: str


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that the current Forma version has a changelog section.",
    )
    parser.add_argument(
        "--version",
        help="Version to check. Defaults to [project].version from pyproject.toml.",
    )
    parser.add_argument(
        "--publish",
        action="store_true",
        help="Require the changelog section to be finalized, not Unreleased.",
    )
    args = parser.parse_args()

    version = args.version or _project_version()
    section = _find_section(version)
    if section is None:
        print(
            f"error: CHANGELOG.md has no section for version {version!r}",
            file=sys.stderr,
        )
        print(
            f"expected a heading like: ## {version} - YYYY-MM-DD",
            file=sys.stderr,
        )
        return 1

    if args.publish and _is_unreleased(section.heading_suffix):
        print(
            f"error: changelog section for version {version!r} is still Unreleased",
            file=sys.stderr,
        )
        print(
            "finalize the heading date before publishing, then reuse that section for release notes",
            file=sys.stderr,
        )
        return 1

    status = "finalized" if not _is_unreleased(section.heading_suffix) else "unreleased"
    print(f"CHANGELOG.md: found {status} section: {section.heading}")
    return 0


def _project_version() -> str:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    return str(project["version"])


def _find_section(version: str) -> ChangelogSection | None:
    escaped = re.escape(version)
    heading_re = re.compile(rf"^##\s+\[?{escaped}\]?(?:\s+-\s*(.*))?\s*$")
    for line in CHANGELOG.read_text(encoding="utf-8").splitlines():
        match = heading_re.match(line)
        if match:
            return ChangelogSection(
                version=version,
                heading=line,
                heading_suffix=(match.group(1) or "").strip(),
            )
    return None


def _is_unreleased(value: str) -> bool:
    return value.casefold() == "unreleased"


if __name__ == "__main__":
    sys.exit(main())
