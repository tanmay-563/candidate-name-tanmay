"""Service wrappers for the deterministic confidence engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate_data_transformer.confidence.engine import ConfidenceEngine
from candidate_data_transformer.models import CandidateRecord, ConfidenceAssessment


@dataclass(slots=True)
class ConfidenceService:
    """Service wrapper around the confidence engine."""

    engine: ConfidenceEngine = field(default_factory=ConfidenceEngine)

    def score_candidate(self, record: CandidateRecord) -> ConfidenceAssessment:
        """Assess confidence for a canonical candidate record."""

        return self.engine.assess(record)


def build_confidence_service() -> ConfidenceService:
    """Create the default confidence service for application wiring."""

    return ConfidenceService()
