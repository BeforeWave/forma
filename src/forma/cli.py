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
from forma.creator import create_suite
from forma.explain import render_guidance
from forma_verifier import verify as verify_suite


@click.group()
@click.version_option()
def main() -> None:
    """Forma — compile project-specific agent workflows into skill bundles."""


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def verify(path: Path) -> None:
    """Verify a generated Forma workflow bundle at PATH."""
    report = verify_suite(path)
    click.echo(report.format_human())
    if not report.passed:
        raise click.ClickException("verification failed")


@main.command()
@click.option(
    "--profile",
    "profile_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Top-level bundle profile file.",
)
@click.option(
    "--target",
    "target_agent",
    required=True,
    type=click.Choice(ADAPTER_TARGETS),
    help="Agent target to emit.",
)
@click.option(
    "--output",
    "output_dir",
    required=True,
    type=click.Path(file_okay=False, path_type=Path),
    help="Output directory for the generated workflow bundle.",
)
@click.option(
    "--methodology",
    "methodology_dir",
    required=False,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Methodology source path override (default: auto-detect).",
)
def create(
    profile_file: Path,
    target_agent: str,
    output_dir: Path,
    methodology_dir: Path | None,
) -> None:
    """Compile a resolved profile into a target-specific workflow bundle."""
    try:
        manifest = create_suite(
            profile_file=profile_file,
            target_agent=target_agent,
            output_dir=output_dir,
            methodology_dir=methodology_dir,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"forma create: wrote {output_dir}")
    click.echo(f"manifest: {manifest}")


@main.command("build-creator")
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
    help="Agent target to emit.",
)
def build_creator_command(
    source_dir: Path | None,
    output_dir: Path,
    target_agent: str,
) -> None:
    """Build target-specific installable Forma creator bundles."""
    try:
        output = build_creator(source_dir, output_dir, target_agent)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"forma build-creator: wrote {output}")


@main.group()
def explain() -> None:
    """Print read-only Forma authoring guidance."""


@explain.command("profile")
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
    """Explain durable profile authoring and constraint placement."""
    try:
        click.echo(render_guidance("profile", output_format, target_agent), nl=False)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


@explain.command("temporary-injection")
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
    """Explain temporary injection classification and output rules."""
    try:
        click.echo(
            render_guidance("temporary-injection", output_format, target_agent),
            nl=False,
        )
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc


if __name__ == "__main__":
    main()
