#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/publish-npm.sh [--publish] [--allow-dirty] [--package <name>] [--all]

Validate and publish Forma's thin npm launcher packages.

Default mode builds every package listed in packaging/npm/packages.toml into
/private/tmp, runs local smoke checks, packs each npm tarball, smokes each
packed tarball, and performs npm publish dry-runs. Pass --publish to upload the
packed tarballs to the public npm registry. Already-published versions are
reported and skipped because npm package versions are immutable.

Use --package <name> to build one configured npm package. Use --all to make the
all-packages behavior explicit.

Authentication for --publish:
  - npm login with an account that can publish the configured package names, and
  - account 2FA, or a granular access token with bypass 2FA enabled.
USAGE
}

published_version_exists() {
  local package_name="$1"
  local package_version="$2"

  npm view "${package_name}@${package_version}" version --json >/dev/null 2>&1
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

read -r python_package python_version < <(
  python3 - <<'PY'
import tomllib
from pathlib import Path

project = tomllib.loads(Path("pyproject.toml").read_text())["project"]
print(project["name"], project["version"])
PY
)

if [[ "${#packages[@]}" -eq 0 ]]; then
  while IFS= read -r package_name; do
    packages+=("$package_name")
  done < <(python3 scripts/build-npm-package.py --list-packages)
fi

echo "Python package: ${python_package} ${python_version}"
echo "npm packages: ${packages[*]}"

changelog_args=()
if [[ "$publish" -eq 1 ]]; then
  changelog_args+=(--publish)
fi
python3 scripts/check-changelog-version.py --version "$python_version" "${changelog_args[@]}"

if [[ "$publish" -eq 1 ]]; then
  npm whoami >/dev/null
fi

for package_name in "${packages[@]}"; do
  package_key="${package_name#@}"
  package_key="${package_key//\//-}"
  package_dir="/private/tmp/forma-npm-src-${package_key}-${python_version}"
  out_dir="/private/tmp/forma-npm-dist-${package_key}-${python_version}"

  python3 scripts/build-npm-package.py --package "$package_name" --out-dir "$package_dir" --clear

  read -r npm_package npm_version bin_name tarball_name < <(
    node -e '
const pkg = require(process.argv[1]);
const bins = typeof pkg.bin === "string" ? [pkg.name.split("/").pop()] : Object.keys(pkg.bin);
const tarball = pkg.name.replace(/^@/, "").replace("/", "-") + "-" + pkg.version + ".tgz";
console.log(pkg.name, pkg.version, bins[0], tarball);
' "$package_dir/package.json"
  )

  if [[ "$npm_version" != "$python_version" ]]; then
    echo "error: npm package version ${npm_version} does not match ${python_package} ${python_version}" >&2
    exit 1
  fi

  tarball="${out_dir}/${tarball_name}"

  echo "npm package: ${npm_package} ${npm_version}"
  echo "Output: ${out_dir}"

  node "${package_dir}/bin/forma-npm.js" --version
  node "${package_dir}/bin/forma-npm.js" >/dev/null
  mkdir -p "$out_dir"
  rm -f "$tarball"

  npm pack "$package_dir" --dry-run
  npm pack "$package_dir" --pack-destination "$out_dir"

  test -f "$tarball"
  npm exec --yes --package "$tarball" -- "$bin_name" --version
  npm exec --yes --package "$tarball" -- "$bin_name" >/dev/null

  if published_version_exists "$npm_package" "$npm_version"; then
    if [[ "$publish" -eq 1 ]]; then
      echo "Already published: ${npm_package} ${npm_version}; skipping immutable npm version."
    else
      echo "Registry already has ${npm_package} ${npm_version}; real publish would skip this immutable version."
    fi
    continue
  fi

  if [[ "$publish" -eq 1 ]]; then
    echo "Publishing ${npm_package} ${npm_version} to npm from ${tarball}"
    npm publish "$tarball" --access public
  else
    echo "Dry-run publish for ${npm_package} ${npm_version} from ${tarball}"
    npm publish "$tarball" --access public --dry-run
  fi
done

if [[ "$publish" -ne 1 ]]; then
  echo "Dry-run complete. Re-run with --publish to upload."
fi
