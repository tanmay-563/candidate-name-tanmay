"""Projection layer components for configurable output payload generation."""

from __future__ import annotations

from candidate_data_transformer.projector.config import (
    ProjectionConfig,
    ProjectionConfigLoader,
    ProjectionFieldConfig,
)
from candidate_data_transformer.projector.engine import (
    ConfigurableProjector,
    ProjectionEngine,
)
from candidate_data_transformer.projector.exceptions import (
    MissingProjectionValueError,
    ProjectionConfigurationError,
    ProjectionError,
)
from candidate_data_transformer.projector.service import (
    ProjectionService,
    build_projection_service,
)

__all__ = [
    "ConfigurableProjector",
    "MissingProjectionValueError",
    "ProjectionConfig",
    "ProjectionConfigLoader",
    "ProjectionConfigurationError",
    "ProjectionEngine",
    "ProjectionError",
    "ProjectionFieldConfig",
    "ProjectionService",
    "build_projection_service",
]
