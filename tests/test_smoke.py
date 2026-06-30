"""Smoke tests for the project scaffold."""

from __future__ import annotations

from pathlib import Path

from candidate_data_transformer.app import build_application
from candidate_data_transformer.config import load_settings


def test_load_settings_uses_explicit_project_root() -> None:
    """Ensure settings resolve expected repository directories."""

    explicit_project_root = Path(__file__).resolve().parent.parent
    settings = load_settings(project_root=explicit_project_root)

    assert settings.project_root == explicit_project_root
    assert settings.source_directory == explicit_project_root / "src"
    assert settings.data_directory == explicit_project_root / "data"


def test_build_application_creates_pipeline_shell() -> None:
    """Ensure the application shell can be composed without business logic."""

    application = build_application(project_root=Path(__file__).resolve().parent.parent)

    assert application.settings.project_root.name == "candidate-name-tanmay"
    assert application.pipeline.parser_registry is not None
