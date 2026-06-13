#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'USAGE'
Usage: scripts/build-dist.sh [--with-creator]

Rebuild Forma's committed dist/ release surface from the current checkout.

Default mode refreshes the active release surface:
  - dist/skill-bundles/codex
  - dist/skill-bundles/claude-code
  - dist/skill-bundles/opencode
  - dist/plugins/codex/forma
  - dist/plugins/claude-code/forma

The active release surface is generated with Forma's product default profile by
calling build commands without `--profile`. Do not use the repository's
self-iteration profile under .forma/ for committed dist output. Creator bundles
under dist/skills/*/forma-creator are deferred by policy and are not rebuilt by
default. Pass --with-creator when an explicit creator issue requires refreshing
them.
USAGE
}

with_creator=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --with-creator)
      with_creator=1
      shift
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

repo_root="$(git rev-parse --show-toplevel)"
cd "$repo_root"

forma_cli() {
  uv run --extra dev forma "$@"
}

refresh_dir() {
  local output_dir="$1"

  rm -rf "$output_dir"
  mkdir -p "$(dirname "$output_dir")"
}

build_bundle() {
  local target="$1"
  local output_dir="dist/skill-bundles/$target"

  echo "Rebuilding bundle: $output_dir"
  refresh_dir "$output_dir"
  forma_cli build bundle --target "$target" --output "$output_dir"
  forma_cli verify "$output_dir"
}

build_plugin() {
  local target="$1"
  local output_dir="$2"

  echo "Rebuilding plugin: $output_dir"
  refresh_dir "$output_dir"
  forma_cli build plugin --target "$target" --output "$output_dir"
  forma_cli verify "$output_dir"
}

build_creator() {
  local target="$1"
  local output_root="dist/skills"
  local output_dir="$output_root/$target/forma-creator"

  echo "Rebuilding creator: $output_dir"
  refresh_dir "$output_dir"
  forma_cli build creator --target "$target" --output "$output_root"
  forma_cli verify "$output_dir"
}

build_bundle codex
build_bundle claude-code
build_bundle opencode

build_plugin codex dist/plugins/codex/forma
build_plugin claude-code dist/plugins/claude-code/forma

if [[ "$with_creator" -eq 1 ]]; then
  build_creator codex
  build_creator claude-code
  build_creator opencode
fi

echo "dist rebuild complete"
