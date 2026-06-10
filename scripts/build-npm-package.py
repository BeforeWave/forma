#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_CONFIG = ROOT / "packaging" / "npm" / "packages.toml"
PYPROJECT = ROOT / "pyproject.toml"
LAUNCHER_ROOT = ROOT / "npm" / "launcher"


@dataclass(frozen=True)
class NpmPackage:
    name: str
    description: str
    readme: str
    repository_directory: str
    bin: dict[str, str]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Build one npm package from the shared Forma npm launcher.",
    )
    parser.add_argument(
        "--package",
        dest="package_name",
        help="npm package name from packaging/npm/packages.toml.",
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        help="Directory where package source should be written.",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear the output directory before writing package source.",
    )
    parser.add_argument(
        "--list-packages",
        action="store_true",
        help="Print configured package names and exit.",
    )
    args = parser.parse_args()

    packages = _load_packages()

    if args.list_packages:
        for package in packages:
            print(package.name)
        return 0

    if not args.package_name:
        parser.error("--package is required unless --list-packages is used")
    if not args.out_dir:
        parser.error("--out-dir is required unless --list-packages is used")

    package = _find_package(packages, args.package_name)
    build_package(package, args.out_dir, clear=args.clear)
    return 0


def build_package(package: NpmPackage, out_dir: Path, *, clear: bool) -> None:
    if clear and out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        LAUNCHER_ROOT / "bin",
        out_dir / "bin",
        dirs_exist_ok=True,
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copy2(ROOT / package.readme, out_dir / "README.md")
    (out_dir / "package.json").write_text(
        json.dumps(_package_json(package), indent=2) + "\n",
        encoding="utf-8",
    )


def _package_json(package: NpmPackage) -> dict[str, object]:
    version = _project_version()
    return {
        "name": package.name,
        "version": version,
        "description": package.description,
        "license": "Apache-2.0",
        "homepage": "https://github.com/BeforeWave/forma#readme",
        "repository": {
            "type": "git",
            "url": "git+https://github.com/BeforeWave/forma.git",
            "directory": package.repository_directory,
        },
        "bugs": {
            "url": "https://github.com/BeforeWave/forma/issues",
        },
        "bin": package.bin,
        "files": [
            "bin/",
            "README.md",
        ],
        "scripts": {
            "smoke": f"node ./{next(iter(package.bin.values()))}",
            "pack:dry-run": "npm pack --dry-run",
        },
        "publishConfig": {
            "access": "public",
        },
    }


def _project_version() -> str:
    project = tomllib.loads(PYPROJECT.read_text(encoding="utf-8"))["project"]
    return str(project["version"])


def _load_packages() -> list[NpmPackage]:
    data = tomllib.loads(PACKAGE_CONFIG.read_text(encoding="utf-8"))
    packages = [
        NpmPackage(
            name=str(entry["name"]),
            description=str(entry["description"]),
            readme=str(entry["readme"]),
            repository_directory=str(entry["repository_directory"]),
            bin={str(key): str(value) for key, value in entry["bin"].items()},
        )
        for entry in data.get("packages", [])
    ]
    if not packages:
        raise SystemExit(f"no packages configured in {PACKAGE_CONFIG}")
    return packages


def _find_package(packages: list[NpmPackage], package_name: str) -> NpmPackage:
    for package in packages:
        if package.name == package_name:
            return package
    valid = ", ".join(package.name for package in packages)
    raise SystemExit(f"unknown package {package_name!r}; expected one of: {valid}")


if __name__ == "__main__":
    sys.exit(main())
