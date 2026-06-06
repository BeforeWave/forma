from __future__ import annotations

import json
import os
import subprocess
import sys
import tarfile
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAMPLE_PROFILE = (
    ROOT / "examples" / "profiles" / "sample-backend" / "sample-backend-go.yaml"
)


def test_wheel_cli_uses_packaged_assets_from_non_repo_cwd(tmp_path: Path) -> None:
    wheel = _build_wheel(tmp_path)
    _assert_wheel_assets(wheel)
    outside_cwd = tmp_path / "outside"
    outside_cwd.mkdir()
    env = os.environ.copy()
    env["PYTHONPATH"] = str(wheel)

    profile = _run_installed(
        ["explain", "profile", "--target", "codex"],
        cwd=outside_cwd,
        env=env,
    )
    assert "# Forma Profile Guidance" in profile.stdout
    assert (
        "source/skill-creator/references/profile-authoring-principles.md"
        in profile.stdout
    )

    injection = _run_installed(
        ["explain", "temporary-injection", "--format", "json", "--target", "codex"],
        cwd=outside_cwd,
        env=env,
    )
    payload = json.loads(injection.stdout)
    assert payload["topic"] == "temporary-injection"
    assert payload["target"] == "codex"
    assert "constraints.default" in payload["markdown"]

    generated = tmp_path / "generated"
    _run_installed(
        [
            "create",
            "--target",
            "codex",
            "--profile",
            str(SAMPLE_PROFILE),
            "--output",
            str(generated),
        ],
        cwd=outside_cwd,
        env=env,
    )
    assert (generated / "backend-plan-first-plan-issue" / "SKILL.md").is_file()
    _run_installed(["verify", str(generated)], cwd=outside_cwd, env=env)

    creator_dist = tmp_path / "creator-dist"
    _run_installed(
        ["build-creator", "--output", str(creator_dist), "--target", "codex"],
        cwd=outside_cwd,
        env=env,
    )
    creator = creator_dist / "codex" / "forma-creator"
    assert (creator / "references" / "profile-authoring-principles.md").is_file()
    assert (
        creator
        / "resources"
        / "plan-first"
        / "methodology"
        / "stages"
        / "shape.md"
    ).is_file()
    _run_installed(["verify", str(creator)], cwd=outside_cwd, env=env)


def test_sdist_includes_runtime_asset_sources(tmp_path: Path) -> None:
    sdist_dir = tmp_path / "sdist"
    sdist_dir.mkdir()
    subprocess.run(
        ["uv", "build", "--sdist", "--out-dir", str(sdist_dir)],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    archive = next(sdist_dir.glob("forma-*.tar.gz"))
    with tarfile.open(archive) as tar:
        names = set(tar.getnames())
    assert any(name.endswith("source/methodology/stages/shape.md") for name in names)
    assert any(
        name.endswith(
            "source/skill-creator/references/profile-authoring-principles.md"
        )
        for name in names
    )
    assert any(
        name.endswith(
            "source/skill-creator/references/temporary-injection-generation.md"
        )
        for name in names
    )


def _build_wheel(tmp_path: Path) -> Path:
    wheel_dir = tmp_path / "wheelhouse"
    wheel_dir.mkdir()
    subprocess.run(
        [
            "uv",
            "build",
            "--wheel",
            "--out-dir",
            str(wheel_dir),
        ],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return next(wheel_dir.glob("forma-*.whl"))


def _assert_wheel_assets(wheel: Path) -> None:
    with zipfile.ZipFile(wheel) as archive:
        names = set(archive.namelist())
    assert "forma/assets/source/methodology/stages/shape.md" in names
    assert (
        "forma/assets/source/skill-creator/references/profile-authoring-principles.md"
        in names
    )
    assert (
        "forma/assets/source/skill-creator/references/temporary-injection-generation.md"
        in names
    )


def _run_installed(
    args: list[str],
    cwd: Path,
    env: dict[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "forma.cli", *args],
        cwd=cwd,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
