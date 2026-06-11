from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_SCRIPT = ROOT / "source" / "methodology" / "resources" / "shared" / "scripts" / "forma-workflow.sh"
PLAN_TEMPLATE = ROOT / "source" / "methodology" / "resources" / "shared" / "references" / "plan-template.md"
TASKS_TEMPLATE = ROOT / "source" / "methodology" / "resources" / "shared" / "references" / "tasks-template.md"


def test_next_rejects_unlocked_plan_with_showhand_stop_message(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    scripts_dir = repo / "skill" / "scripts"
    references_dir = repo / "skill" / "references"
    scripts_dir.mkdir(parents=True)
    references_dir.mkdir(parents=True)
    shutil.copy2(WORKFLOW_SCRIPT, scripts_dir / "forma-workflow.sh")
    shutil.copy2(PLAN_TEMPLATE, references_dir / "plan-template.md")
    shutil.copy2(TASKS_TEMPLATE, references_dir / "tasks-template.md")

    _run(["git", "init"], cwd=repo)
    workflow = scripts_dir / "forma-workflow.sh"
    init_result = _run(["bash", str(workflow), "init", "unlocked"], cwd=repo)
    assert "stage only those files" in init_result.stdout
    assert "show the staged diff for user confirmation" in init_result.stdout

    result = subprocess.run(
        ["bash", str(workflow), "next", "unlocked"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert "plan.md must be locked before execution" in result.stderr
    assert "Stop showhand and return to the lock stage." in result.stderr


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


def test_review_ready_rejects_process_gate_bypass_decision_notes(tmp_path: Path) -> None:
    repo, workflow = _locked_issue(tmp_path, "gate-notes")

    notes_file = repo / "plans" / "issue-gate-notes" / "implement-notes.md"
    notes_file.write_text(
        """# Implement Notes

## Task 1: notes-guard

Outcome:
- Exercised notes guard.

Decision Notes:
- Bypassed workflow runner approval and skipped validation because this was faster.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- None
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(workflow), "review-ready", "gate-notes"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert "Decision Notes must not record bypassing workflow" in result.stderr
    assert "return to the required gate" in result.stderr


def test_review_ready_accepts_ordinary_decision_notes(tmp_path: Path) -> None:
    repo, workflow = _locked_issue(tmp_path, "ordinary-notes")

    notes_file = repo / "plans" / "issue-ordinary-notes" / "implement-notes.md"
    notes_file.write_text(
        """# Implement Notes

## Task 1: notes-guard

Outcome:
- Exercised notes guard.

Decision Notes:
- Chose the smaller helper function because it kept the runner behavior scoped.

Plan Gaps Found:
- None

Classifications:
- None

Deviations From Plan:
- None

Follow-ups:
- None
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(workflow), "review-ready", "ordinary-notes"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Review-ready task [1]" in result.stdout


def _locked_issue(tmp_path: Path, issue_id: str) -> tuple[Path, Path]:
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
    _run(["bash", str(workflow), "init", issue_id], cwd=repo)

    plan_file = repo / "plans" / f"issue-{issue_id}" / "plan.md"
    tasks_file = repo / "plans" / f"issue-{issue_id}" / "tasks.md"
    plan_file.write_text(
        """# Issue Plan

## Goal

- Exercise implement-notes review behavior.

## Plan Strategy

- Plan Strategy: step-execution

## Scope

- In scope: runner behavior.

## Approach

- Use a minimal task.

## Constraints

- Keep the fixture small.

## Acceptance Criteria

- review-ready validates implement-notes.

## Validation

## Final Validation

```sh
true
```

## Risks / Notes

- None.
""",
        encoding="utf-8",
    )
    tasks_file.write_text(
        """- [ ] [notes-guard] Exercise notes guard
Accept: Task Type=gate; review-ready checks implement-notes
Validate: true
Depends: none
""",
        encoding="utf-8",
    )
    _run(["git", "add", f"plans/issue-{issue_id}/plan.md", f"plans/issue-{issue_id}/tasks.md"], cwd=repo)
    _run(["git", "commit", "-m", "test plan"], cwd=repo)
    return repo, workflow


def _run(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
