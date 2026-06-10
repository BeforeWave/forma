"""Forma CLI dispatcher.

`verify` wires through `forma_verifier`, the Python package that ships
organizationally inside Layer 1's meta skill source at
`source/skill-creator/scripts/forma_verifier/`. `explain` is a read-only
stdout surface for agent command routing plus canonical profile and injection
guidance.

"""

from __future__ import annotations

from pathlib import Path

import click
from forma import __version__
from forma.adapters import ADAPTER_TARGETS, build_creator
from forma.adopt import adopt_profile
from forma.creator import build_bundle
from forma.doctor import diagnose_artifact
from forma.drift import drift_artifact, drift_release_surface
from forma.explain import render_guidance
from forma.install import install_artifact
from forma.plugin_guidance import codex_plugin_install_hint
from forma.plugins import build_codex_plugin
from forma.runtime_assets import runtime_asset_path
from forma_verifier import verify as verify_bundle


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


class RawEpilogGroup(RawEpilogMixin, click.Group):
    """Click group that preserves command examples in epilog text."""


ROOT_HELP = """
Agents:

  Read the workflow command guide first:
    forma explain agent
    forma explain agent --target codex
    forma explain agent --target claude-code

Use create-bundle or create-plugin. The old forma create command is not supported.
"""


VERIFY_HELP = """
Next:

  If verification passes for a skill bundle, install it with:
    forma install --target codex|claude-code --scope user|project <path>

  If verification passes for a Codex plugin source, install it through Codex.
"""


DOCTOR_HELP = """
Next:

  Use this before handoff when you need to know what an artifact is, whether
  Forma can install it, and which install route is correct.
"""


DRIFT_HELP = """
Sources:

  Use --profile when an artifact should still match tracked profile source.
  Use --creator-source for creator bundles or no-injection creator output.
  Without a source, drift reports base-origin freshness only.
"""


CREATE_BUNDLE_HELP = """
Next:

  Verify before installing:
    forma verify <output-dir>

  Install verified local skill bundles with:
    forma install --target codex|claude-code --scope user|project <output-dir>
"""


CREATE_PLUGIN_HELP = """
Next:

  Verify the plugin source:
    forma verify <output-dir>

  Install Codex plugins through Codex marketplace/plugin UI, not forma install.
  Claude Code plugin output is unsupported.
"""


INSTALL_HELP = """
Boundaries:

  Install only verified local skills or skill bundles.
  Do not pass URLs.
  Do not pass Codex plugin sources; install plugins through Codex.
  Use --replace only when replacing existing installed artifacts is intended.
"""


BUILD_CREATOR_HELP = """
Next:

  Verify the generated creator skill:
    forma verify <output-dir>/<target>/forma-creator

  Install the verified creator for the target:
    forma install --target codex|claude-code --scope user|project <creator-path>
"""


EXPLAIN_HELP = """
Use this when an agent needs command-routing guidance, durable profile rules, or
temporary one-off workflow rules without reading Forma source files.
"""


EXPLAIN_AGENT_HELP = """
Next:

  Read this before choosing between creator, generic no-profile output, tracked
  profile generation, plugin output, profile adoption, drift, doctor, and install.
"""


EXPLAIN_PROFILE_HELP = """
Next:

  Combine this guidance with project facts to draft a tracked profile YAML.
  Then generate output with forma create-bundle or forma create-plugin.
"""


EXPLAIN_INJECTION_HELP = """
Next:

  Use this guidance inside forma-creator to classify one-off workflow rules.
  Temporary injection is not durable tracked profile source.
"""


PROFILE_ADOPT_HELP = """
Next:

  Generate from the adopted profile and compare with the source artifact before
  committing it as durable project profile source.
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


@main.command(cls=RawEpilogCommand, epilog=DOCTOR_HELP)
@click.option(
    "--json",
    "json_output",
    is_flag=True,
    help="Emit a machine-readable artifact diagnosis.",
)
@click.argument("path", type=click.Path(path_type=Path))
@click.pass_context
def doctor(ctx: click.Context, json_output: bool, path: Path) -> None:
    """Diagnose a generated Forma artifact at PATH."""
    report = diagnose_artifact(path)
    if json_output:
        click.echo(report.format_json())
    else:
        click.echo(report.format_human())
    if report.blockers:
        ctx.exit(1)


@main.command("drift", cls=RawEpilogCommand, epilog=DRIFT_HELP)
@click.option(
    "--profile",
    "profile_file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Tracked profile source used to regenerate the artifact.",
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
    help="Check Forma's committed examples/generated and dist release surface.",
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


@main.command("create-bundle", cls=RawEpilogCommand, epilog=CREATE_BUNDLE_HELP)
@click.option(
    "--profile",
    "profile_file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Tracked profile file that owns project workflow rules (default: generic Plan-First).",
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
def create_bundle_command(
    profile_file: Path,
    target_agent: str,
    output_dir: Path,
    methodology_dir: Path | None,
) -> None:
    """Compile project rules into a target-specific skill bundle."""
    try:
        resolved_profile = _resolve_profile_file(profile_file)
        manifest = build_bundle(
            profile_file=resolved_profile,
            target_agent=target_agent,
            output_dir=output_dir,
            methodology_dir=methodology_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"forma create-bundle: wrote workflow bundle: {output_dir}")
    click.echo(f"manifest: {manifest}")


@main.command("create-plugin", cls=RawEpilogCommand, epilog=CREATE_PLUGIN_HELP)
@click.option(
    "--profile",
    "profile_file",
    required=False,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Tracked profile file that owns project workflow rules (default: generic Plan-First).",
)
@click.option(
    "--target",
    "target_agent",
    required=True,
    type=click.Choice(ADAPTER_TARGETS),
    help="Plugin target for the generated workflow. Currently only codex is supported.",
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
def create_plugin_command(
    profile_file: Path | None,
    target_agent: str,
    output_dir: Path,
    methodology_dir: Path | None,
) -> None:
    """Compile project rules into a Codex plugin source."""
    if target_agent != "codex":
        raise click.ClickException("forma create-plugin currently supports only --target codex")
    try:
        plugin_json = build_codex_plugin(
            profile_file=_resolve_profile_file(profile_file),
            output_dir=output_dir,
            methodology_dir=methodology_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"forma create-plugin: wrote Codex plugin: {output_dir}")
    click.echo(f"plugin: {plugin_json}")
    click.echo("install hint:")
    click.echo(codex_plugin_install_hint(output_dir))


@main.command("install", cls=RawEpilogCommand, epilog=INSTALL_HELP)
@click.option(
    "--target",
    "target_agent",
    required=True,
    type=click.Choice(ADAPTER_TARGETS),
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


def _resolve_profile_file(profile_file: Path | None) -> Path:
    if profile_file is not None:
        return profile_file
    with runtime_asset_path("profiles", "default", "forma-plan-first.yaml") as path:
        return path


@main.command("build-creator", cls=RawEpilogCommand, epilog=BUILD_CREATOR_HELP)
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
    """Build target-specific creators that generate and verify workflow outputs."""
    try:
        output = build_creator(source_dir, output_dir, target_agent)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"forma build-creator: wrote creator bundle: {output}")


@main.group("profile", cls=RawEpilogGroup)
def profile_group() -> None:
    """Manage durable Forma profile source."""


@profile_group.command("adopt", cls=RawEpilogCommand, epilog=PROFILE_ADOPT_HELP)
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Directory to write the adopted profile package.",
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
    """Convert a same-origin creator artifact into tracked profile source."""
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
    click.echo(f"forma profile adopt: wrote profile: {result.profile_file}")
    click.echo(f"adoption report: {result.report_file}")


@main.group(cls=RawEpilogGroup, epilog=EXPLAIN_HELP)
def explain() -> None:
    """Print read-only Forma authoring guidance."""


@explain.command("agent", cls=RawEpilogCommand, epilog=EXPLAIN_AGENT_HELP)
@click.option(
    "--format",
    "output_format",
    default="markdown",
    type=click.Choice(("markdown", "json")),
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
    default="markdown",
    type=click.Choice(("markdown", "json")),
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
    """Explain durable profile authoring and task-rule placement."""
    try:
        click.echo(render_guidance("profile", output_format, target_agent), nl=False)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@explain.command("temporary-injection", cls=RawEpilogCommand, epilog=EXPLAIN_INJECTION_HELP)
@click.option(
    "--format",
    "output_format",
    default="markdown",
    type=click.Choice(("markdown", "json")),
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
