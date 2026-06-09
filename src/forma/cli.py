"""Forma CLI dispatcher.

`verify` wires through `forma_verifier`, the Python package that ships
organizationally inside Layer 1's meta skill source at
`source/skill-creator/scripts/forma_verifier/`. `explain` is a read-only
stdout surface that formats canonical guidance references instead of keeping a
second copy of profile and injection rules in CLI code.

"""

from __future__ import annotations

from pathlib import Path

import click
from forma.adapters import ADAPTER_TARGETS, build_creator
from forma.creator import build_bundle
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
Agent paths:

  Start from creator:
    forma build-creator --target codex --output <dir>
    forma install --target codex --scope project <dir>/codex/forma-creator

  Build a skill bundle from a reviewed profile:
    forma create-bundle --target codex --profile <profile.yaml> --output <dir>
    forma verify <dir>
    forma install --target codex --scope project <dir>

  Build a Codex plugin source:
    forma create-plugin --target codex --profile <profile.yaml> --output <dir>
    forma verify <dir>
    # Install plugins through Codex, not forma install.

  Ask for authoring guidance:
    forma explain profile --target codex
    forma explain temporary-injection --target codex

Use create-bundle or create-plugin. The old forma create command is not supported.
"""


VERIFY_HELP = """
Next:

  If verification passes for a skill bundle, install it with:
    forma install --target codex|claude-code --scope user|project <path>

  If verification passes for a Codex plugin source, install it through Codex.
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
Use this when an agent needs rules for drafting durable profiles or
temporary one-off workflow constraints without reading Forma source files.
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


@click.group(cls=RawEpilogGroup, invoke_without_command=True, epilog=ROOT_HELP)
@click.version_option()
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


@main.group(cls=RawEpilogGroup, epilog=EXPLAIN_HELP)
def explain() -> None:
    """Print read-only Forma authoring guidance."""


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
