from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC_SOURCES = [
    ROOT / "README.md",
    ROOT / "README.zh-CN.md",
    ROOT / "STRUCTURE.md",
    *sorted((ROOT / "docs").glob("*.md")),
]
MARKDOWN_LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def test_relative_markdown_doc_links_exist() -> None:
    missing: list[str] = []

    for source in DOC_SOURCES:
        text = source.read_text(encoding="utf-8")
        for match in MARKDOWN_LINK_RE.finditer(text):
            target = match.group(1).strip()
            if not _is_relative_markdown_link(target):
                continue
            target_path = target.split("#", 1)[0]
            resolved = (source.parent / target_path).resolve()
            if not resolved.is_file():
                missing.append(f"{source.relative_to(ROOT)} -> {target}")

    assert not missing, "Missing markdown links:\n" + "\n".join(missing)


def _is_relative_markdown_link(target: str) -> bool:
    if (
        not target
        or target.startswith("#")
        or target.startswith("http://")
        or target.startswith("https://")
        or target.startswith("mailto:")
    ):
        return False
    return Path(target.split("#", 1)[0]).suffix == ".md"
