#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/publish-pypi.sh [--publish] [--allow-dirty] [--package <name>] [--all]

Build and validate PyPI packages without writing Python distribution files into
the repository's committed dist/ release surface.

Default mode runs tests, builds every package listed in
packaging/pypi/packages.toml into /private/tmp, smokes each wheel, and validates
distribution metadata with twine. Pass --publish to upload to PyPI with twine.

Use --package <name> to build one configured distribution package. Use --all to
make the all-packages behavior explicit.

Authentication for --publish:
  - TWINE_USERNAME and TWINE_PASSWORD, or
  - ~/.pypirc [pypi] with username = __token__ and password = <token>
USAGE
}

run_twine() {
  if python3 -m twine --version >/dev/null 2>&1; then
    python3 -m twine "$@"
  else
    uvx twine "$@"
  fi
}

publish=0
allow_dirty=0
all_packages=0
packages=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --publish)
      publish=1
      shift
      ;;
    --allow-dirty)
      allow_dirty=1
      shift
      ;;
    --all)
      all_packages=1
      shift
      ;;
    --package)
      if [[ $# -lt 2 ]]; then
        echo "error: --package requires a package name" >&2
        usage >&2
        exit 2
      fi
      packages+=("$2")
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$all_packages" -eq 1 ]] && [[ "${#packages[@]}" -gt 0 ]]; then
  echo "error: use either --all or --package, not both" >&2
  exit 2
fi

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ "$allow_dirty" -ne 1 ]] && [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree is dirty; commit changes or pass --allow-dirty" >&2
  exit 1
fi

read -r package_version < <(
  python3 - <<'PY'
import tomllib
from pathlib import Path

project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
print(project["version"])
PY
)

if [[ "${#packages[@]}" -eq 0 ]]; then
  while IFS= read -r package_name; do
    packages+=("$package_name")
  done < <(python3 scripts/build-pypi-package.py --list-packages)
fi

echo "Version: ${package_version}"
echo "Packages: ${packages[*]}"

uv run --extra dev python -m pytest -p no:cacheprovider tests/

for package_name in "${packages[@]}"; do
  dist_prefix="$(python3 scripts/build-pypi-package.py --dist-prefix "$package_name")"
  out_dir="/private/tmp/forma-pypi-dist-${package_name}-${package_version}"
  wheel="${out_dir}/${dist_prefix}-${package_version}-py3-none-any.whl"
  sdist="${out_dir}/${dist_prefix}-${package_version}.tar.gz"

  echo "Package: ${package_name} ${package_version}"
  echo "Output: ${out_dir}"

  python3 scripts/build-pypi-package.py --package "$package_name" --out-dir "$out_dir" --clear

  test -f "$wheel"
  test -f "$sdist"

  uv run --isolated --with "$wheel" forma --version
  uv run --isolated --with "$wheel" forma --help >/dev/null
  run_twine check "$wheel" "$sdist"

  if [[ "$publish" -eq 1 ]]; then
    echo "Publishing ${package_name} ${package_version} to PyPI with twine"
    run_twine upload --repository pypi "$wheel" "$sdist"
  else
    echo "Upload skipped for ${package_name} ${package_version}. Re-run with --publish to upload."
  fi
done

if [[ "$publish" -ne 1 ]]; then
  echo "Validation complete. Re-run with --publish to upload."
fi
