"""Shared test configuration for the scaffolded project."""

from __future__ import annotations

import sys
from pathlib import Path


def project_root() -> Path:
    """Return the repository root used by local tests."""

    return Path(__file__).resolve().parent.parent


def bootstrap_test_import_path() -> Path:
    """Ensure the local ``src`` directory is importable during test collection."""

    source_directory = project_root() / "src"

    if str(source_directory) not in sys.path:
        sys.path.insert(0, str(source_directory))

    return source_directory


bootstrap_test_import_path()
