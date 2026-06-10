"""Forma — compile project-specific agent workflows into skill bundles."""

from importlib.metadata import PackageNotFoundError, version


DISTRIBUTION_NAME = "beforewave-forma"


def _package_version() -> str:
    try:
        return version(DISTRIBUTION_NAME)
    except PackageNotFoundError:
        return "0+unknown"


__version__ = _package_version()
