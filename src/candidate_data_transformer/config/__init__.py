"""Configuration objects and helpers for the project scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AppSettings:
    """Application settings shared across the transformation scaffold."""

    project_root: Path
    source_directory: Path
    data_directory: Path
    documentation_directory: Path
    tests_directory: Path


def load_settings(project_root: Path | None = None) -> AppSettings:
    """Load local project settings from the repository layout."""

    resolved_project_root = project_root or Path(__file__).resolve().parents[3]
    return AppSettings(
        project_root=resolved_project_root,
        source_directory=resolved_project_root / "src",
        data_directory=resolved_project_root / "data",
        documentation_directory=resolved_project_root / "docs",
        tests_directory=resolved_project_root / "tests",
    )
