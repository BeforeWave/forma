"""Runtime access to packaged Forma source assets."""

from __future__ import annotations

import tempfile
from contextlib import contextmanager
from importlib import resources
from pathlib import Path
from typing import Iterator

ASSET_PACKAGE = "forma.assets"
_MATERIALIZED_ASSETS: dict[tuple[str, ...], Path] = {}


@contextmanager
def runtime_asset_path(*relative_parts: str) -> Iterator[Path]:
    """Yield a filesystem path for a packaged asset or source-checkout fallback."""
    packaged = _packaged_asset(relative_parts)
    if packaged is not None:
        if isinstance(packaged, Path):
            yield packaged
            return
        key = tuple(relative_parts)
        target = _MATERIALIZED_ASSETS.get(key)
        if target is None or not target.exists():
            temp_dir = Path(tempfile.mkdtemp(prefix="forma-asset-"))
            target = temp_dir / Path(*relative_parts).name
            _copy_traversable(packaged, target)
            _MATERIALIZED_ASSETS[key] = target
        yield target
        return

    fallback = _checkout_asset(relative_parts)
    if fallback is not None:
        yield fallback
        return

    rel = "/".join(relative_parts)
    raise ValueError(
        f"could not locate Forma runtime asset {rel!r}; install a package that "
        "includes runtime assets or run from a Forma source checkout"
    )


def read_runtime_text(*relative_parts: str) -> str:
    """Read a packaged text asset, falling back to the source checkout."""
    with runtime_asset_path(*relative_parts) as path:
        return path.read_text(encoding="utf-8").strip()


def _packaged_asset(relative_parts: tuple[str, ...]):
    try:
        root = resources.files(ASSET_PACKAGE)
    except ModuleNotFoundError:
        return None
    target = root.joinpath(*relative_parts)
    if target.is_file() or target.is_dir():
        return target
    return None


def _checkout_asset(relative_parts: tuple[str, ...]) -> Path | None:
    rel = Path(*relative_parts)
    candidates = [Path.cwd().resolve(), Path(__file__).resolve()]
    for base in candidates:
        for parent in (base, *base.parents):
            candidate = parent / rel
            if candidate.exists():
                return candidate.resolve()
    return None


def _copy_traversable(source, target: Path) -> None:
    if source.is_file():
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(source.read_bytes())
        return
    target.mkdir(parents=True, exist_ok=True)
    for child in source.iterdir():
        _copy_traversable(child, target / child.name)
