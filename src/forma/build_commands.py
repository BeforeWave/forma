"""Command-domain helpers for Forma build CLI surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from forma.adapters import build_creator
from forma.creator import build_bundle
from forma.plugin_guidance import codex_plugin_install_hint
from forma.plugins import build_plugin
from forma.reports import ActionableReport, NextAction, ReportSection, render_report
from forma.runtime_assets import runtime_asset_path


@dataclass(frozen=True)
class ProfileWorkflowScriptStatus:
    profile_dir: Path
    script_name: str = "reinstall-workflow.sh"
    present: bool = False
    bootstrap_incomplete: bool = False

    @property
    def missing(self) -> tuple[str, ...]:
        return () if self.present else (self.script_name,)

    @property
    def reusable(self) -> bool:
        return self.present and not self.bootstrap_incomplete

    @property
    def state(self) -> str:
        if not self.present:
            return "missing"
        if self.bootstrap_incomplete:
            return "bootstrap-incomplete"
        return "reusable"

    def to_dict(self) -> dict[str, object]:
        return {
            "profile_dir": str(self.profile_dir),
            "script": self.script_name,
            "present": self.present,
            "state": self.state,
            "required_install_facts": list(REINSTALL_INSTALL_FACTS),
        }

    def format_human(self) -> str:
        lines = [
            "profile-local reinstall workflow:",
            f"  profile-dir: {self.profile_dir}",
            f"  {self.script_name}: {'present' if self.present else 'missing'}",
        ]

        if not self.reusable:
            lines.extend(
                [
                    "  next: settle install facts with the user, write them into "
                    "this profile-local reinstall script, and run the completed "
                    "script before reporting reusable reinstall success.",
                ]
            )
        else:
            lines.append(
                "  next: run the profile-local reinstall script from this directory for "
                "this reusable profile-backed build/install flow instead of "
                "hand-assembling commands."
            )
        return "\n".join(lines)


@dataclass(frozen=True)
class BuildBundleCommandResult:
    output_dir: Path
    manifest: Path
    profile_status: ProfileWorkflowScriptStatus | None
    profile_file: Path | None = None

    def to_report(self) -> ActionableReport:
        sections = [
            ReportSection(
                kind="produced-artifact",
                title="Produced Artifact",
                payload={
                    "artifact_kind": "skill-bundle",
                    "output_dir": str(self.output_dir),
                    "manifest": str(self.manifest),
                },
            )
        ]
        next_actions = [
            NextAction(
                title="verify generated bundle",
                command=f"forma verify {self.output_dir}",
                stop_condition="verification fails",
            ),
            NextAction(
                title="install verified local skill bundle",
                command=(
                    "forma install --target codex|claude-code|opencode "
                    f"--scope user|project {self.output_dir}"
                ),
                description="Use the target and scope requested by the user.",
            ),
        ]
        if self.profile_status is not None:
            sections.append(_profile_workflow_section(self.profile_status))
            next_actions = (
                _profile_workflow_actions(self.profile_status)
                + _profile_freshness_actions(self.output_dir, self.profile_file)
                + next_actions
            )
        return ActionableReport(
            command="forma build bundle",
            subject=str(self.output_dir),
            status="needs-agent",
            summary=f"wrote workflow bundle: {self.output_dir}",
            sections=tuple(sections),
            next_actions=tuple(next_actions),
        )

    def format_human(self) -> str:
        return render_report(self.to_report(), "human")


@dataclass(frozen=True)
class BuildPluginCommandResult:
    output_dir: Path
    target_agent: str
    plugin_json: Path
    profile_status: ProfileWorkflowScriptStatus | None
    profile_file: Path | None = None

    def to_report(self) -> ActionableReport:
        label = "Codex" if self.target_agent == "codex" else "Claude Code"
        sections = [
            ReportSection(
                kind="produced-artifact",
                title="Produced Artifact",
                payload={
                    "artifact_kind": f"{self.target_agent}-plugin",
                    "output_dir": str(self.output_dir),
                    "plugin_json": str(self.plugin_json),
                },
            )
        ]
        next_actions = [
            NextAction(
                title="verify generated plugin",
                command=f"forma verify {self.output_dir}",
                stop_condition="verification fails",
            )
        ]
        if self.profile_status is not None:
            sections.append(_profile_workflow_section(self.profile_status))
            next_actions = (
                _profile_workflow_actions(self.profile_status)
                + _profile_freshness_actions(self.output_dir, self.profile_file)
                + next_actions
            )
        if self.target_agent == "codex":
            sections.append(
                ReportSection(
                    kind="codex-plugin-handoff",
                    title="Codex Plugin Handoff",
                    payload=codex_plugin_install_hint(self.output_dir),
                )
            )
            next_actions.extend(
                [
                    NextAction(
                        title="confirm Codex plugin install facts",
                        description=(
                            "Settle plugin id, marketplace name, marketplace source, "
                            "install selector, and visibility check with the user. "
                            "Use marketplace listing only as bootstrap discovery or "
                            "diagnostics, not inside a stable reinstall script."
                        ),
                        stop_condition=(
                            "plugin id, marketplace, marketplace source, selector, "
                            "or visibility check is not confirmed"
                        ),
                        forbidden=(
                            "do not install Codex plugins with forma install",
                            "do not leave plugin id, marketplace, selector, or source refresh decisions open at stable reinstall runtime",
                        ),
                    ),
                    NextAction(
                        title="install through Codex with the confirmed selector",
                        command="codex plugin add <confirmed-plugin-id>@<confirmed-marketplace>",
                        description=(
                            "Generated plugin root is not a marketplace root; "
                            "Codex owns marketplace registration and enabled state."
                        ),
                    ),
                    NextAction(
                        title="start a new Codex thread",
                        description="Newly installed plugin skills are discovered in a new thread.",
                    ),
                ]
            )
        else:
            next_actions.append(
                NextAction(
                    title=f"install verified {label} plugin",
                    command=(
                        "forma install --target claude-code --scope user|project "
                        f"{self.output_dir}"
                    ),
                )
            )
        return ActionableReport(
            command="forma build plugin",
            subject=str(self.output_dir),
            status="needs-agent",
            summary=f"wrote {label} plugin: {self.output_dir}",
            sections=tuple(sections),
            next_actions=tuple(next_actions),
        )

    def format_human(self) -> str:
        return render_report(self.to_report(), "human")


@dataclass(frozen=True)
class BuildCreatorCommandResult:
    output: Path

    def format_human(self) -> str:
        return f"forma build creator: wrote creator bundle: {self.output}"


def run_build_bundle(
    *,
    profile_file: Path | None,
    target_agent: str,
    output_dir: Path,
    methodology_dir: Path | None,
) -> BuildBundleCommandResult:
    resolved_profile = resolve_profile_file(profile_file)
    manifest = build_bundle(
        profile_file=resolved_profile,
        target_agent=target_agent,
        output_dir=output_dir,
        methodology_dir=methodology_dir,
    )
    return BuildBundleCommandResult(
        output_dir=output_dir,
        manifest=manifest,
        profile_status=_profile_workflow_script_status(resolved_profile)
        if profile_file is not None
        else None,
        profile_file=resolved_profile if profile_file is not None else None,
    )


def run_build_plugin(
    *,
    profile_file: Path | None,
    target_agent: str,
    output_dir: Path,
    methodology_dir: Path | None,
) -> BuildPluginCommandResult:
    resolved_profile = resolve_profile_file(profile_file)
    plugin_json = build_plugin(
        profile_file=resolved_profile,
        output_dir=output_dir,
        target_agent=target_agent,
        methodology_dir=methodology_dir,
    )
    return BuildPluginCommandResult(
        output_dir=output_dir,
        target_agent=target_agent,
        plugin_json=plugin_json,
        profile_status=_profile_workflow_script_status(resolved_profile)
        if profile_file is not None
        else None,
        profile_file=resolved_profile if profile_file is not None else None,
    )


def run_build_creator(
    *,
    source_dir: Path | None,
    output_dir: Path,
    target_agent: str,
) -> BuildCreatorCommandResult:
    return BuildCreatorCommandResult(
        output=build_creator(source_dir, output_dir, target_agent)
    )


def resolve_profile_file(profile_file: Path | None) -> Path:
    if profile_file is not None:
        return profile_file
    with runtime_asset_path("profiles", "default", "forma-plan-first.yaml") as path:
        return path


def _profile_workflow_script_status(profile_file: Path) -> ProfileWorkflowScriptStatus:
    script_name = "reinstall-workflow.sh"
    profile_dir = profile_file.parent
    script_path = profile_dir / script_name
    present = script_path.is_file()
    bootstrap_incomplete = False
    if present:
        try:
            script_text = script_path.read_text(encoding="utf-8")
        except OSError:
            script_text = ""
        bootstrap_incomplete = "FORMA_REINSTALL_WORKFLOW_BOOTSTRAP_INCOMPLETE=1" in script_text
    return ProfileWorkflowScriptStatus(
        profile_dir=profile_dir,
        script_name=script_name,
        present=present,
        bootstrap_incomplete=bootstrap_incomplete,
    )


def _profile_workflow_section(status: ProfileWorkflowScriptStatus) -> ReportSection:
    return ReportSection(
        kind="profile-local-reinstall-workflow",
        title="Profile-Local Reinstall Workflow",
        payload=status.to_dict(),
    )


def _profile_workflow_actions(
    status: ProfileWorkflowScriptStatus,
) -> list[NextAction]:
    if status.reusable:
        return [
            NextAction(
                title="run profile-local reinstall workflow",
                command=f"cd {status.profile_dir} && ./{status.script_name}",
                description=(
                    "Use this fixed-fact profile-backed build/install flow before "
                    "assembling commands manually. The script should already encode "
                    "artifact kind, target, install route, and visibility check."
                ),
            )
        ]
    return [
        NextAction(
            title="settle install facts and complete profile-local reinstall workflow",
            description=(
                "Continue with the user after build/install exploration to confirm "
                "artifact kind, target, plugin id when relevant, marketplace name, "
                "marketplace source, install selector, and visibility check. Write "
                "the confirmed facts into reinstall-workflow.sh beside the profile "
                "and run that script before reporting reusable reinstall success. "
                "A one-off manual flow is allowed only when explicitly requested."
            ),
            stop_condition=(
                "install facts are not confirmed or reinstall-workflow.sh is "
                "missing/bootstrap-incomplete"
            ),
            forbidden=(
                "do not report the manual flow as reusable",
                "do not leave plugin id, marketplace, selector, or source refresh decisions open at stable reinstall runtime",
                "do not put Codex marketplace listing in the stable reinstall script",
            ),
        )
    ]


def _profile_freshness_actions(
    output_dir: Path,
    profile_file: Path | None,
) -> list[NextAction]:
    profile_arg = str(profile_file) if profile_file is not None else "<profile.yaml>"
    return [
        NextAction(
            title="drift generated output against profile",
            command=f"forma drift {output_dir} --profile {profile_arg}",
            description=(
                "Run this freshness gate before any intentional postprocess. "
                "If postprocess is required, run it after drift and use "
                "forma verify as the final gate."
            ),
            stop_condition="drift check reports stale output",
        )
    ]


REINSTALL_INSTALL_FACTS = (
    "artifact kind",
    "target",
    "plugin id when artifact kind is plugin",
    "marketplace name when target install uses a marketplace",
    "marketplace source when target install uses a marketplace",
    "install selector",
    "visibility check",
)
