"""Read-only guidance surfaces for profile and injection authoring."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Literal

from forma.runtime_assets import read_runtime_text

OutputFormat = Literal["markdown", "json"]


@dataclass(frozen=True)
class GuidanceSource:
    path: str
    title: str


@dataclass(frozen=True)
class GuidanceTopic:
    topic: str
    title: str
    sources: tuple[GuidanceSource, ...]


TOPICS = {
    "profile": GuidanceTopic(
        topic="profile",
        title="Forma Profile Guidance",
        sources=(
            GuidanceSource(
                path="source/skill-creator/references/profile-authoring-principles.md",
                title="Profile authoring principles",
            ),
            GuidanceSource(
                path="source/skill-creator/references/temporary-injection-generation.md",
                title="Temporary injection generation standard",
            ),
        ),
    ),
    "temporary-injection": GuidanceTopic(
        topic="temporary-injection",
        title="Forma Temporary Injection Guidance",
        sources=(
            GuidanceSource(
                path="source/skill-creator/references/temporary-injection-generation.md",
                title="Temporary injection generation standard",
            ),
            GuidanceSource(
                path="source/skill-creator/references/profile-authoring-principles.md",
                title="Profile authoring principles",
            ),
        ),
    ),
}


def render_guidance(
    topic: str,
    output_format: OutputFormat = "markdown",
    target_agent: str | None = None,
) -> str:
    """Render a read-only guidance topic from canonical source references."""
    if topic not in TOPICS:
        allowed = ", ".join(sorted(TOPICS))
        raise ValueError(f"unsupported explain topic {topic!r}; use {allowed}")
    if output_format not in ("markdown", "json"):
        raise ValueError("output_format must be markdown or json")

    spec = TOPICS[topic]
    source_payload = [
        {
            "path": source.path,
            "title": source.title,
            "content": read_runtime_text(*source.path.split("/")),
        }
        for source in spec.sources
    ]
    markdown = _render_markdown(spec, source_payload, target_agent)
    if output_format == "markdown":
        return markdown
    return json.dumps(
        {
            "topic": spec.topic,
            "title": spec.title,
            "target": target_agent,
            "sources": source_payload,
            "markdown": markdown,
        },
        indent=2,
        sort_keys=True,
    )


def _render_markdown(
    spec: GuidanceTopic,
    sources: list[dict[str, str]],
    target_agent: str | None,
) -> str:
    lines = [f"# {spec.title}", ""]
    if target_agent is not None:
        lines.extend([f"Target: `{target_agent}`", ""])
    lines.extend(
        [
            "This output is assembled from Forma canonical references; the CLI "
            "does not maintain a second copy of the guidance.",
            "",
            "Sources:",
        ]
    )
    for source in sources:
        lines.append(f"- `{source['path']}`")
    lines.append("")
    for source in sources:
        lines.extend([f"## {source['title']}", "", source["content"], ""])
    return "\n".join(lines).rstrip() + "\n"
