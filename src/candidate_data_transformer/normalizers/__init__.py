"""Normalization contracts for mapping parsed documents into canonical records."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Protocol

from candidate_data_transformer.models import CandidateRecord, SourceDocument


class CandidateNormalizer(Protocol):
    """Interface for transforming parsed source documents into canonical records."""

    def normalize(self, document: SourceDocument) -> CandidateRecord:
        """Normalize a parsed source document into a canonical candidate record."""


@dataclass(slots=True)
class NormalizationService:
    """Service shell for coordinating future normalization workflows."""

    normalizers: dict[str, CandidateNormalizer] = field(default_factory=dict)

    def register(self, source_name: str, normalizer: CandidateNormalizer) -> None:
        """Register a normalizer for a named source."""

        self.normalizers[source_name] = normalizer

    def normalize_documents(
        self,
        documents: Sequence[SourceDocument],
    ) -> list[CandidateRecord]:
        """Normalize parsed documents into canonical candidate records."""

        raise NotImplementedError(
            "NormalizationService.normalize_documents is not implemented yet."
        )


def build_normalization_service() -> NormalizationService:
    """Create a placeholder normalization service."""

    return NormalizationService()
