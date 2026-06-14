#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

usage() {
  cat <<'EOF'
Usage: scripts/validate.sh [shared|cli|docs|creator|verifier|full]

Modes:
  shared    Run the repo-wide source gate: tests/ plus git diff --check. Default.
  cli       Run CLI behavior tests.
  docs      Run documentation link tests and documentation whitespace checks.
  creator   Run profile composition and creator builder tests.
  verifier  Run verifier and Layer 1 dogfood tests, then verify source/skill-creator/.
  full      Run shared plus source/skill-creator verification.
EOF
}

require_command() {
  if ! command -v "$1" >/dev/null 2>&1; then
    printf 'missing required command: %s\n' "$1" >&2
    exit 127
  fi
}

run_shared() {
  uv run --extra dev python -m pytest -p no:cacheprovider tests/
  git diff --check
}

run_cli() {
  uv run --extra dev python -m pytest -p no:cacheprovider tests/test_cli.py
}

run_docs() {
  uv run --extra dev python -m pytest -p no:cacheprovider tests/test_docs_links.py
  git diff --check README.md README.zh-CN.md STRUCTURE.md AGENTS.md dist/AGENTS.md docs
}

run_creator() {
  uv run --extra dev python -m pytest -p no:cacheprovider tests/test_workflow_build.py tests/test_creator_builder.py
}

run_verifier() {
  uv run --extra dev python -m pytest -p no:cacheprovider tests/test_verifier.py tests/test_layer_1_dogfood.py
  uv run --extra dev forma verify source/skill-creator/
}

require_command uv
require_command git

mode="${1:-shared}"

case "$mode" in
  shared)
    run_shared
    ;;
  cli)
    run_cli
    ;;
  docs)
    run_docs
    ;;
  creator)
    run_creator
    ;;
  verifier)
    run_verifier
    ;;
  full)
    run_shared
    uv run --extra dev forma verify source/skill-creator/
    ;;
  -h|--help|help)
    usage
    ;;
  *)
    usage >&2
    exit 2
    ;;
esac
