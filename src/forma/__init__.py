"""Forma — build plan-first AI skill suites with a verified shape."""

from importlib.metadata import PackageNotFoundError, version


def _package_version() -> str:
    try:
        return version("forma")
    except PackageNotFoundError:
        return "0+unknown"


__version__ = _package_version()
