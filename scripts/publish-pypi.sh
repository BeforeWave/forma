#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/publish-pypi.sh [--publish] [--allow-dirty]

Build and validate the PyPI package without writing Python distribution files
into the repository's committed dist/ release surface.

Default mode runs tests, builds wheel/sdist into /private/tmp, smokes the wheel,
and performs an upload dry-run. Pass --publish to upload to PyPI.

Authentication for --publish:
  - UV_PUBLISH_TOKEN, or
  - ~/.pypirc [pypi] with username = __token__ and password = <token>
USAGE
}

publish=0
allow_dirty=0

for arg in "$@"; do
  case "$arg" in
    --publish)
      publish=1
      ;;
    --allow-dirty)
      allow_dirty=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "error: unknown argument: $arg" >&2
      usage >&2
      exit 2
      ;;
  esac
done

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

if [[ "$allow_dirty" -ne 1 ]] && [[ -n "$(git status --porcelain)" ]]; then
  echo "error: working tree is dirty; commit changes or pass --allow-dirty" >&2
  exit 1
fi

read -r package_name package_version dist_prefix < <(
  python3 - <<'PY'
import re
import tomllib
from pathlib import Path

project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
name = project["name"]
version = project["version"]
dist_prefix = re.sub(r"[-_.]+", "_", name).lower()
print(name, version, dist_prefix)
PY
)

out_dir="/private/tmp/forma-pypi-dist-${package_version}"
wheel="${out_dir}/${dist_prefix}-${package_version}-py3-none-any.whl"
sdist="${out_dir}/${dist_prefix}-${package_version}.tar.gz"

echo "Package: ${package_name} ${package_version}"
echo "Output: ${out_dir}"

uv run --extra dev python -m pytest -p no:cacheprovider tests/
uv build --out-dir "$out_dir" --clear

test -f "$wheel"
test -f "$sdist"

uv run --isolated --with "$wheel" forma --version
uv run --isolated --with "$wheel" forma --help >/dev/null

if [[ "$publish" -eq 1 ]]; then
  echo "Publishing ${package_name} ${package_version} to PyPI"
  uv publish --trusted-publishing never --check-url https://pypi.org/simple/ "$wheel" "$sdist"
else
  echo "Dry-run upload for ${package_name} ${package_version}"
  uv publish --dry-run --trusted-publishing never "$wheel" "$sdist"
  echo "Dry-run complete. Re-run with --publish to upload."
fi
