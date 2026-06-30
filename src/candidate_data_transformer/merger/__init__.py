"""Merging contracts for consolidating canonical candidate records."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Protocol

from candidate_data_transformer.models import CandidateRecord


class MergeStrategy(Protocol):
    """Interface for consolidating multiple canonical records into one."""

    def merge(self, records: Sequence[CandidateRecord]) -> CandidateRecord:
        """Merge multiple canonical candidate records into a single result."""


@dataclass(slots=True)
class MergeService:
    """Service shell for future candidate record consolidation."""

    strategy: MergeStrategy | None = None

    def merge_records(self, records: Sequence[CandidateRecord]) -> CandidateRecord:
        """Merge normalized records into a unified candidate representation."""

        raise NotImplementedError("MergeService.merge_records is not implemented yet.")


def build_merge_service() -> MergeService:
    """Create a placeholder merge service."""

    return MergeService()
