#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/publish-npm.sh [--publish] [--allow-dirty]

Validate and publish the thin npm launcher package at npm/forma.

Default mode runs local smoke checks, packs the npm tarball into /private/tmp,
smokes the packed tarball, and performs an npm publish dry-run. Pass --publish
to upload the packed tarball to the public npm registry.

Authentication for --publish:
  - npm login with an account that can publish @beforewave/forma, and
  - account 2FA, or a granular access token with bypass 2FA enabled.
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

read -r python_package python_version < <(
  python3 - <<'PY'
import tomllib
from pathlib import Path

project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
print(project["name"], project["version"])
PY
)

package_dir="npm/forma"
read -r npm_package npm_version < <(
  node -e 'const pkg = require("./npm/forma/package.json"); console.log(pkg.name, pkg.version);'
)
tarball_name="$(
  node -e 'const pkg = require("./npm/forma/package.json"); console.log(pkg.name.replace(/^@/, "").replace("/", "-") + "-" + pkg.version + ".tgz");'
)"

if [[ "$npm_version" != "$python_version" ]]; then
  echo "error: npm package version ${npm_version} does not match ${python_package} ${python_version}" >&2
  exit 1
fi

echo "Python package: ${python_package} ${python_version}"
echo "npm package: ${npm_package} ${npm_version}"

out_dir="/private/tmp/forma-npm-dist-${npm_version}"
tarball="${out_dir}/${tarball_name}"

node "${package_dir}/bin/forma-npm.js" --version
node "${package_dir}/bin/forma-npm.js" >/dev/null
mkdir -p "$out_dir"
rm -f "$tarball"

(
  cd "$package_dir"
  npm pack --dry-run
  npm pack --pack-destination "$out_dir"
)

test -f "$tarball"
npm exec --yes --package "$tarball" -- forma-npm --version
npm exec --yes --package "$tarball" -- forma-npm >/dev/null

if [[ "$publish" -eq 1 ]]; then
  npm whoami >/dev/null
  echo "Publishing ${npm_package} ${npm_version} to npm from ${tarball}"
  npm publish "$tarball" --access public
else
  echo "Dry-run publish for ${npm_package} ${npm_version} from ${tarball}"
  npm publish "$tarball" --access public --dry-run
  echo "Dry-run complete. Re-run with --publish to upload."
fi
