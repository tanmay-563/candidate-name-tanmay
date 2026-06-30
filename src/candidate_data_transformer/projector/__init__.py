"""Projection contracts for mapping internal records into downstream payloads."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from candidate_data_transformer.models import CandidateRecord


class CandidateProjector(Protocol):
    """Interface for projecting canonical records into output schemas."""

    def project(self, record: CandidateRecord) -> dict[str, Any]:
        """Project a canonical candidate record into a downstream payload."""


@dataclass(slots=True)
class ProjectionService:
    """Service shell for future downstream payload projection."""

    projector: CandidateProjector | None = None

    def project_candidate(self, record: CandidateRecord) -> Mapping[str, Any]:
        """Project a canonical candidate record into an output contract."""

        raise NotImplementedError(
            "ProjectionService.project_candidate is not implemented yet."
        )


def build_projection_service() -> ProjectionService:
    """Create a placeholder projection service."""

    return ProjectionService()
