"""Entry script the agent invokes after scaffolding a Plan-First workflow bundle.

Stdlib-only. Wraps `forma_verifier`, which lives organizationally inside the
Layer 1 meta source at `scripts/forma_verifier/`, so every adapted
`forma-creator` bundle ships the verifier — no `pip install` required for an
agent to use it.

Usage::

    python scripts/verify.py <path-to-bundle>
"""

from __future__ import annotations

import sys
from pathlib import Path

# Make `scripts/forma_verifier` importable when running this script directly,
# regardless of where Layer 1 was copied to.
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from forma_verifier.runner import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
