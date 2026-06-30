"""Command-line entry point for the project scaffold."""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap_source_path() -> Path:
    """Ensure the local ``src`` directory is importable during early development."""

    project_root = Path(__file__).resolve().parent
    source_directory = project_root / "src"

    if str(source_directory) not in sys.path:
        sys.path.insert(0, str(source_directory))

    return project_root


def main() -> int:
    """Build the application shell without executing business logic."""

    project_root = _bootstrap_source_path()

    from candidate_data_transformer.app import build_application

    application = build_application(project_root=project_root)
    application.bootstrap()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
