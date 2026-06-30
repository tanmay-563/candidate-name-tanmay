"""Candidate-level orchestration for normalization of profile data."""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate_data_transformer.models import (
    Candidate,
    Education,
    Experience,
    Link,
    ProvenanceEntry,
)
from candidate_data_transformer.normalizers.base import BaseNormalizer
from candidate_data_transformer.normalizers.date import DateNormalizer
from candidate_data_transformer.normalizers.email import EmailNormalizer
from candidate_data_transformer.normalizers.location import LocationNormalizer
from candidate_data_transformer.normalizers.phone import PhoneNormalizer
from candidate_data_transformer.normalizers.skill import SkillNormalizer


@dataclass(slots=True)
class CandidateNormalizer(BaseNormalizer[Candidate, Candidate]):
    """Normalize a candidate profile into a clean canonical representation."""

    email_normalizer: BaseNormalizer[str | None, str | None] = field(
        default_factory=EmailNormalizer
    )
    phone_normalizer: BaseNormalizer[str | None, str | None] = field(
        default_factory=PhoneNormalizer
    )
    skill_normalizer: BaseNormalizer[str | None, str | None] = field(
        default_factory=SkillNormalizer
    )
    date_normalizer: BaseNormalizer[str | int | None, str | None] = field(
        default_factory=DateNormalizer
    )
    location_normalizer: BaseNormalizer[str | None, str | None] = field(
        default_factory=LocationNormalizer
    )

    def normalize(self, value: Candidate) -> Candidate:
        """Return a normalized copy of the provided candidate."""

        if not isinstance(value, Candidate):
            raise TypeError("value must be an instance of Candidate.")

        return Candidate(
            candidate_id=value.candidate_id,
            full_name=value.full_name,
            emails=self._normalize_unique_strings(
                values=value.emails,
                normalizer=self.email_normalizer,
            ),
            phones=self._normalize_unique_strings(
                values=value.phones,
                normalizer=self.phone_normalizer,
            ),
            location=self.location_normalizer.normalize(value.location),
            links=self._copy_links(value.links),
            headline=value.headline,
            years_experience=value.years_experience,
            skills=self._normalize_unique_strings(
                values=value.skills,
                normalizer=self.skill_normalizer,
            ),
            experience=self._normalize_experience_entries(value.experience),
            education=self._copy_education_entries(value.education),
            provenance=self._copy_provenance_entries(value.provenance),
            overall_confidence=value.overall_confidence,
        )

    def _normalize_unique_strings(
        self,
        values: list[str],
        normalizer: BaseNormalizer[str | None, str | None],
    ) -> list[str]:
        """Normalize, filter, and deduplicate string values while preserving order."""

        normalized_values: list[str] = []
        seen_values: set[str] = set()

        for value in values:
            normalized_value = normalizer.normalize(value)

            if normalized_value is None:
                continue

            canonical_key = normalized_value.casefold()

            if canonical_key in seen_values:
                continue

            seen_values.add(canonical_key)
            normalized_values.append(normalized_value)

        return normalized_values

    def _normalize_experience_entries(
        self,
        entries: list[Experience],
    ) -> list[Experience]:
        """Normalize date fields across candidate experience entries."""

        return [
            Experience(
                company=entry.company,
                title=entry.title,
                start_date=self.date_normalizer.normalize(entry.start_date),
                end_date=self.date_normalizer.normalize(entry.end_date),
                summary=entry.summary,
            )
            for entry in entries
        ]

    def _copy_education_entries(
        self,
        entries: list[Education],
    ) -> list[Education]:
        """Create detached copies of education entries for the normalized output."""

        return [
            Education(
                institution=entry.institution,
                degree=entry.degree,
                field=entry.field,
                end_year=entry.end_year,
            )
            for entry in entries
        ]

    def _copy_links(self, links: list[Link]) -> list[Link]:
        """Create detached copies of link entries for the normalized output."""

        return [Link(type=link.type, url=link.url) for link in links]

    def _copy_provenance_entries(
        self,
        entries: list[ProvenanceEntry],
    ) -> list[ProvenanceEntry]:
        """Create detached copies of provenance entries without modification."""

        return [
            ProvenanceEntry(
                field=entry.field,
                source=entry.source,
                method=entry.method,
            )
            for entry in entries
        ]
