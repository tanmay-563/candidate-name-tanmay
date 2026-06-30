"""Provenance contracts for tracing where transformed candidate fields originated."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from candidate_data_transformer.models import CandidateRecord, ProvenanceEntry


class ProvenanceTracker(Protocol):
    """Interface for collecting provenance details from candidate data."""

    def collect(self, record: CandidateRecord) -> list[ProvenanceEntry]:
        """Collect provenance entries for a canonical candidate record."""


@dataclass(slots=True)
class ProvenanceService:
    """Service shell for future field-level provenance tracking."""

    tracker: ProvenanceTracker | None = None

    def collect_entries(self, record: CandidateRecord) -> list[ProvenanceEntry]:
        """Collect provenance entries for a merged candidate record."""

        raise NotImplementedError(
            "ProvenanceService.collect_entries is not implemented yet."
        )


def build_provenance_service() -> ProvenanceService:
    """Create a placeholder provenance service."""

    return ProvenanceService()
