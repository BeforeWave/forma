"""Read-only guidance surfaces for agent workflow and profile authoring."""

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
    """Render a read-only guidance topic."""
    if topic == "agent":
        return render_agent_guidance(output_format, target_agent)
    if topic not in TOPICS:
        allowed = ", ".join(["agent", *sorted(TOPICS)])
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


def render_agent_guidance(
    output_format: OutputFormat = "markdown",
    target_agent: str | None = None,
) -> str:
    """Render the command-level guide agents should read before using Forma."""
    if output_format not in ("markdown", "json"):
        raise ValueError("output_format must be markdown or json")
    markdown = _render_agent_markdown(target_agent)
    if output_format == "markdown":
        return markdown
    return json.dumps(
        {
            "topic": "agent",
            "title": "Forma Agent Guide",
            "target": target_agent,
            "markdown": markdown,
        },
        indent=2,
        sort_keys=True,
    )


def _render_agent_markdown(target_agent: str | None) -> str:
    target = target_agent or "<target>"
    target_line = (
        f"Target: `{target_agent}`"
        if target_agent is not None
        else "Targets: `codex`, `claude-code`"
    )
    plugin_lines: list[str]
    if target_agent in (None, "codex"):
        plugin_intro = (
            "Use this only for Codex plugin source output. Install the verified "
            "plugin through Codex, not `forma install`."
        )
        if target_agent is None:
            plugin_intro = (
                "Codex plugin output is Codex-only. For Claude Code, generate a "
                "skill bundle instead. Install the verified plugin through Codex, "
                "not `forma install`."
            )
        plugin_lines = [
            "## Generate a Codex plugin from reviewed project rules",
            "",
            plugin_intro,
            "",
            "```bash",
            "forma create-plugin --target codex --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "```",
            "",
        ]
    else:
        plugin_lines = [
            "## Plugin output",
            "",
            f"`forma create-plugin --target {target}` is not supported. Generate "
            "a skill bundle instead.",
            "",
        ]

    lines = [
        "# Forma Agent Guide",
        "",
        target_line,
        "",
        "Use this guide to choose the right Forma command path before reading "
        "profile or injection authoring details.",
        "",
        "## If the artifact type or install route is unclear",
        "",
        "Run `doctor` first. Do this before handoff when you do not know whether "
        "a directory is a skill, skill bundle, creator, or Codex plugin source.",
        "",
        "```bash",
        "forma doctor <path>",
        "```",
        "",
        "## Ask an agent to summarize a project and generate workflows",
        "",
        "Build and install a target-specific creator. Verify the generated "
        "creator before installing it.",
        "",
        "```bash",
        f"forma build-creator --target {target} --output <dir>",
        f"forma verify <dir>/{target}/forma-creator",
        f"forma install --target {target} --scope project <dir>/{target}/forma-creator",
        "```",
        "",
        "## Generate a generic no-profile workflow",
        "",
        "Use this when the user wants the generic Plan-First workflow. This "
        "output does not contain project-specific rules.",
        "",
        "```bash",
        f"forma create-bundle --target {target} --output <dir>",
        "forma verify <dir>",
        f"forma install --target {target} --scope project <dir>",
        "```",
        "",
        "## Generate from reviewed durable project rules",
        "",
        "Use a tracked profile when project rules should be durable source. "
        "Verify shape first, then use drift to prove the artifact is fresh "
        "against the profile.",
        "",
        "```bash",
        f"forma create-bundle --target {target} --profile <profile.yaml> --output <dir>",
        "forma verify <dir>",
        "forma drift <dir> --profile <profile.yaml>",
        f"forma install --target {target} --scope project <dir>",
        "```",
        "",
        *plugin_lines,
        "## Adopt a same-origin creator artifact into profile source",
        "",
        "Use this only when the artifact carries same-origin Forma metadata. "
        "Adoption writes candidate profile source; regenerate from that profile "
        "and compare before treating it as durable.",
        "",
        "```bash",
        "forma profile adopt <artifact-dir> --output <profile-dir>",
        f"forma create-bundle --target {target} --profile <profile-dir>/profile.yaml --output <dir>",
        "forma verify <dir>",
        "forma drift <dir> --profile <profile-dir>/profile.yaml",
        "```",
        "",
        "## Command boundaries",
        "",
        "- `verify` checks generated artifact structure and required files.",
        "- `drift` checks whether generated output is fresh against its source "
        "profile, creator source, or release surface.",
        "- `doctor` identifies artifact kind and the correct install route.",
        "- `install` accepts verified local skills and skill bundles only; do "
        "not pass URLs or Codex plugin sources.",
        "- Omitting `--profile` generates generic no-profile workflow output, "
        "not project-specific rules.",
        "- Use `forma explain profile --target <target>` for durable profile authoring rules.",
        "- Use `forma explain temporary-injection --target <target>` for "
        "one-off creator injection rules.",
    ]
    return "\n".join(lines).rstrip() + "\n"


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
