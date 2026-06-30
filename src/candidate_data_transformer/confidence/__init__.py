"""Confidence scoring contracts for assessing transformed candidate data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from candidate_data_transformer.models import CandidateRecord, ConfidenceAssessment


class ConfidenceScorer(Protocol):
    """Interface for assessing confidence in transformed candidate records."""

    def assess(self, record: CandidateRecord) -> ConfidenceAssessment:
        """Generate a confidence assessment for a canonical candidate record."""


@dataclass(slots=True)
class ConfidenceService:
    """Service shell for future candidate confidence scoring."""

    scorer: ConfidenceScorer | None = None

    def score_candidate(self, record: CandidateRecord) -> ConfidenceAssessment:
        """Assess confidence for a canonical candidate record."""

        raise NotImplementedError(
            "ConfidenceService.score_candidate is not implemented yet."
        )


def build_confidence_service() -> ConfidenceService:
    """Create a placeholder confidence scoring service."""

    return ConfidenceService()
