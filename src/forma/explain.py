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
    if target_agent == "codex":
        plugin_lines = [
            "## Generate a Codex plugin from an already reviewed tracked profile",
            "",
            "Install the verified plugin through Codex marketplace/plugin UI, "
            "not `forma install`.",
            "",
            "```bash",
            "forma create-plugin --target codex --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "```",
            "",
        ]
    elif target_agent == "claude-code":
        plugin_lines = [
            "## Generate a Claude Code plugin from an already reviewed tracked profile",
            "",
            "Install the verified plugin root with `forma install --target "
            "claude-code`.",
            "",
            "```bash",
            "forma create-plugin --target claude-code --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "forma install --target claude-code --scope project <dir>",
            "```",
            "",
        ]
    else:
        plugin_lines = [
            "## Generate plugin output from an already reviewed tracked profile",
            "",
            "Codex plugins install through Codex marketplace/plugin UI. Claude "
            "Code plugin roots can be installed with `forma install --target "
            "claude-code`.",
            "",
            "```bash",
            "forma create-plugin --target codex --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "",
            "forma create-plugin --target claude-code --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "forma install --target claude-code --scope project <dir>",
            "```",
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
        "OpenCode compatibility uses Codex direct-skill output installed in "
        "`.agents/skills`; Forma does not expose `--target opencode` or "
        "OpenCode JS/TS plugin output.",
        "",
        "## Profile write boundary",
        "",
        "Profiles are durable project source. If no reviewed profile exists yet, "
        "do not write or modify profile files from the command guide alone.",
        "",
        "Run `forma explain profile --target <target>` first, then return both a "
        "`Profile YAML Proposal` and `Profile Review Packet` for human review. "
        "Write or promote profile files only after explicit user approval.",
        "",
        "Creator and temporary injection outputs are generated workflow "
        "artifacts, not durable profile source. `forma profile adopt` writes a "
        "candidate profile package; exact regeneration and drift proof show that "
        "the candidate can reproduce the artifact, not that it has been reviewed "
        "as source of truth.",
        "",
        "## If the artifact type or install route is unclear",
        "",
        "Run `doctor` first. Do this before handoff when you do not know whether "
        "a directory is a skill, skill bundle, creator, Codex plugin source, "
        "or Claude Code plugin source.",
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
        "## Generate from an already reviewed tracked profile",
        "",
        "Use this only when `<profile.yaml>` already exists as reviewed durable "
        "project source. If the profile does not exist yet, follow the profile "
        "write boundary first. Verify shape, then use drift to prove the artifact "
        "is fresh against the profile.",
        "",
        "```bash",
        f"forma create-bundle --target {target} --profile <profile.yaml> --output <dir>",
        "forma verify <dir>",
        "forma drift <dir> --profile <profile.yaml>",
        f"forma install --target {target} --scope project <dir>",
        "```",
        "",
        *plugin_lines,
        "## Adopt a same-origin creator artifact into a candidate profile package",
        "",
        "Use this only when the artifact carries same-origin Forma metadata. "
        "Adoption writes a candidate profile package, not durable source of "
        "truth. Regenerate from the candidate and compare before presenting it "
        "for human review; promote it only after explicit approval.",
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
        "- `install` accepts verified local skills, skill bundles, and Claude "
        "Code plugin roots only; do not pass URLs or Codex plugin sources.",
        "- Omitting `--profile` generates generic no-profile workflow output, "
        "not project-specific rules.",
        "- `profile adopt` writes candidate profile packages for review, not "
        "already-approved tracked profile source.",
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
