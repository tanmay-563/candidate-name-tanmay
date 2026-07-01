"""Service wrapper for the provenance engine."""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate_data_transformer.models import CandidateRecord, ProvenanceEntry
from candidate_data_transformer.provenance.engine import ProvenanceEngine


@dataclass(slots=True)
class ProvenanceService:
    """Service wrapper around the provenance engine."""

    engine: ProvenanceEngine = field(default_factory=ProvenanceEngine)

    def collect_entries(self, record: CandidateRecord) -> list[ProvenanceEntry]:
        """Collect field-level provenance entries for a merged candidate record."""

        return self.engine.collect(record)


def build_provenance_service() -> ProvenanceService:
    """Create the default provenance service for application wiring."""

    return ProvenanceService()
