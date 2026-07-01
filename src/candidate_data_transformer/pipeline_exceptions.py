"""Custom exceptions used by the integrated pipeline orchestrator."""

from __future__ import annotations


class PipelineError(Exception):
    """Base exception for pipeline orchestration failures."""


class PipelineConfigurationError(PipelineError):
    """Raised when runtime pipeline configuration is invalid."""


class PipelineInputError(PipelineError):
    """Raised when no usable input sources can be processed."""


class PipelineProcessingError(PipelineError):
    """Raised when pipeline processing fails after input loading."""


class PipelineOutputError(PipelineError):
    """Raised when projection or schema validation fails."""
