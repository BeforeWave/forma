"""Forma CLI dispatcher.

`verify` wires through `forma_verifier`, the Python package that ships in
Forma's bundled verifier source. `explain` is a read-only stdout surface for
agent command routing plus canonical profile and injection guidance.

"""

from __future__ import annotations

from pathlib import Path

import click
from forma import __version__
from forma.adapters import ADAPTER_TARGETS
from forma.adopt import adopt_profile
from forma.build_commands import (
    run_build_bundle,
    run_build_creator,
    run_build_plugin,
)
from forma.drift import drift_artifact, drift_release_surface
from forma.creator.profiles import KINDS
from forma.explain import render_guidance, render_stage_guidance
from forma.init_remediation import plan_init
from forma.install import INSTALL_TARGETS, install_artifact
from forma.repo_doctor import diagnose_repo
from forma.reports import REPORT_FORMATS, ReportFormat, render_report
from forma_verifier import verify as verify_bundle

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
PLUGIN_TARGETS = ("codex", "claude-code")


class RawEpilogMixin:
    """Write Click epilog text without paragraph reflow."""

    epilog: str | None

    def format_epilog(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        if self.epilog:
            formatter.write_paragraph()
            formatter.write(self.epilog.strip("\n"))
            formatter.write("\n")


class RawEpilogCommand(RawEpilogMixin, click.Command):
    """Click command that preserves command examples in epilog text."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        context_settings = dict(CONTEXT_SETTINGS)
        context_settings.update(
            kwargs.pop("context_settings", None) or {}  # type: ignore[arg-type]
        )
        kwargs["context_settings"] = context_settings
        super().__init__(*args, **kwargs)


class RawEpilogGroup(RawEpilogMixin, click.Group):
    """Click group that preserves command examples in epilog text."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        context_settings = dict(CONTEXT_SETTINGS)
        context_settings.update(
            kwargs.pop("context_settings", None) or {}  # type: ignore[arg-type]
        )
        kwargs["context_settings"] = context_settings
        super().__init__(*args, **kwargs)


ROOT_HELP = """
Agents:

  Start with the workflow command guide:
    forma explain agent
    forma explain agent --target codex
    forma explain agent --target claude-code
    forma explain agent --target opencode

  For repository diagnosis or "is this project ready for agents":
    forma doctor --format agent <repo>
    forma doctor --format json <repo>
"""


VERIFY_HELP = """
Next:

  If verification passes for a skill bundle or Claude Code plugin source, install it with:
    forma install --target codex|claude-code|opencode --scope user|project <path>

  If verification passes for a Codex plugin source, install it through Codex.
"""


DOCTOR_HELP = """
Next:

  Agents should read the Forma command guide before interpreting findings:
    forma explain agent
    forma explain agent --target codex|claude-code|opencode

  Then use --format agent or --format json. A needs-agent result requires
  follow-up investigation and finding dispositions; it is not a final
  diagnosis to return unchanged.
"""


DRIFT_HELP = """
Sources:

  Use --profile when an artifact should still match profile source.
  Use --creator-source for creator bundles or no-injection creator output.
  Without a source, drift reports base-origin freshness only.
"""


PROFILE_LOCAL_WORKFLOW_HELP = """
Profile-local reinstall workflow:

  For profile-backed build/install work, inspect the profile directory before
  composing commands. If reinstall-workflow.sh exists there, run the script
  from that directory instead of rebuilding the command chain.

  If the script is missing, treat the reusable install path as incomplete.
  Before hand-assembling build/install commands, ask whether to create the
  missing profile-local reinstall script and then run the workflow through it.
  Only use a one-off manual flow when the user explicitly asks not to keep
  scripts for this profile or explicitly requests a temporary one-time run.

  A completed reinstall script should cover generation, drift when
  profile-backed, verify, the local install route, marketplace or install-target
  refresh, and the final visibility check.
"""


BUILD_HELP = PROFILE_LOCAL_WORKFLOW_HELP


BUILD_BUNDLE_HELP = """
Next:

  Verify before installing:
    forma verify <output-dir>

  Install verified local skill bundles with:
    forma install --target codex|claude-code|opencode --scope user|project <output-dir>
""" + PROFILE_LOCAL_WORKFLOW_HELP


BUILD_PLUGIN_HELP = """
Next:

  Verify the plugin source:
    forma verify <output-dir>

  For Codex plugins, list marketplaces, ask the user which marketplace to use
  or whether to create/register a new one, then install with:
    codex plugin add <plugin-id>@<marketplace-name>

  If Codex CLI output or marketplace behavior differs, consult current Codex
  plugin docs or `codex plugin marketplace --help`.

  Do not install Codex plugins with forma install.
  Install Claude Code plugin roots with forma install --target claude-code.
""" + PROFILE_LOCAL_WORKFLOW_HELP


INSTALL_HELP = """
Boundaries:

  Install only verified local skills, skill bundles, or Claude Code plugin roots.
  Do not pass URLs.
  Do not pass Codex plugin sources; install plugins through Codex.
  Use --replace only when replacing existing installed artifacts is intended.
"""


INIT_HELP = """
Behavior:

  Default mode is a dry run. Use --apply to create deterministic workflow source files.
  Generated profile source is draft project source and still needs human review.
"""


BUILD_CREATOR_HELP = """
Optional path:

  Use this when a user specifically wants an on-the-spot creator run instead
  of handling a profile file first.

Next:

  Verify the generated creator skill:
    forma verify <output-dir>/<target>/forma-creator

  Install the verified creator for the target:
    forma install --target codex|claude-code|opencode --scope user|project <creator-path>
"""


EXPLAIN_HELP = """
Use this when an agent needs command-routing guidance, profile authoring rules,
stage methodology boundaries, or temporary one-off workflow rules without
reading Forma source files.
"""


EXPLAIN_AGENT_HELP = """
Next:

  Read this as the read-only command-routing guide for agents using Forma before
  choosing between profile authoring, workflow generation, plugin output,
  optional creator output, profile adoption, drift, doctor, init, verify, and install.
  It does not inspect a repository, create profile drafts, build artifacts, or
  install workflows.
  If no approved profile exists yet, this guide routes the agent to
  forma explain profile before repo-specific profile drafting.
"""


EXPLAIN_PROFILE_HELP = """
Next:

  Use this only after forma explain agent routes the work to profile authoring.
  This command explains how to combine project facts into source-backed
  candidate rules, group them by touched stage, then return a Profile YAML
  Proposal and Profile Review Packet. Write profile files only after user approval.
  Use forma explain stage <stage> before placing stage-specific rules.
  Then generate output with forma build bundle or forma build plugin.
"""


EXPLAIN_STAGE_HELP = """
Next:

  Use this after drafting candidate profile rules and before writing profile
  files. Omit rules that restate the base stage contract. If the base stage
  contract is weak, propose a methodology change instead of hiding the fix in a
  profile.
"""


EXPLAIN_INJECTION_HELP = """
Next:

  Use this guidance inside forma-creator to classify one-off workflow rules.
  Temporary injection is not an approved profile source.
"""


PROFILE_ADOPT_HELP = """
Next:

  Generate from the candidate profile package and compare with the source
  artifact. Treat the profile as approved project source only after human review
  and explicit promotion.
"""


@click.group(cls=RawEpilogGroup, invoke_without_command=True, epilog=ROOT_HELP)
@click.version_option(version=__version__, prog_name="forma")
@click.pass_context
def main(ctx: click.Context) -> None:
    """Forma — compile project rules into task-level agent workflows."""
    if ctx.invoked_subcommand is None:
        click.echo(ctx.get_help())


@main.command(cls=RawEpilogCommand, epilog=VERIFY_HELP)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit a machine-readable verification report.",
)
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.pass_context
def verify(ctx: click.Context, json_output: bool, path: Path) -> None:
    """Verify a generated Forma workflow output at PATH."""
    report = verify_bundle(path)
    if json_output:
        click.echo(report.format_json())
        if not report.passed:
            ctx.exit(1)
        return
    click.echo(report.format_human())
    if not report.passed:
        raise click.ClickException("verification failed")


@main.command(
    "doctor",
    cls=RawEpilogCommand,
    epilog=DOCTOR_HELP,
)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.pass_context
def doctor(
    ctx: click.Context,
    output_format: ReportFormat,
    path: Path | None,
) -> None:
    """Diagnose repository agent operability."""
    report = diagnose_repo(path or Path.cwd())
    click.echo(report.render(output_format))
    if report.status == "unsafe":
        ctx.exit(1)


@main.command("drift", cls=RawEpilogCommand, epilog=DRIFT_HELP)
@click.option(
    "--profile",
    "profile_file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Profile source used to regenerate the artifact.",
)
@click.option(
    "--creator-source",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Creator source used to regenerate creator artifacts.",
)
@click.option(
    "--release-surface",
    is_flag=True,
    help="Check Forma's committed dist release surface.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit a machine-readable drift report.",
)
@click.argument(
    "artifact_path",
    required=False,
    type=click.Path(exists=True, path_type=Path),
)
@click.pass_context
def drift_command(
    ctx: click.Context,
    profile_file: Path | None,
    creator_source: Path | None,
    release_surface: bool,
    json_output: bool,
    artifact_path: Path | None,
) -> None:
    """Check whether generated Forma artifacts are fresh."""
    if release_surface and artifact_path is not None:
        raise click.ClickException("--release-surface does not accept an artifact path")
    if release_surface and (profile_file is not None or creator_source is not None):
        raise click.ClickException("--release-surface uses Forma's fixed source map")
    if not release_surface and artifact_path is None:
        raise click.ClickException("provide an artifact path or --release-surface")
    try:
        report = (
            drift_release_surface(Path.cwd())
            if release_surface
            else drift_artifact(
                artifact_path=artifact_path or Path(),
                profile_file=profile_file,
                creator_source=creator_source,
            )
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(report.format_json())
    else:
        click.echo(report.format_human())
    if report.status == "invalid":
        ctx.exit(1)


@main.group("build", cls=RawEpilogGroup, epilog=BUILD_HELP)
def build_group() -> None:
    """Build Forma workflow artifacts from profile or creator source."""


@build_group.command("bundle", cls=RawEpilogCommand, epilog=BUILD_BUNDLE_HELP)
@click.option(
    "--profile",
    "profile_file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Profile file describing project workflow rules (default: generic Plan-First).",
)
@click.option(
    "--target",
    "target_agent",
    required=True,
    type=click.Choice(ADAPTER_TARGETS),
    help="Agent target for the generated workflow.",
)
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to write the generated workflow bundle.",
)
@click.option(
    "--methodology",
    "methodology_dir",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Methodology source path override (default: auto-detect).",
)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
def build_bundle_command(
    profile_file: Path | None,
    target_agent: str,
    output_dir: Path,
    methodology_dir: Path | None,
    output_format: ReportFormat,
) -> None:
    """Compile project rules into a target-specific skill bundle."""
    try:
        result = run_build_bundle(
            profile_file=profile_file,
            target_agent=target_agent,
            output_dir=output_dir,
            methodology_dir=methodology_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(render_report(result.to_report(), output_format))


@build_group.command("plugin", cls=RawEpilogCommand, epilog=BUILD_PLUGIN_HELP)
@click.option(
    "--profile",
    "profile_file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Profile file describing project workflow rules (default: generic Plan-First).",
)
@click.option(
    "--target",
    "target_agent",
    required=True,
    type=click.Choice(PLUGIN_TARGETS),
    help="Plugin target for the generated workflow.",
)
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to write the generated plugin.",
)
@click.option(
    "--methodology",
    "methodology_dir",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Methodology source path override (default: auto-detect).",
)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
def build_plugin_command(
    profile_file: Path | None,
    target_agent: str,
    output_dir: Path,
    methodology_dir: Path | None,
    output_format: ReportFormat,
) -> None:
    """Compile project rules into a target-specific plugin source."""
    try:
        result = run_build_plugin(
            profile_file=profile_file,
            output_dir=output_dir,
            target_agent=target_agent,
            methodology_dir=methodology_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(render_report(result.to_report(), output_format))


@main.command("install", cls=RawEpilogCommand, epilog=INSTALL_HELP)
@click.option(
    "--target",
    "target_agent",
    required=True,
    type=click.Choice(INSTALL_TARGETS),
    help="Agent target to install into.",
)
@click.option(
    "--scope",
    "scope",
    required=True,
    type=click.Choice(("user", "project")),
    help="Install into the user or current project scope.",
)
@click.option(
    "--replace",
    is_flag=True,
    help="Replace existing installed artifacts.",
)
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def install_command(
    target_agent: str,
    scope: str,
    replace: bool,
    path: Path,
) -> None:
    """Install a verified local Forma skill or skill bundle."""
    try:
        result = install_artifact(
            source=path,
            target_agent=target_agent,  # type: ignore[arg-type]
            scope=scope,  # type: ignore[arg-type]
            replace=replace,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"forma install: installed {result.artifact_kind}")
    for installed_path in result.installed_paths:
        click.echo(str(installed_path))


@main.command("init", cls=RawEpilogCommand, epilog=INIT_HELP)
@click.option(
    "--apply",
    "apply_changes",
    is_flag=True,
    help="Create missing deterministic workflow source files instead of only planning.",
)
@click.option(
    "--profile-dir",
    required=False,
    type=click.Path(file_okay=False, path_type=Path),
    help="Repo-local profile directory (default: .forma under PATH).",
)
@click.option(
    "--from-report",
    "from_report",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Repo doctor JSON report to materialize deterministic workflow source from.",
)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
@click.argument(
    "path",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
@click.pass_context
def init_command(
    ctx: click.Context,
    apply_changes: bool,
    profile_dir: Path | None,
    from_report: Path | None,
    output_format: ReportFormat,
    path: Path | None,
) -> None:
    """Plan or apply deterministic Forma repository initialization."""
    report = plan_init(
        root=path or Path.cwd(),
        profile_dir=profile_dir,
        apply=apply_changes,
        from_report=from_report,
    )
    click.echo(render_report(report, output_format))
    if report.status == "unsafe":
        ctx.exit(1)


@build_group.command("creator", cls=RawEpilogCommand, epilog=BUILD_CREATOR_HELP)
@click.option(
    "--source",
    "source_dir",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Forma creator source override (default: packaged runtime assets).",
)
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Output root for generated target-specific creator bundles.",
)
@click.option(
    "--target",
    "target_agent",
    required=True,
    type=click.Choice(ADAPTER_TARGETS),
    help="Agent target for the generated creator.",
)
def build_creator_command(
    source_dir: Path | None,
    output_dir: Path,
    target_agent: str,
) -> None:
    """Build optional target-specific creators for on-the-spot workflow output."""
    try:
        result = run_build_creator(
            source_dir=source_dir,
            output_dir=output_dir,
            target_agent=target_agent,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(result.format_human())


@main.group("profile", cls=RawEpilogGroup)
def profile_group() -> None:
    """Manage Forma profile utilities and candidate adoption."""


@profile_group.command("adopt", cls=RawEpilogCommand, epilog=PROFILE_ADOPT_HELP)
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to write the candidate profile package.",
)
@click.option(
    "--profile-id",
    required=False,
    help="Profile id to write into profile.yaml.",
)
@click.option(
    "--replace",
    is_flag=True,
    help="Replace an existing output directory.",
)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit the machine-readable adoption report.",
)
@click.argument("artifact_path", type=click.Path(exists=True, path_type=Path))
def profile_adopt_command(
    artifact_path: Path,
    output_dir: Path,
    profile_id: str | None,
    replace: bool,
    json_output: bool,
) -> None:
    """Convert a Forma-provenance creator artifact into a candidate profile package."""
    try:
        result = adopt_profile(
            artifact_path=artifact_path,
            output_dir=output_dir,
            profile_id=profile_id,
            replace=replace,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    if json_output:
        click.echo(result.report_file.read_text(encoding="utf-8"), nl=False)
        return
    click.echo(f"forma profile adopt: wrote candidate profile: {result.profile_file}")
    click.echo(f"adoption report: {result.report_file}")


@main.group(cls=RawEpilogGroup, epilog=EXPLAIN_HELP)
def explain() -> None:
    """Print read-only Forma authoring guidance."""


@explain.command("agent", cls=RawEpilogCommand, epilog=EXPLAIN_AGENT_HELP)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--target",
    "target_agent",
    required=False,
    type=click.Choice(ADAPTER_TARGETS),
    help="Optional agent target context.",
)
def explain_agent(output_format: str, target_agent: str | None) -> None:
    """Explain the agent command path for workflow generation and maintenance."""
    try:
        click.echo(render_guidance("agent", output_format, target_agent), nl=False)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@explain.command("profile", cls=RawEpilogCommand, epilog=EXPLAIN_PROFILE_HELP)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--target",
    "target_agent",
    required=False,
    type=click.Choice(ADAPTER_TARGETS),
    help="Optional agent target context.",
)
def explain_profile(output_format: str, target_agent: str | None) -> None:
    """Explain profile authoring and task-rule placement."""
    try:
        click.echo(render_guidance("profile", output_format, target_agent), nl=False)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@explain.command("stage", cls=RawEpilogCommand, epilog=EXPLAIN_STAGE_HELP)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--target",
    "target_agent",
    required=False,
    type=click.Choice(ADAPTER_TARGETS),
    help="Optional agent target context.",
)
@click.argument("stage", type=click.Choice(KINDS))
def explain_stage(
    output_format: str,
    target_agent: str | None,
    stage: str,
) -> None:
    """Explain one stage's base methodology and profile injection boundary."""
    try:
        click.echo(
            render_stage_guidance(stage, output_format, target_agent),
            nl=False,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@explain.command("temporary-injection", cls=RawEpilogCommand, epilog=EXPLAIN_INJECTION_HELP)
@click.option(
    "--format",
    "output_format",
    default="human",
    type=click.Choice(REPORT_FORMATS),
    show_default=True,
    help="Output format.",
)
@click.option(
    "--target",
    "target_agent",
    required=False,
    type=click.Choice(ADAPTER_TARGETS),
    help="Optional agent target context.",
)
def explain_temporary_injection(
    output_format: str,
    target_agent: str | None,
) -> None:
    """Explain temporary injection classification for one-off workflow rules."""
    try:
        click.echo(
            render_guidance("temporary-injection", output_format, target_agent),
            nl=False,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
