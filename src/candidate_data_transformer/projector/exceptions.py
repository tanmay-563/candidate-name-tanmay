"""Custom exceptions used by the projection layer."""

from __future__ import annotations


class ProjectionError(Exception):
    """Base exception for projection-layer failures."""


class ProjectionConfigurationError(ProjectionError):
    """Raised when projection configuration is malformed or unsupported."""


class MissingProjectionValueError(ProjectionError):
    """Raised when a required projected value is missing under ``error`` policy."""
