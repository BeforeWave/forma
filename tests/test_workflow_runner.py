from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = ROOT / "source" / "methodology" / "resources" / "shared" / "scripts" / "forma-workflow.sh"
PLAN_TEMPLATE = ROOT / "source" / "methodology" / "resources" / "shared" / "references" / "plan-template.md"
TASKS_TEMPLATE = ROOT / "source" / "methodology" / "resources" / "shared" / "references" / "tasks-template.md"


def test_review_ready_rejects_stateful_final_validation_lines(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "skill" / "scripts"
    references_dir = repo / "skill" / "references"
    scripts_dir.mkdir(parents=True)
    references_dir.mkdir(parents=True)
    shutil.copy2(WORKFLOW_SCRIPT, scripts_dir / "forma-workflow.sh")
    shutil.copy2(PLAN_TEMPLATE, references_dir / "plan-template.md")
    shutil.copy2(TASKS_TEMPLATE, references_dir / "tasks-template.md")

    _run(["git", "init"], cwd=repo)
    _run(["git", "config", "user.email", "test@example.com"], cwd=repo)
    _run(["git", "config", "user.name", "Test User"], cwd=repo)
    workflow = scripts_dir / "forma-workflow.sh"
    _run(["bash", str(workflow), "init", "stateful-final"], cwd=repo)

    plan_file = repo / "plans" / "issue-stateful-final" / "plan.md"
    tasks_file = repo / "plans" / "issue-stateful-final" / "tasks.md"
    plan_file.write_text(
        """# Issue Plan

## Goal

- Prove stateful final validation lines fail fast.

## Plan Strategy

- Plan Strategy: step-execution

## Scope

- In scope: runner behavior.

## Approach

- Use a minimal task.

## Constraints

- Keep the fixture small.

## Acceptance Criteria

- review-ready rejects assignment-only final validation.

## Validation

## Final Validation

```sh
tmp_root=/private/tmp/forma-stateful-final
```

## Risks / Notes

- None.
""",
        encoding="utf-8",
    )
    tasks_file.write_text(
        """- [ ] [runner-guard] Exercise runner guard
Accept: Task Type=gate; review-ready reaches final validation parsing
Validate: true
Depends: none
""",
        encoding="utf-8",
    )
    _run(["git", "add", "plans/issue-stateful-final/plan.md", "plans/issue-stateful-final/tasks.md"], cwd=repo)
    _run(["git", "commit", "-m", "test plan"], cwd=repo)

    result = subprocess.run(
        ["bash", str(workflow), "review-ready", "stateful-final"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert "Final Validation command must be self-contained" in result.stderr
    assert "tmp_root=/private/tmp/forma-stateful-final" in result.stderr


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
