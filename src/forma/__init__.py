"""Forma — compile project-specific agent workflows into skill bundles."""

from importlib.metadata import PackageNotFoundError, version


DISTRIBUTION_NAME = "forma-cli"
DISTRIBUTION_NAMES = (
    DISTRIBUTION_NAME,
    "beforewave-forma",
)


def _package_version() -> str:
    for distribution_name in DISTRIBUTION_NAMES:
        try:
            return version(distribution_name)
        except PackageNotFoundError:
            continue
    return "0+unknown"


__version__ = _package_version()
