"""Deterministic Forma repository initialization remediation."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from forma.repo_doctor import diagnose_repo
from forma.reports import ActionableReport, NextAction, ReportSection


@dataclass(frozen=True)
class InitFile:
    path: Path
    description: str
    content: str
    executable: bool = False


def plan_init(
    *,
    root: Path,
    profile_dir: Path | None,
    apply: bool,
) -> ActionableReport:
    repo_root = root.resolve()
    if not repo_root.exists() or not repo_root.is_dir():
        return ActionableReport(
            command="forma init",
            subject=str(repo_root),
            status="unsafe",
            summary="init target is not an existing directory",
            blockers=("provide an existing repository directory",),
        )

    resolved_profile_dir = _resolve_profile_dir(repo_root, profile_dir)
    files = _init_files(repo_root, resolved_profile_dir)
    changes = [_plan_or_apply(file, repo_root, apply) for file in files]
    doctor = diagnose_repo(repo_root)
    verb = "applied" if apply else "planned"
    return ActionableReport(
        command="forma init",
        subject=str(repo_root),
        status="needs-human",
        summary=f"deterministic Forma initialization {verb}",
        sections=(
            ReportSection(
                kind="repo-diagnosis",
                title="Repository Diagnosis",
                payload={
                    "status": doctor.status,
                    "summary": doctor.summary,
                },
            ),
            ReportSection(
                kind="planned-changes" if not apply else "applied-changes",
                title="Planned Changes" if not apply else "Applied Changes",
                payload={"items": changes},
            ),
        ),
        next_actions=(
            NextAction(
                title="review generated profile source",
                description=(
                    "Treat .forma contents as draft project workflow source; "
                    "human review is still required before workflow generation."
                ),
            ),
            NextAction(
                title="run repo doctor after edits",
                command=f"forma doctor repo {_display_path(repo_root, repo_root)}",
            ),
        ),
        warnings=(
            "init creates draft skeletons only; it does not review or approve a profile",
            "accepted .forma contents should be tracked by Git",
        ),
    )


def _resolve_profile_dir(root: Path, profile_dir: Path | None) -> Path:
    if profile_dir is None:
        return root / ".forma"
    if profile_dir.is_absolute():
        return profile_dir
    return root / profile_dir


def _plan_or_apply(file: InitFile, root: Path, apply: bool) -> dict[str, str]:
    exists = file.path.exists()
    action = "skip-existing" if exists else ("create" if apply else "plan-create")
    if apply and not exists:
        file.path.parent.mkdir(parents=True, exist_ok=True)
        file.path.write_text(file.content, encoding="utf-8")
        if file.executable:
            file.path.chmod(0o755)
    return {
        "path": _display_path(root, file.path),
        "action": action,
        "description": file.description,
    }


def _init_files(root: Path, profile_dir: Path) -> tuple[InitFile, ...]:
    return (
        InitFile(
            path=root / ".forma" / ".gitignore",
            description="Ignore Forma runtime state while keeping workflow source tracked.",
            content=FORMA_GITIGNORE,
        ),
        InitFile(
            path=profile_dir / "profile.yaml",
            description="Draft profile skeleton; requires human review before use.",
            content=PROFILE_YAML,
        ),
        InitFile(
            path=profile_dir / "reinstall-workflow.sh",
            description="Single profile-local reinstall entrypoint skeleton.",
            content=REINSTALL_WORKFLOW,
            executable=True,
        ),
    )


def _display_path(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


PROFILE_YAML = """profile:
  id: local-project
  description: Draft local Forma profile. Review before workflow generation.
bundle:
  name: local-project
  description: Draft local workflow bundle. Review before use.
constraints:
  default:
    - Replace this draft constraint with reviewed project rules before building installable workflow output.
"""


FORMA_GITIGNORE = """/state/
"""


REINSTALL_WORKFLOW = """#!/usr/bin/env sh
set -eu

FORMA_REINSTALL_WORKFLOW_BOOTSTRAP_INCOMPLETE=1

cat <<'MSG'
This reinstall-workflow.sh is bootstrap-incomplete.

Before using it as a reusable profile-local reinstall flow, confirm the install
facts with the user and replace this skeleton with a fixed-fact script:

- artifact kind
- target
- plugin id when the artifact kind is plugin
- marketplace name when the target install uses a marketplace
- marketplace source when the target install uses a marketplace
- install selector
- visibility check

The completed script should run the build, freshness gate, verify gate, install
or marketplace refresh, and visibility check with those facts encoded. It should
not list marketplaces or leave plugin id, marketplace, selector, or source
refresh decisions open at runtime.
MSG

exit 3
"""
