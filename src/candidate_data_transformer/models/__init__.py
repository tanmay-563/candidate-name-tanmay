"""Domain and support models for the candidate data transformer."""

from __future__ import annotations

from candidate_data_transformer.models.candidate import Candidate
from candidate_data_transformer.models.education import Education
from candidate_data_transformer.models.experience import Experience
from candidate_data_transformer.models.link import Link
from candidate_data_transformer.models.provenance import ProvenanceEntry
from candidate_data_transformer.models.support import (
    ConfidenceAssessment,
    RawCandidatePayload,
    SourceDocument,
    TransformationResult,
    ValidationIssue,
    empty_transformation_result,
)

CandidateRecord = Candidate

__all__ = [
    "Candidate",
    "CandidateRecord",
    "ConfidenceAssessment",
    "Education",
    "Experience",
    "Link",
    "ProvenanceEntry",
    "RawCandidatePayload",
    "SourceDocument",
    "TransformationResult",
    "ValidationIssue",
    "empty_transformation_result",
]
