from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from forma_verifier import verify


ROOT = Path(__file__).resolve().parents[1]
LAYER_1 = ROOT / "source" / "skill-creator"


def test_layer_1_bundle_verifies_itself() -> None:
    report = verify(LAYER_1)

    assert report.passed, report.format_human()


def test_layer_1_entry_script_runs_without_developer_cli() -> None:
    result = subprocess.run(
        [sys.executable, str(LAYER_1 / "scripts" / "verify.py"), str(LAYER_1)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok - all rules passed" in result.stdout


def test_layer_1_source_does_not_duplicate_methodology_resources() -> None:
    assert not (LAYER_1 / "resources" / "plan-first" / "methodology").exists()
