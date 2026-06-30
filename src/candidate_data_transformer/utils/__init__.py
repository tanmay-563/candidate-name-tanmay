"""Shared infrastructure utilities for the project scaffold."""

from __future__ import annotations

import logging
from dataclasses import dataclass


@dataclass(slots=True)
class RuntimeMetadata:
    """Small runtime metadata container for future operational concerns."""

    service_name: str = "candidate_data_transformer"
    environment_name: str = "development"


def configure_logging(level: int = logging.INFO) -> logging.Logger:
    """Return a package logger configured for early-stage development use."""

    logger = logging.getLogger("candidate_data_transformer")

    if not logger.handlers:
        logger.addHandler(logging.NullHandler())

    logger.setLevel(level)
    return logger
