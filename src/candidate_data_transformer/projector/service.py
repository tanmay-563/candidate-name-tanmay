"""Service wrappers for configurable output projection."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from candidate_data_transformer.models import (
    CandidateRecord,
    ConfidenceAssessment,
    ProvenanceEntry,
)
from candidate_data_transformer.projector.config import ProjectionConfig
from candidate_data_transformer.projector.engine import ConfigurableProjector


@dataclass(slots=True)
class ProjectionService:
    """Service wrapper around the configurable projection engine."""

    projector: ConfigurableProjector = field(default_factory=ConfigurableProjector)

    def project_candidate(
        self,
        record: CandidateRecord,
        config: ProjectionConfig | Path,
        *,
        confidence: ConfidenceAssessment | None = None,
        provenance: list[ProvenanceEntry] | None = None,
    ) -> Mapping[str, Any]:
        """Project a canonical candidate record into a configured output payload."""

        return self.projector.project(
            record,
            config,
            confidence=confidence,
            provenance=provenance,
        )


def build_projection_service() -> ProjectionService:
    """Create the default projection service for application wiring."""

    return ProjectionService()
