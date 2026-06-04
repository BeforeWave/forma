"""Forma CLI dispatcher.

`verify` is implemented in issue-three-layer-suite task `layer-1-and-verifier`. It wires
through `forma_verifier`, the Python package that ships organizationally
inside Layer 1's meta skill source at
`source/skill-creator/scripts/forma_verifier/`.

"""

from __future__ import annotations

from pathlib import Path

import click
from forma.adapters import ADAPTER_TARGETS, build_creator
from forma.creator import create_suite
from forma_verifier import verify as verify_suite


@click.group()
@click.version_option()
def main() -> None:
    """Forma — build plan-first AI skill suites with a verified shape."""


@main.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
def verify(path: Path) -> None:
    """Verify a plan-first skill suite at PATH."""
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
    help="Output directory for the generated suite.",
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
    """Compose methodology + resolved profile into a target-specific suite."""
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
    required=True,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Forma creator source directory.",
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
    source_dir: Path,
    output_dir: Path,
    target_agent: str,
) -> None:
    """Generate target-specific installable Forma creator skills."""
    try:
        output = build_creator(source_dir, output_dir, target_agent)
    except ValueError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(f"forma build-creator: wrote {output}")


if __name__ == "__main__":
    main()
