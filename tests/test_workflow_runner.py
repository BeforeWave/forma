from __future__ import annotations

import os
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


def test_check_accepts_dirty_contract_without_running_validation_or_state(
    tmp_path: Path,
) -> None:
    repo, workflow = _locked_issue(tmp_path, "contract-check", validate="false")
    tasks_file = repo / "plans" / "issue-contract-check" / "tasks.md"
    tasks_file.write_text(
        """- [ ] [contract-guard] Exercise contract check
Accept: Task Type=gate; check parses the contract
Validate: false
Depends: none
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(workflow), "check", "contract-check"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Contract check passed for issue-contract-check" in result.stdout
    assert "Task format: structured" in result.stdout
    assert "Tasks: 1 total, 0 checked, 1 unchecked" in result.stdout
    assert "Validation commands were not run." in result.stdout
    assert not (repo / ".forma" / "state" / "workflow").exists()
    assert not list((repo / "plans" / "issue-contract-check" / "runs").glob("*.md"))
    staged = _run(["git", "diff", "--cached", "--name-only"], cwd=repo)
    assert staged.stdout == ""


def test_check_rejects_structured_task_schema_before_review_ready(
    tmp_path: Path,
) -> None:
    repo, workflow = _locked_issue(tmp_path, "contract-schema")
    tasks_file = repo / "plans" / "issue-contract-schema" / "tasks.md"
    tasks_file.write_text(
        """- [ ] [contract-guard] Exercise contract check
Accept: Task Type=gate; check parses the contract
Accept: Task Type=gate; duplicate accept should fail
Validate: false
Depends: none
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(workflow), "check", "contract-schema"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert "Structured task [contract-guard] must not repeat Accept:" in result.stderr
    assert not (repo / ".forma" / "state" / "workflow").exists()
    assert not list((repo / "plans" / "issue-contract-schema" / "runs").glob("*.md"))
    staged = _run(["git", "diff", "--cached", "--name-only"], cwd=repo)
    assert staged.stdout == ""


def test_check_rejects_unknown_shared_check_reference(tmp_path: Path) -> None:
    repo, workflow = _locked_issue(tmp_path, "contract-shared-check")
    tasks_file = repo / "plans" / "issue-contract-shared-check" / "tasks.md"
    tasks_file.write_text(
        """- [ ] [contract-guard] Exercise contract check
Accept: Task Type=gate; check parses shared check references
Validate: true
Use-Check: missing-check
Depends: none
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(workflow), "check", "contract-shared-check"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert "Structured task references unknown shared check: missing-check" in result.stderr
    assert not (repo / ".forma" / "state" / "workflow").exists()


def test_check_rejects_missing_plan_contract_section(tmp_path: Path) -> None:
    repo, workflow = _locked_issue(tmp_path, "contract-plan")
    plan_file = repo / "plans" / "issue-contract-plan" / "plan.md"
    plan_file.write_text(
        plan_file.read_text(encoding="utf-8").replace(
            "## Artifact/Evidence Boundary\n\n",
            "",
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(workflow), "check", "contract-plan"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert "plan.md is missing required section: ## Artifact/Evidence Boundary" in result.stderr
    assert not (repo / ".forma" / "state" / "workflow").exists()


def test_check_rejects_rework_task_missing_from_rework_ledger(tmp_path: Path) -> None:
    repo, workflow = _locked_issue(tmp_path, "contract-rework")
    tasks_file = repo / "plans" / "issue-contract-rework" / "tasks.md"
    rework_file = repo / "plans" / "issue-contract-rework" / "rework.md"
    tasks_file.write_text(
        """- [ ] [rework-001-contract-guard] Exercise rework ledger check
Accept: Task Type=gate; check parses rework ledger
Validate: true
Depends: none
""",
        encoding="utf-8",
    )
    rework_file.write_text(
        """# Rework

## Rework 001: Contract guard

Source:
- direct-human-feedback

Feedback:
- Check rework ledger structure.

Classification:
- task-rework

Same-Issue Rationale:
- This remains inside the active issue.

User Confirmation:
- confirmed

Appended Tasks:
- rework-001-other-task
""",
        encoding="utf-8",
    )

    result = subprocess.run(
        ["bash", str(workflow), "check", "contract-rework"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert (
        "rework task is not listed in rework.md Appended Tasks: rework-001-contract-guard"
        in result.stderr
    )
    assert not (repo / ".forma" / "state" / "workflow").exists()


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
    assert (
        repo / ".forma" / "state" / "workflow" / "issue-ordinary-notes" / "review-state.env"
    ).is_file()
    assert (
        repo / ".forma" / "state" / "workflow" / "issue-ordinary-notes" / "validation.log"
    ).is_file()
    assert not (repo / ".forma-workflow").exists()


def test_review_ready_rejects_pre_staged_index_as_contract_violation(
    tmp_path: Path,
) -> None:
    repo, workflow = _locked_issue(tmp_path, "staged-index")
    (repo / "proof.txt").write_text("changed\n", encoding="utf-8")
    _run(["git", "add", "proof.txt"], cwd=repo)

    result = subprocess.run(
        ["bash", str(workflow), "review-ready", "staged-index"],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode != 0
    assert "Pre-staged changes violate the workflow contract" in result.stderr
    assert "Do not run git add, git rm" in result.stderr
    assert "the workflow runner owns review staging" in result.stderr
    assert "git restore --staged <path>" in result.stderr


def test_review_ready_inherits_invoking_environment(tmp_path: Path) -> None:
    repo, workflow = _locked_issue(
        tmp_path,
        "env-inherit",
        validate='test "$FORMA_WORKFLOW_TEST_ENV" = "inherited-value"',
    )
    (repo / "proof.txt").write_text("changed\n", encoding="utf-8")

    env = os.environ.copy()
    env["FORMA_WORKFLOW_TEST_ENV"] = "inherited-value"
    result = subprocess.run(
        ["bash", str(workflow), "review-ready", "env-inherit"],
        cwd=repo,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Review-ready task [1]" in result.stdout


def test_review_ready_ignores_bash_startup_environment_hooks(tmp_path: Path) -> None:
    repo, workflow = _locked_issue(
        tmp_path,
        "bash-env",
        validate='test -z "${BASH_ENV:-}" && test -z "${ENV:-}" && test ! -e .bash-env-sourced',
    )
    hook = tmp_path / "bash-env-hook.sh"
    hook.write_text(
        "export FORMA_WORKFLOW_BASH_ENV_INJECTED=1\n"
        "touch .bash-env-sourced\n",
        encoding="utf-8",
    )
    (repo / "proof.txt").write_text("changed\n", encoding="utf-8")

    env = os.environ.copy()
    result = subprocess.run(
        [
            "bash",
            "--noprofile",
            "--norc",
            "-c",
            'hook="$1"; workflow="$2"; shift 2; export BASH_ENV="$hook" ENV="$hook"; source "$workflow" "$@"',
            "_",
            str(hook),
            str(workflow),
            "review-ready",
            "bash-env",
        ],
        cwd=repo,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    assert result.returncode == 0, result.stderr + result.stdout
    assert "Review-ready task [1]" in result.stdout
    assert not (repo / ".bash-env-sourced").exists()


def _locked_issue(
    tmp_path: Path,
    issue_id: str,
    *,
    validate: str = "true",
    final_validation: str = "true",
) -> tuple[Path, Path]:
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
        f"""# Issue Plan

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

## Artifact/Evidence Boundary

- Evidence stays under the issue runs directory.

## Validation

## Final Validation

```sh
{final_validation}
```

## Risks / Notes

- None.
""",
        encoding="utf-8",
    )
    tasks_file.write_text(
        f"""- [ ] [notes-guard] Exercise notes guard
Accept: Task Type=gate; review-ready checks implement-notes
Validate: {validate}
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
