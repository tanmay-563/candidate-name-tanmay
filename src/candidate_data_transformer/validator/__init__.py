"""Validation contracts for assessing quality and completeness of candidate data."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from candidate_data_transformer.models import CandidateRecord, ValidationIssue


class CandidateValidator(Protocol):
    """Interface for validating canonical candidate records."""

    def validate(self, record: CandidateRecord) -> list[ValidationIssue]:
        """Validate a canonical candidate record and report any issues."""


@dataclass(slots=True)
class ValidationService:
    """Service shell for future validation workflows."""

    validator: CandidateValidator | None = None

    def validate_candidate(self, record: CandidateRecord) -> list[ValidationIssue]:
        """Validate a canonical candidate record."""

        raise NotImplementedError(
            "ValidationService.validate_candidate is not implemented yet."
        )


def build_validation_service() -> ValidationService:
    """Create a placeholder validation service."""

    return ValidationService()
