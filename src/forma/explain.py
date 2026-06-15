"""Read-only guidance surfaces for agent workflow and profile authoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from forma.creator.composer import StageSource, load_stage_sources
from forma.creator.manifest import methodology_dir_context
from forma.creator.profiles import KINDS
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
                path="source/agent-guide/references/profile-authoring-principles.md",
                title="Profile authoring principles",
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


def render_stage_guidance(
    stage: str,
    output_format: OutputFormat = "human",
    target_agent: str | None = None,
    methodology_dir: Path | None = None,
) -> str:
    """Render stage-specific methodology and profile-injection guidance."""
    if output_format not in ("human", "agent", "json"):
        raise ValueError("output_format must be human, agent, or json")
    if stage not in KINDS:
        allowed = ", ".join(KINDS)
        raise ValueError(f"unsupported stage {stage!r}; use one of: {allowed}")
    with methodology_dir_context(methodology_dir) as resolved_methodology_dir:
        stage_source = load_stage_sources(resolved_methodology_dir, (stage,))[stage]
        markdown = _render_stage_markdown(
            stage=stage,
            stage_source=stage_source,
            target_agent=target_agent,
        )
        report = ActionableReport(
            command=f"forma explain stage {stage}",
            subject=target_agent or "all-targets",
            status="ready",
            summary=f"Forma stage guidance is available for {stage}",
            sections=(
                ReportSection(
                    kind="guidance",
                    title=f"Forma Stage Guidance: {stage}",
                    payload=markdown,
                ),
                ReportSection(
                    kind="sources",
                    title="Sources",
                    payload={
                        "items": [
                            {
                                "path": f"source/methodology/stages/{stage}.md",
                                "title": f"{stage} stage methodology",
                            }
                        ]
                    },
                ),
            ),
            next_actions=(
                NextAction(
                    title="filter candidate profile rules",
                    description=(
                        "Omit rules that restate this base stage contract; keep "
                        "only project-specific durable adaptations or explicit "
                        "environment integrations."
                    ),
                ),
                NextAction(
                    title="update methodology only when needed",
                    description=(
                        "If the base stage contract is weak or missing, propose a "
                        "methodology change instead of duplicating the rule in a profile."
                    ),
                ),
            ),
            metadata={
                "topic": "stage",
                "stage": stage,
                "target": target_agent,
                "source": f"source/methodology/stages/{stage}.md",
                "markdown": markdown,
                "stage_contract": {
                    "description": stage_source.description,
                    "interaction_semantics": list(stage_source.interaction_lines),
                    "mode_check": list(stage_source.mode_check_lines),
                    "entry_gate": list(stage_source.entry_gate_lines),
                    "workflow": list(stage_source.workflow_lines),
                    "requirements": list(stage_source.adds),
                    "output": list(stage_source.output_lines),
                },
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
                title="load profile authoring guidance",
                command=f"forma explain profile --target {target}",
                description=(
                    "Use when no approved profile exists yet; the agent still "
                    "has to read repository facts and draft candidate rules."
                ),
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
                title="diagnose repository agent operability",
                command="forma doctor --format json <repo>",
                description=(
                    "Use when a repository needs facts, findings, Agent handoff, "
                    "and owner-decision routing before Forma init or remediation."
                ),
            ),
            NextAction(
                title="materialize deterministic repo workflow source",
                command="forma init --from-report <report> --apply <repo>",
                description=(
                    "Creates draft .forma workflow source and report-derived "
                    "handoff files; Agent remediation and owner confirmations still follow."
                ),
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
            "When the reusable install path is missing or incomplete, inspect configured "
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
            "Codex plugin install state belongs to Codex. When the reusable "
            "install path is missing or incomplete, inspect configured marketplaces as "
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
        "This is the agent-facing command guide for Forma CLI surfaces. Use it "
        "to choose between profile authoring, workflow generation, plugin "
        "output, optional creator output, profile adoption, drift, doctor, init, "
        "verify, and install before reading narrower command guidance.",
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
        "Start from this Agent Guide. When no approved profile exists or repo "
        "rules need to become durable Forma configuration, run "
        "`forma explain profile --target <target>` next to load the profile "
        "authoring contract. That command does not inspect the repository or "
        "produce a draft by itself.",
        "",
        "## Profile semantic check before writing",
        "",
        "Use the `forma explain profile` guidance while reading repository "
        "facts. The agent must produce source-backed candidate profile rules, "
        "group them by touched stage, and return both a `Profile YAML Proposal` "
        "and `Profile Review Packet` for human review. Treat that draft as "
        "candidate semantics, not as permission to write the profile.",
        "",
        "Doctor-ready operability is not the same as a project-ready profile. "
        "Before drafting profile rules, summarize what the repository is for, "
        "what it delivers, what makes changes safe and maintainable, and which "
        "durable maintenance semantics belong in workflow rules beyond doctor "
        "findings.",
        "",
        "After the candidate draft identifies touched stages and before writing "
        "profile files, run `forma explain stage <stage>` for every touched "
        "stage. Use the stage guide to compare each candidate rule with the "
        "base methodology contract.",
        "",
        "For each candidate rule, decide one of these outcomes and record it in "
        "the Profile Review Packet: keep in the profile at the narrowest target, "
        "omit because the base methodology already owns it, keep as temporary "
        "injection because it is generation-only, ask the user because the "
        "durability or owner is unclear, or propose a methodology change because "
        "the base stage contract is weak or missing.",
        "",
        "Do not use profile injection to restate a stage's base responsibility. "
        "For example, do not inject that reconcile is read-only or that rework "
        "does not implement code when those are already methodology contracts. "
        "Use profile `constraints`, `workflow_adds`, `output_adds`, and "
        "`resources` only for durable repository adaptations such as source "
        "boundaries, validation surfaces, handoff conventions, host capabilities, "
        "or project-owned adapters.",
        "",
        "Write profile files only after explicit user approval. Commit them "
        "only when the rules should be reused.",
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
        "bootstrap-incomplete, treat the reusable install path as incomplete, "
        "not as a normal manual build/install path. Before running "
        "hand-assembled build or install commands, ask the user whether to complete "
        "`reinstall-workflow.sh` with confirmed install facts and then run the "
        "workflow through that script. Only proceed with a one-off manual flow "
        "when the user explicitly says not to keep scripts for this profile or "
        "explicitly asks for a temporary one-time run.",
        "",
        "Reusable install setup goal: explore whatever local environment details "
        "are needed to make this profile build/install repeatable, then preserve "
        "that verified local process beside the profile. This is where target-specific "
        "marketplace paths, plugin selectors, output directories, remove/add "
        "steps, and installation checks belong. Do not make future agents "
        "rediscover those details from scratch.",
        "",
        "Required install facts before reusable success: artifact kind, target, "
        "plugin id when the artifact kind is plugin, marketplace name and "
        "marketplace source when the install route uses a marketplace, install "
        "selector, and visibility check.",
        "",
        "When the user approves reusable install setup, write one real script, not notes. "
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
        "open at runtime. Marketplace listing belongs only to install-path "
        "discovery or diagnostics before those facts are written.",
        "",
        "Script authoring rules: resolve the repository root and profile path "
        "relative to the script directory; keep output paths configurable with "
        "environment variables while preserving the just-used defaults; include "
        "`set -euo pipefail`; do not write placeholder commands; make scripts "
        "executable; and run the new script once before reporting reusable "
        "install setup success.",
        "",
        "Your final install report must include the profile-local reinstall "
        "state: reused existing script, completed and ran the script, user "
        "requested one-off manual flow, or blocked waiting for the install-script "
        "decision.",
        "",
        "## Diagnose repository agent-operability",
        "",
        "`forma doctor` checks whether a repository gives a new Agent "
        "enough structure to know what to read, what can change, how to "
        "validate, when to stop, and how to hand off findings. It is not a "
        "generated artifact verifier; Forma workflow source is project-rule "
        "management, not a core readiness prerequisite.",
        "",
        "```bash",
        "forma doctor --format json <repo> > <report>",
        "forma doctor --format agent <repo>",
        "```",
        "",
        "The doctor report is an investigation input, not the final user "
        "diagnosis. When the status is `needs-agent`, inspect the reported "
        "evidence and repository guidance, assign a disposition to every "
        "non-contract core finding, and classify it as confirmed, resolved, "
        "not applicable, blocked by unavailable evidence, or requiring an "
        "owner decision. Do not copy unresolved findings into the final answer "
        "and stop.",
        "",
        "Stop only when every finding has a disposition, an owner decision is "
        "required, required evidence is unavailable, or an unsafe blocker is "
        "present. Finish all agent-resolvable investigation before asking the "
        "owner.",
        "",
        "If the owner wants Forma workflow source after the diagnosis, preserve "
        "the JSON report and run:",
        "",
        "```bash",
        "forma init --from-report <report> --apply <repo>",
        "```",
        "",
        "`init --from-report` materializes deterministic `.forma` workflow "
        "source and Agent handoff files. It does not approve semantic rules or "
        "make the repo agent-friendly by itself; profile approval, build/verify, "
        "install target/scope, and commit remain separate owner confirmations.",
        "If doctor reports `ready`, treat that as operability readiness only; "
        "profile authoring still needs project purpose, maintenance semantics, "
        "validation model, risk model, and source/artifact boundaries.",
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
        "## Adopt a Forma-provenance creator artifact into a candidate profile package",
        "",
        "Use this only when the artifact carries Forma provenance metadata that "
        "matches the current creator baseline. "
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
        "- `doctor` diagnoses repository agent-operability and can feed "
        "`init --from-report`.",
        "- Generated artifact handoff should use `forma verify`, build command "
        "agent/json output, and the relevant install boundary.",
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
                "- Use this after `forma explain agent` routes the work to profile authoring.",
                "- Use profiles for durable, repeated project workflow rules.",
                "- This command explains how to extract candidate rules from project facts by workflow behavior.",
                "- The agent must group candidate rules by touched stage before proposing YAML.",
                "- Keep task-specific or one-off generation constraints out of the profile.",
                "- Draft a `Profile YAML Proposal` and `Profile Review Packet` before writing files.",
                "- Use `forma explain stage <stage>` to filter stage-specific rules against base methodology before writing profile files.",
                "- Do not inject rules that merely repeat the base stage contract; propose a methodology change when the base contract is weak.",
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


def _render_stage_markdown(
    stage: str,
    stage_source: StageSource,
    target_agent: str | None,
) -> str:
    lines = ["# Forma Stage Guidance", ""]
    if target_agent is not None:
        lines.extend([f"Target: `{target_agent}`", ""])
    lines.extend(
        [
            f"Stage: `{stage}`",
            f"Methodology source: `source/methodology/stages/{stage}.md`",
            "",
            "Use this after drafting candidate profile rules and before writing "
            "the profile file. The goal is to filter candidate rules against the "
            "base methodology contract for this stage.",
            "",
            "## Base Stage Contract",
            "",
            stage_source.description,
            "",
        ]
    )
    _append_stage_section(lines, "Interaction Semantics", stage_source.interaction_lines)
    _append_stage_section(lines, "Mode Check", stage_source.mode_check_lines)
    _append_stage_section(lines, "Entry Gate", stage_source.entry_gate_lines)
    _append_stage_section(lines, "Workflow", stage_source.workflow_lines)
    _append_stage_section(lines, "Requirements", stage_source.adds)
    _append_stage_section(lines, "Output", stage_source.output_lines)
    lines.extend(
        [
            "## Profile Injection Boundary",
            "",
            f"- Use `constraints.{stage}` only for durable project rules that adapt this stage to the owning repository.",
            f"- Use `workflow_adds.{stage}` only when the project adds an ordered workflow step, gate, handoff, or stop condition that belongs in this stage's execution path.",
            f"- Use `output_adds.{stage}` only when the project requires an additional final-response field for this stage.",
            f"- Use `resources.{stage}` only for project-owned references, scripts, or support files this stage must load.",
            f"- Use `validation_commands.{stage}` only for validation commands that are actually relevant to this stage.",
            "- Do not inject rules that merely restate the base stage contract above.",
            "- If the base methodology is weak, missing, or ambiguous, propose a methodology update instead of hiding the fix in a profile.",
            "- If the rule is one-off generation context, keep it in temporary injection rather than durable profile source.",
            "",
            "## Filtering Questions",
            "",
            "- Is this rule already covered by the base stage contract?",
            "- Is this rule durable for the owning repository, or only true for the current generation?",
            "- Does this rule change a stage stop condition, handoff, or output field?",
            "- Does this rule need a project-owned reference, script, or adapter?",
            "- Should this be a methodology improvement rather than a profile injection?",
        ]
    )
    if stage in {"hone", "mend"}:
        lines.extend(
            [
                "",
                "## Optional Stage Note",
                "",
                f"`{stage}` is an optional stage. A profile must enable it with `stages.{stage}.enabled: true` before `{stage}` constraints, workflow additions, output additions, or resources can affect generated output.",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def _append_stage_section(
    lines: list[str],
    title: str,
    items: tuple[str, ...],
) -> None:
    if not items:
        return
    lines.extend([f"### {title}", ""])
    for item in items:
        if item.startswith(("-", "```", "#", ">", "|", " ")):
            lines.append(item)
        else:
            lines.append(f"- {item}")
    lines.append("")
