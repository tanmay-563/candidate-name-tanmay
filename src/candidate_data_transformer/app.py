"""Application composition layer for wiring the project scaffold together."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from candidate_data_transformer.config import AppSettings, load_settings
from candidate_data_transformer.pipeline import (
    CandidateTransformationPipeline,
    build_pipeline,
)
from candidate_data_transformer.utils import configure_logging


@dataclass(slots=True)
class Application:
    """Lightweight application shell that holds shared runtime dependencies."""

    settings: AppSettings
    pipeline: CandidateTransformationPipeline
    logger: logging.Logger

    def bootstrap(self) -> None:
        """Prepare the application shell for future runtime execution."""

        self.logger.debug("Application bootstrap completed.")


def build_application(project_root: Path | None = None) -> Application:
    """Construct the application shell with default placeholder dependencies."""

    settings = load_settings(project_root=project_root)
    logger = configure_logging()
    pipeline = build_pipeline()
    return Application(settings=settings, pipeline=pipeline, logger=logger)
