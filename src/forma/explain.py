"""Read-only guidance surfaces for agent workflow and profile authoring."""

from __future__ import annotations

from dataclasses import dataclass

from forma.reports import (
    ActionableReport,
    NextAction,
    ReportFormat,
    ReportSection,
    render_report,
)
from forma.runtime_assets import read_runtime_text

OutputFormat = ReportFormat


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
    output_format: OutputFormat = "human",
    target_agent: str | None = None,
) -> str:
    """Render a read-only guidance topic."""
    if topic == "agent":
        return render_agent_guidance(output_format, target_agent)
    if topic not in TOPICS:
        allowed = ", ".join(["agent", *sorted(TOPICS)])
        raise ValueError(f"unsupported explain topic {topic!r}; use {allowed}")
    if output_format not in ("human", "agent", "json"):
        raise ValueError("output_format must be human, agent, or json")

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
    guidance_payload = (
        _render_human_markdown(spec, source_payload, target_agent)
        if output_format == "human"
        else markdown
    )
    report = ActionableReport(
        command=f"forma explain {topic}",
        subject=target_agent or "all-targets",
        status="ready",
        summary=f"{spec.title} is available",
        sections=(
            ReportSection(
                kind="guidance",
                title=spec.title,
                payload=guidance_payload,
            ),
            ReportSection(
                kind="sources",
                title="Sources",
                payload={
                    "items": [
                        {"path": source["path"], "title": source["title"]}
                        for source in source_payload
                    ]
                },
            ),
        ),
        next_actions=_topic_next_actions(topic, target_agent),
        metadata={
            "topic": spec.topic,
            "target": target_agent,
            "sources": source_payload,
            "markdown": markdown,
        },
    )
    return render_report(report, output_format)


def render_agent_guidance(
    output_format: OutputFormat = "human",
    target_agent: str | None = None,
) -> str:
    """Render the command-level guide agents should read before using Forma."""
    if output_format not in ("human", "agent", "json"):
        raise ValueError("output_format must be human, agent, or json")
    markdown = _render_agent_markdown(target_agent)
    report = ActionableReport(
        command="forma explain agent",
        subject=target_agent or "all-targets",
        status="ready",
        summary="Forma Agent Guide is available",
        sections=(
            ReportSection(
                kind="guidance",
                title="Forma Agent Guide",
                payload=markdown,
            ),
        ),
        next_actions=_topic_next_actions("agent", target_agent),
        metadata={
            "topic": "agent",
            "title": "Forma Agent Guide",
            "target": target_agent,
            "markdown": markdown,
        },
    )
    return render_report(report, output_format)


def _topic_next_actions(topic: str, target_agent: str | None) -> tuple[NextAction, ...]:
    target = target_agent or "<target>"
    if topic == "agent":
        return (
            NextAction(
                title="draft project rules before generation",
                command=f"forma explain profile --target {target}",
                description="Use when no approved profile exists yet.",
            ),
            NextAction(
                title="build from approved profile",
                command=f"forma build bundle --target {target} --profile <profile.yaml> --output <dir>",
                description=(
                    "If the profile directory has a completed reinstall-workflow.sh, "
                    "run that fixed-fact script first. If the script is missing or "
                    "bootstrap-incomplete, settle install facts with the user and "
                    "complete the script before reporting reusable reinstall success."
                ),
                stop_condition=(
                    "install facts are not confirmed or reinstall-workflow.sh is "
                    "missing/bootstrap-incomplete"
                ),
                forbidden=(
                    "do not reconstruct profile-backed install commands before checking reinstall-workflow.sh",
                    "do not report reusable reinstall success until the completed script has run",
                ),
            ),
            NextAction(
                title="diagnose artifact install route",
                command="forma doctor <path>",
            ),
        )
    if topic == "profile":
        return (
            NextAction(
                title="return profile proposal and review packet",
                description="Write files only after explicit user approval.",
            ),
            NextAction(
                title="build after approval",
                command=f"forma build bundle --target {target} --profile <profile.yaml> --output <dir>",
            ),
            NextAction(
                title="settle reusable reinstall facts",
                description=(
                    "After first build/install exploration, confirm artifact kind, "
                    "target, plugin id when relevant, marketplace name/source when "
                    "relevant, install selector, and visibility check. Write those "
                    "facts into the profile-local reinstall-workflow.sh before "
                    "calling the flow reusable."
                ),
                stop_condition="profile-local reinstall facts are not confirmed",
            ),
        )
    return (
        NextAction(
            title="classify one-off rules",
            description="Keep temporary injection separate from approved profile source.",
        ),
    )


def _render_agent_markdown(target_agent: str | None) -> str:
    generation_target = target_agent or "<generation-target>"
    install_target = target_agent or "<install-target>"
    target_line = (
        f"Target: `{target_agent}`"
        if target_agent is not None
        else "Generation targets: `codex`, `claude-code`, `opencode`; plugin targets: `codex`, `claude-code`; install targets: `codex`, `claude-code`, `opencode`"
    )
    plugin_lines: list[str]
    if target_agent == "codex":
        plugin_lines = [
            "## Generate a Codex plugin from an approved profile",
            "",
            "Run drift before any postprocess. If the artifact is intentionally "
            "postprocessed, run postprocess after drift and use `forma verify` "
            "as the final gate for the postprocessed artifact.",
            "",
            "Codex plugin install state belongs to Codex, not `forma install`. "
            "During bootstrap discovery or diagnostics, inspect configured "
            "marketplaces as needed, then ask the user to confirm plugin id, "
            "marketplace name, marketplace source, install selector, and "
            "visibility check. Stable reinstall scripts must encode those "
            "facts and must not list marketplaces or ask for marketplace "
            "choices at runtime.",
            "",
            "```bash",
            "forma build plugin --target codex --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "codex plugin add <confirmed-plugin-id>@<confirmed-marketplace>",
            "```",
            "",
            "If Codex CLI output or marketplace behavior differs from this "
            "guide, consult current Codex plugin docs or "
            "`codex plugin marketplace --help`.",
            "",
        ]
    elif target_agent == "claude-code":
        plugin_lines = [
            "## Generate a Claude Code plugin from an approved profile",
            "",
            "Install the verified plugin root with `forma install --target "
            "claude-code`.",
            "",
            "```bash",
            "forma build plugin --target claude-code --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "forma install --target claude-code --scope project <dir>",
            "```",
            "",
        ]
    elif target_agent == "opencode":
        plugin_lines = [
            "## OpenCode plugin output",
            "",
            "Forma does not generate OpenCode JS/TS runtime plugins. Use "
            "`forma build bundle --target opencode` for native OpenCode "
            "direct skill output.",
            "",
        ]
    else:
        plugin_lines = [
            "## Generate plugin output from an approved profile",
            "",
            "Codex plugin install state belongs to Codex. During bootstrap "
            "discovery or diagnostics, inspect configured marketplaces as "
            "needed, then ask the user to confirm plugin id, marketplace name, "
            "marketplace source, install selector, and visibility check. Stable "
            "reinstall scripts must encode those facts and must not list "
            "marketplaces or ask for marketplace choices at runtime. Claude Code "
            "plugin roots can be installed with `forma install --target "
            "claude-code`.",
            "",
            "```bash",
            "forma build plugin --target codex --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "codex plugin add <confirmed-plugin-id>@<confirmed-marketplace>",
            "",
            "forma build plugin --target claude-code --profile <profile.yaml> --output <dir>",
            "forma verify <dir>",
            "forma drift <dir> --profile <profile.yaml>",
            "forma install --target claude-code --scope project <dir>",
            "```",
            "",
            "If a generated artifact is intentionally postprocessed, run "
            "postprocess after drift and use `forma verify` as the final gate.",
            "If Codex CLI output or marketplace behavior differs from this "
            "guide, consult current Codex plugin docs or "
            "`codex plugin marketplace --help`.",
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
        "OpenCode uses native direct skill output. Generate an OpenCode bundle "
        "with `forma build bundle --target opencode`, verify it, then install "
        "it with `forma install --target opencode`; project installs land in "
        "`.opencode/skills` and user installs land in "
        "`$HOME/.config/opencode/skills`. Forma does not generate OpenCode "
        "JS/TS runtime plugins.",
        "",
        "## Profile write boundary",
        "",
        "Profiles are structured project-rule input for workflow generation. "
        "They can be temporary for a trial workflow or committed for long-term "
        "reuse.",
        "",
        "Run `forma explain profile --target <target>` first, then return both a "
        "`Profile YAML Proposal` and `Profile Review Packet` for human review. "
        "Write profile files only after explicit user approval. Commit them only "
        "when the rules should be reused.",
        "",
        "Creator and temporary injection outputs are generated workflow "
        "artifacts, not automatically approved profile source. `forma profile "
        "adopt` writes a candidate profile package; exact regeneration and drift "
        "proof show that the candidate can reproduce the artifact, not that it "
        "has been reviewed as source of truth.",
        "",
        "## Profile-local workflow scripts",
        "",
        "When using an approved profile, treat the profile file's parent "
        "directory as the profile directory. Before composing generation or "
        "installation commands from this guide, check that directory for "
        "a profile-local script named `reinstall-workflow.sh`.",
        "",
        "If `<profile-dir>/reinstall-workflow.sh` exists and is not marked "
        "bootstrap-incomplete, run it from the profile directory instead of "
        "assembling `forma build bundle`, `forma build plugin`, install, "
        "marketplace refresh, or visibility check commands by hand. Run the "
        "script from the profile directory so relative paths stay stable, and "
        "verify or drift exactly as the script specifies.",
        "",
        "If the profile-local reinstall script is missing or "
        "bootstrap-incomplete, treat that as a bootstrap state, not a normal "
        "manual build/install path. Before running hand-assembled build or "
        "install commands, ask the user whether to complete "
        "`reinstall-workflow.sh` with confirmed install facts and then run the "
        "workflow through that script. Only proceed with a one-off manual flow "
        "when the user explicitly says not to keep scripts for this profile or "
        "explicitly asks for a temporary one-time run.",
        "",
        "Bootstrap goal: explore whatever local environment details are needed "
        "to make this profile build/install repeatable, then preserve that "
        "verified local process beside the profile. This is where target-specific "
        "marketplace paths, plugin selectors, output directories, remove/add "
        "steps, and installation checks belong. Do not make future agents "
        "rediscover those details from scratch.",
        "",
        "Required install facts before reusable success: artifact kind, target, "
        "plugin id when the artifact kind is plugin, marketplace name and "
        "marketplace source when the install route uses a marketplace, install "
        "selector, and visibility check.",
        "",
        "When the user approves bootstrap, write one real script, not notes. "
        "`reinstall-workflow.sh` must reproduce generation and freshness gates "
        "for the same profile, including `forma build bundle` or `forma build "
        "plugin`, `forma drift` when a profile-backed artifact is produced, "
        "`forma verify`, the local install route for this environment, any "
        "target-specific marketplace sync, `forma install`, or explicit plugin "
        "add/remove commands, followed by the required installation visibility "
        "check.",
        "",
        "Stable reinstall scripts must encode fixed facts. They must not run "
        "`codex plugin marketplace list`, ask the user which marketplace to use, "
        "or leave plugin id, marketplace, selector, or source refresh decisions "
        "open at runtime. Marketplace listing belongs only to bootstrap "
        "discovery or diagnostics before those facts are written.",
        "",
        "Script authoring rules: resolve the repository root and profile path "
        "relative to the script directory; keep output paths configurable with "
        "environment variables while preserving the just-used defaults; include "
        "`set -euo pipefail`; do not write placeholder commands; make scripts "
        "executable; and run the new script once before reporting bootstrap "
        "success.",
        "",
        "Your final install report must include the profile-local reinstall "
        "state: reused existing script, bootstrapped the script and ran it, "
        "user requested one-off manual flow, or blocked waiting for the "
        "bootstrap decision.",
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
        "## Draft project rules, then generate workflow output",
        "",
        "Use this when no approved profile exists yet. Load profile guidance, "
        "summarize project rules, return a profile proposal and review packet, "
        "then generate only after user approval.",
        "",
        "```bash",
        f"forma explain profile --target {generation_target}",
        f"forma build bundle --target {generation_target} --profile <profile.yaml> --output <dir>",
        "forma verify <dir>",
        f"forma install --target {install_target} --scope project <dir>",
        "```",
        "",
        "## Generate a generic no-profile workflow",
        "",
        "Use this when the user wants the generic Plan-First workflow. This "
        "output does not contain project-specific rules.",
        "",
        "```bash",
        f"forma build bundle --target {generation_target} --output <dir>",
        "forma verify <dir>",
        f"forma install --target {install_target} --scope project <dir>",
        "```",
        "",
        "## Generate from an approved profile",
        "",
        "Use this when `<profile.yaml>` already exists and has been approved for "
        "this generation. If the profile does not exist yet, follow the profile "
        "write boundary first. Verify shape, then use drift to prove the "
        "artifact is fresh against the profile.",
        "",
        "```bash",
        f"forma build bundle --target {generation_target} --profile <profile.yaml> --output <dir>",
        "forma verify <dir>",
        "forma drift <dir> --profile <profile.yaml>",
        f"forma install --target {install_target} --scope project <dir>",
        "```",
        "",
        *plugin_lines,
        "## Optional on-the-spot creator path",
        "",
        "Use this only when the user specifically wants a creator run instead "
        "of handling a profile file first. Verify the generated creator before "
        "installing it.",
        "",
        "```bash",
        f"forma build creator --target {generation_target} --output <dir>",
        f"forma verify <dir>/{generation_target}/forma-creator",
        f"forma install --target {install_target} --scope project <dir>/{generation_target}/forma-creator",
        "```",
        "",
        "## Adopt a same-origin creator artifact into a candidate profile package",
        "",
        "Use this only when the artifact carries same-origin Forma metadata. "
        "Adoption writes a candidate profile package, not approved source of "
        "truth. Regenerate from the candidate and compare before presenting it "
        "for human review; promote it only after explicit approval.",
        "",
        "```bash",
        "forma profile adopt <artifact-dir> --output <profile-dir>",
        f"forma build bundle --target {generation_target} --profile <profile-dir>/profile.yaml --output <dir>",
        "forma verify <dir>",
        "forma drift <dir> --profile <profile-dir>/profile.yaml",
        "```",
        "",
        "## Command boundaries",
        "",
        "- Build workflow artifacts with `forma build bundle`, `forma build "
        "plugin`, or `forma build creator`.",
        "- Do not use removed command entrypoints: `forma create`, "
        "`forma create-bundle`, `forma create-plugin`, or "
        "`forma build-creator`. Do not add compatibility aliases for them.",
        "- `verify` checks generated artifact structure and required files.",
        "- `drift` checks whether generated output is fresh against its source "
        "profile, creator source, or release surface.",
        "- `doctor` identifies artifact kind and the correct install route.",
        "- `install` accepts verified local skills, skill bundles, and Claude "
        "Code plugin roots only; do not pass URLs, Codex plugin sources, or "
        "OpenCode JS/TS runtime plugins.",
        "- Omitting `--profile` generates generic no-profile workflow output, "
        "not project-specific rules.",
        "- `profile adopt` writes candidate profile packages for review, not "
        "already-approved profile source.",
        "- Use `forma explain profile --target <target>` for profile authoring rules.",
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


def _render_human_markdown(
    spec: GuidanceTopic,
    sources: list[dict[str, str]],
    target_agent: str | None,
) -> str:
    lines = [f"# {spec.title}", ""]
    if target_agent is not None:
        lines.extend([f"Target: `{target_agent}`", ""])
    lines.extend(
        [
            "This is reader-facing guidance. Use `--format agent` for the full "
            "executable authoring contract, or `--format json` for structured "
            "tool output.",
            "",
        ]
    )
    if spec.topic == "profile":
        lines.extend(
            [
                "## Profile Renderer Boundary",
                "",
                "- Use profiles for durable, repeated project workflow rules.",
                "- Keep task-specific or one-off generation constraints out of the profile.",
                "- Draft a `Profile YAML Proposal` and `Profile Review Packet` before writing files.",
                "- Human review decides whether candidate rules become long-term profile source.",
                "",
            ]
        )
    else:
        lines.extend(
            [
                "## Temporary Injection Boundary",
                "",
                "- Use temporary injection for one-off generation constraints.",
                "- Do not promote temporary rules into tracked profile source without review.",
                "",
            ]
        )
    lines.extend(["Sources:"])
    for source in sources:
        lines.append(f"- `{source['path']}`")
    return "\n".join(lines).rstrip() + "\n"
