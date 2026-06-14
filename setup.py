from __future__ import annotations

import shutil
from pathlib import Path

from setuptools import setup
from setuptools.command.build_py import build_py as _build_py


class build_py(_build_py):
    """Copy canonical Forma source trees into the installed package."""

    def run(self) -> None:
        super().run()
        root = Path(__file__).parent
        assets_root = Path(self.build_lib) / "forma" / "assets" / "source"
        for name in ("agent-guide", "methodology", "skill-creator"):
            source = root / "source" / name
            target = assets_root / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
        default_profile = root / "profiles" / "default"
        target = Path(self.build_lib) / "forma" / "assets" / "profiles" / "default"
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(default_profile, target)


setup(cmdclass={"build_py": build_py})
