"""Top-level package for the candidate data transformation scaffold."""

from __future__ import annotations

from candidate_data_transformer.app import Application, build_application


def package_name() -> str:
    """Return the importable package name used by local tooling."""

    return "candidate_data_transformer"


__all__ = ["Application", "build_application", "package_name"]
