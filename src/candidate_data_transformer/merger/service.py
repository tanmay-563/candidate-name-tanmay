"""Service wrappers for the candidate merge engine."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field

from candidate_data_transformer.merger.engine import MergeEngine
from candidate_data_transformer.models import CandidateRecord


@dataclass(slots=True)
class MergeService:
    """Service wrapper around the merge engine."""

    engine: MergeEngine = field(default_factory=MergeEngine)

    def merge_records(self, records: Sequence[CandidateRecord]) -> CandidateRecord:
        """Merge normalized candidate records into a canonical record."""

        return self.engine.merge(list(records))


def build_merge_service() -> MergeService:
    """Create the default merge service for application wiring."""

    return MergeService()
