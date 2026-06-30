"""Service wrappers for applying candidate normalization across collections."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from candidate_data_transformer.models import Candidate
from candidate_data_transformer.normalizers.candidate import CandidateNormalizer


@dataclass(slots=True)
class NormalizationService:
    """Coordinate normalization across one or more candidate profiles."""

    candidate_normalizer: CandidateNormalizer = field(default_factory=CandidateNormalizer)

    def normalize_candidate(self, candidate: Candidate) -> Candidate:
        """Normalize a single candidate profile."""

        return self.candidate_normalizer.normalize(candidate)

    def normalize_candidates(self, candidates: Sequence[Candidate]) -> list[Candidate]:
        """Normalize a sequence of candidate profiles."""

        return [self.normalize_candidate(candidate) for candidate in candidates]

    def normalize_documents(self, documents: Sequence[Candidate]) -> list[Candidate]:
        """Normalize candidate records using the service's configured normalizer."""

        return self.normalize_candidates(documents)


def build_normalization_service() -> NormalizationService:
    """Create the default normalization service for application wiring."""

    return NormalizationService()
