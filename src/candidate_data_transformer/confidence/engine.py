"""Confidence engine for deterministic candidate field scoring."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Mapping

from candidate_data_transformer.models import Candidate, ConfidenceAssessment
from candidate_data_transformer.utils.source_metadata import (
    best_field_source,
    is_empty_value,
    source_confidence,
)


@dataclass(slots=True)
class ConfidenceEngine:
    """Calculate deterministic confidence scores for candidate fields."""

    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(
            "candidate_data_transformer.confidence.ConfidenceEngine"
        )
    )
    tracked_fields: tuple[str, ...] = (
        "candidate_id",
        "full_name",
        "emails",
        "phones",
        "location",
        "links",
        "headline",
        "years_experience",
        "skills",
        "experience",
        "education",
    )

    def calculate_field_confidence(self, value: object, source: str | None) -> float:
        """Calculate a deterministic confidence score for a single field value."""

        if is_empty_value(value):
            return 0.00

        return source_confidence(source)

    def calculate_candidate_confidence(self, candidate: Candidate) -> dict[str, float]:
        """Calculate confidence scores for all tracked fields on a candidate."""

        if not isinstance(candidate, Candidate):
            raise TypeError("candidate must be an instance of Candidate.")

        field_scores: dict[str, float] = {}

        for field_name in self.tracked_fields:
            field_value = getattr(candidate, field_name)
            field_source = best_field_source(candidate, field_name)
            field_scores[field_name] = self.calculate_field_confidence(
                value=field_value,
                source=field_source,
            )

        self.logger.info(
            "Calculated confidence for %s tracked field(s).",
            len(field_scores),
        )
        return field_scores

    def overall_confidence(self, field_scores: Mapping[str, float]) -> float:
        """Calculate the overall candidate confidence from field-level scores."""

        if not field_scores:
            return 0.00

        overall_score = sum(field_scores.values()) / len(field_scores)
        return round(overall_score, 4)

    def assess(self, candidate: Candidate) -> ConfidenceAssessment:
        """Calculate full confidence assessment metadata for a candidate."""

        field_scores = self.calculate_candidate_confidence(candidate)
        overall_score = self.overall_confidence(field_scores)
        self.logger.info("Calculated overall candidate confidence of %.4f.", overall_score)
        return ConfidenceAssessment(
            overall_score=overall_score,
            field_scores=dict(field_scores),
        )
