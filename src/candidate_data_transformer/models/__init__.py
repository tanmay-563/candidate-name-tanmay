"""Domain models shared across the candidate transformation pipeline."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class RawCandidatePayload:
    """Raw candidate payload received from an upstream data source."""

    source_name: str
    payload: Mapping[str, Any]


@dataclass(slots=True)
class SourceDocument:
    """Structured representation emitted by a source parser."""

    source_name: str
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class CandidateRecord:
    """Canonical candidate record shared across transformation stages."""

    candidate_id: str | None = None
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ProvenanceEntry:
    """Field-level provenance metadata for a transformed candidate record."""

    field_name: str
    source_name: str
    evidence: str | None = None


@dataclass(slots=True)
class ConfidenceAssessment:
    """Confidence metadata produced for a transformed candidate record."""

    overall_score: float | None = None
    field_scores: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class ValidationIssue:
    """Validation issue raised during candidate quality checks."""

    code: str
    message: str
    field_name: str | None = None
    severity: str = "error"


@dataclass(slots=True)
class TransformationResult:
    """Aggregate return type for the end-to-end transformation pipeline."""

    candidate: CandidateRecord | None = None
    projected_payload: dict[str, Any] | None = None
    confidence: ConfidenceAssessment | None = None
    provenance: list[ProvenanceEntry] = field(default_factory=list)
    validation_issues: list[ValidationIssue] = field(default_factory=list)


def empty_transformation_result() -> TransformationResult:
    """Create an empty pipeline result placeholder."""

    return TransformationResult()
