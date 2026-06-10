#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import tempfile
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_CONFIG = ROOT / "packaging" / "pypi" / "packages.toml"
PYPROJECT = ROOT / "pyproject.toml"


@dataclass(frozen=True)
class PypiPackage:
    name: str
    readme: str


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one PyPI distribution package from the Forma source tree.",
    )
    parser.add_argument(
        "--package",
        dest="package_name",
        help="Distribution package name from packaging/pypi/packages.toml.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Directory where wheel and sdist files should be written.",
    )
    parser.add_argument(
        "--wheel",
        action="store_true",
        help="Build only a wheel. Defaults to wheel and sdist when no format is set.",
    )
    parser.add_argument(
        "--sdist",
        action="store_true",
        help="Build only an sdist. Defaults to wheel and sdist when no format is set.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the output directory before building.",
    )
    parser.add_argument(
        "--list-packages",
        action="store_true",
        help="Print configured package names and exit.",
    )
    parser.add_argument(
        "--dist-prefix",
        metavar="NAME",
        help="Print the normalized distribution filename prefix for NAME and exit.",
    )
    args = parser.parse_args()

    packages = _load_packages()

    if args.list_packages:
        for package in packages:
            print(package.name)
        return 0

    if args.dist_prefix:
        print(dist_prefix(args.dist_prefix))
        return 0

    if not args.package_name:
        parser.error("--package is required unless --list-packages is used")
    if not args.out_dir:
        parser.error("--out-dir is required unless --list-packages is used")

    package = _find_package(packages, args.package_name)
    formats = _build_formats(args.wheel, args.sdist)
    build_package(package, args.out_dir, formats, clear=args.clear)
    return 0


def dist_prefix(package_name: str) -> str:
    return re.sub(r"[-_.]+", "_", package_name).lower()


def build_package(
    package: PypiPackage,
    out_dir: Path,
    formats: list[str],
    *,
    clear: bool,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=f"forma-pypi-{dist_prefix(package.name)}-",
    ) as tmp:
        build_root = Path(tmp) / "source"
        _copy_build_source(build_root)
        _write_package_pyproject(build_root, package)
        cmd = ["uv", "build", "--out-dir", str(out_dir)]
        if clear:
            cmd.append("--clear")
        cmd.extend(formats)
        subprocess.run(cmd, cwd=build_root, check=True)


def _load_packages() -> list[PypiPackage]:
    data = tomllib.loads(PACKAGE_CONFIG.read_text(encoding="utf-8"))
    packages = [
        PypiPackage(
            name=str(entry["name"]),
            readme=str(entry.get("readme", "README.md")),
        )
        for entry in data.get("packages", [])
    ]
    if not packages:
        raise SystemExit(f"no packages configured in {PACKAGE_CONFIG}")
    return packages


def _find_package(packages: list[PypiPackage], package_name: str) -> PypiPackage:
    for package in packages:
        if package.name == package_name:
            return package
    valid = ", ".join(package.name for package in packages)
    raise SystemExit(f"unknown package {package_name!r}; expected one of: {valid}")


def _build_formats(wheel: bool, sdist: bool) -> list[str]:
    if not wheel and not sdist:
        return []
    formats: list[str] = []
    if wheel:
        formats.append("--wheel")
    if sdist:
        formats.append("--sdist")
    return formats


def _copy_build_source(build_root: Path) -> None:
    build_root.mkdir(parents=True)
    for file_name in (
        "pyproject.toml",
        "setup.py",
        "MANIFEST.in",
        "README.md",
        "LICENSE",
        "NOTICE",
    ):
        shutil.copy2(ROOT / file_name, build_root / file_name)
    for directory in ("src", "source", "profiles", "packaging"):
        shutil.copytree(
            ROOT / directory,
            build_root / directory,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache"),
        )


def _write_package_pyproject(build_root: Path, package: PypiPackage) -> None:
    pyproject = PYPROJECT.read_text(encoding="utf-8")
    pyproject = _replace_project_string(pyproject, "name", package.name)
    pyproject = _replace_project_string(pyproject, "readme", package.readme)
    (build_root / "pyproject.toml").write_text(pyproject, encoding="utf-8")


def _replace_project_string(pyproject: str, key: str, value: str) -> str:
    lines = pyproject.splitlines()
    in_project = False
    replaced = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == "[project]":
            in_project = True
            continue
        if in_project and stripped.startswith("[") and stripped.endswith("]"):
            break
        if in_project and re.match(rf"{re.escape(key)}\s*=", stripped):
            lines[index] = f"{key} = {json.dumps(value)}"
            replaced = True
            break
    if not replaced:
        raise ValueError(f"could not replace [project].{key}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    sys.exit(main())
