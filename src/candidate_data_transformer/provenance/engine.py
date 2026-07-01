"""Provenance engine for synthesizing final field-level origin metadata."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from candidate_data_transformer.models import Candidate, ProvenanceEntry
from candidate_data_transformer.utils.source_metadata import (
    field_sources,
    is_empty_value,
    source_priority,
)


@dataclass(slots=True)
class ProvenanceEngine:
    """Create final field-level provenance entries for a merged candidate."""

    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(
            "candidate_data_transformer.provenance.ProvenanceEngine"
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

    def collect(self, record: Candidate) -> list[ProvenanceEntry]:
        """Collect final provenance entries for all tracked candidate fields."""

        if not isinstance(record, Candidate):
            raise TypeError("record must be an instance of Candidate.")

        collected_entries: list[ProvenanceEntry] = []

        for field_name in self.tracked_fields:
            collected_entries.extend(self.collect_field_entries(record, field_name))

        self.logger.info(
            "Collected %s provenance entry(ies) for %s tracked field(s).",
            len(collected_entries),
            len(self.tracked_fields),
        )
        return collected_entries

    def collect_field_entries(
        self,
        record: Candidate,
        field_name: str,
    ) -> list[ProvenanceEntry]:
        """Collect final provenance entries for a specific candidate field."""

        if not hasattr(record, field_name):
            raise ValueError(f"Candidate does not expose a field named '{field_name}'.")

        field_value = getattr(record, field_name)
        sources = field_sources(record, field_name)

        if sources:
            ordered_sources = sorted(
                sources,
                key=lambda source_name: (-source_priority(source_name), source_name),
            )
            return [
                ProvenanceEntry(
                    field=field_name,
                    source=source_name,
                    method="merged",
                )
                for source_name in ordered_sources
            ]

        if is_empty_value(field_value):
            return [
                ProvenanceEntry(
                    field=field_name,
                    source="Missing",
                    method="missing",
                )
            ]

        return [
            ProvenanceEntry(
                field=field_name,
                source="Unknown",
                method="merged",
            )
        ]
