#!/usr/bin/env sh
set -eu

profile_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
repo_root=$(CDPATH= cd -- "$profile_dir/.." && pwd)
profile="$profile_dir/profile.yaml"
env_file="$profile_dir/reinstall-workflow.env"

if [ ! -f "$env_file" ]; then
  cat >&2 <<MSG
Missing local reinstall facts: $env_file

Create this ignored file with:
  FORMA_CODEX_MARKETPLACE_PLUGIN_ROOT=<local marketplace plugin source dir>
  FORMA_CODEX_PLUGIN_SELECTOR=<plugin-id>@<marketplace>
MSG
  exit 3
fi

. "$env_file"
: "${FORMA_CODEX_MARKETPLACE_PLUGIN_ROOT:?Missing FORMA_CODEX_MARKETPLACE_PLUGIN_ROOT in $env_file}"
: "${FORMA_CODEX_PLUGIN_SELECTOR:?Missing FORMA_CODEX_PLUGIN_SELECTOR in $env_file}"

target="codex"
artifact="plugin"
output="${TMPDIR:-/tmp}/forma-self-${artifact}-${target}"
codex_marketplace_plugin_root="$FORMA_CODEX_MARKETPLACE_PLUGIN_ROOT"
codex_plugin_selector="$FORMA_CODEX_PLUGIN_SELECTOR"

forma_cli() {
  (cd "$repo_root" && uv run --extra dev forma "$@")
}

case "$artifact" in
  plugin)
    forma_cli build plugin --target "$target" --profile "$profile" --output "$output"
    forma_cli drift "$output" --profile "$profile"
    forma_cli verify "$output"
    mkdir -p "$codex_marketplace_plugin_root"
    find "$codex_marketplace_plugin_root" -mindepth 1 -maxdepth 1 -exec rm -rf {} +
    cp -R "$output"/. "$codex_marketplace_plugin_root"/
    forma_cli verify "$codex_marketplace_plugin_root"
    codex plugin add "$codex_plugin_selector"
    ;;
  *)
    echo "unsupported artifact: $artifact" >&2
    exit 2
    ;;
esac

cat <<MSG
Reinstall complete.
profile: $profile
artifact: $artifact
target: $target
output: $output
marketplace_plugin_root: $codex_marketplace_plugin_root
plugin_selector: $codex_plugin_selector
repo: $repo_root
MSG
