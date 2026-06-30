"""Supporting pipeline dataclasses that wrap the canonical domain models."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from candidate_data_transformer.models.candidate import Candidate
from candidate_data_transformer.models.provenance import ProvenanceEntry


@dataclass(slots=True)
class RawCandidatePayload:
    """Raw candidate payload received from an upstream data source."""

    source_name: str
    payload: Mapping[str, Any]

    def __post_init__(self) -> None:
        """Validate the basic shape of the raw source payload wrapper."""

        if not isinstance(self.source_name, str) or not self.source_name.strip():
            raise ValueError("source_name must be a non-empty string.")

        if not isinstance(self.payload, Mapping):
            raise TypeError("payload must implement the Mapping interface.")


@dataclass(slots=True)
class SourceDocument:
    """Structured representation emitted by a future source parser."""

    source_name: str
    attributes: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate the basic shape of the parsed source document."""

        if not isinstance(self.source_name, str) or not self.source_name.strip():
            raise ValueError("source_name must be a non-empty string.")

        if not isinstance(self.attributes, dict):
            raise TypeError("attributes must be a dictionary.")


@dataclass(slots=True)
class ConfidenceAssessment:
    """Confidence metadata produced for a transformed candidate record."""

    overall_score: float | None = None
    field_scores: dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate confidence score containers used by later pipeline stages."""

        if self.overall_score is not None and not isinstance(
            self.overall_score,
            (int, float),
        ):
            raise TypeError("overall_score must be numeric or None.")

        if not isinstance(self.field_scores, dict):
            raise TypeError("field_scores must be a dictionary.")


@dataclass(slots=True)
class ValidationIssue:
    """Validation issue raised during candidate quality checks."""

    code: str
    message: str
    field_name: str | None = None
    severity: str = "error"

    def __post_init__(self) -> None:
        """Validate required metadata for a validation issue."""

        if not isinstance(self.code, str) or not self.code.strip():
            raise ValueError("code must be a non-empty string.")

        if not isinstance(self.message, str) or not self.message.strip():
            raise ValueError("message must be a non-empty string.")

        if self.field_name is not None and not isinstance(self.field_name, str):
            raise TypeError("field_name must be a string or None.")

        if not isinstance(self.severity, str) or not self.severity.strip():
            raise ValueError("severity must be a non-empty string.")


@dataclass(slots=True)
class TransformationResult:
    """Aggregate return type for the end-to-end transformation pipeline."""

    candidate: Candidate | None = None
    projected_payload: dict[str, Any] | None = None
    confidence: ConfidenceAssessment | None = None
    provenance: list[ProvenanceEntry] = field(default_factory=list)
    validation_issues: list[ValidationIssue] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Validate container types used by the transformation result."""

        if self.candidate is not None and not isinstance(self.candidate, Candidate):
            raise TypeError("candidate must be an instance of Candidate or None.")

        if self.projected_payload is not None and not isinstance(
            self.projected_payload,
            dict,
        ):
            raise TypeError("projected_payload must be a dictionary or None.")

        if self.confidence is not None and not isinstance(
            self.confidence,
            ConfidenceAssessment,
        ):
            raise TypeError(
                "confidence must be an instance of ConfidenceAssessment or None."
            )

        if any(
            not isinstance(entry, ProvenanceEntry) for entry in self.provenance
        ):
            raise TypeError("provenance must contain ProvenanceEntry instances only.")

        if any(
            not isinstance(issue, ValidationIssue) for issue in self.validation_issues
        ):
            raise TypeError(
                "validation_issues must contain ValidationIssue instances only."
            )


def empty_transformation_result() -> TransformationResult:
    """Create an empty transformation result placeholder."""

    return TransformationResult()
