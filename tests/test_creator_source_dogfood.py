from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from forma_verifier import verify


ROOT = Path(__file__).resolve().parents[1]
CREATOR_SOURCE = ROOT / "source" / "skill-creator"


def test_creator_source_verifies_itself() -> None:
    report = verify(CREATOR_SOURCE)

    assert report.passed, report.format_human()


def test_creator_source_entry_script_runs_without_developer_cli() -> None:
    result = subprocess.run(
        [sys.executable, str(CREATOR_SOURCE / "scripts" / "verify.py"), str(CREATOR_SOURCE)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    assert "ok - all rules passed" in result.stdout


def test_creator_source_does_not_duplicate_methodology_resources() -> None:
    assert not (CREATOR_SOURCE / "resources" / "plan-first" / "methodology").exists()
