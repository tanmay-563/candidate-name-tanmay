"""Merge engine for consolidating normalized candidate profiles."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from candidate_data_transformer.models import (
    Candidate,
    Education,
    Experience,
    Link,
    ProvenanceEntry,
)
from candidate_data_transformer.utils.source_metadata import (
    best_field_source,
    is_empty_value,
    source_priority,
)


@dataclass(slots=True)
class MergeEngine:
    """Merge multiple normalized candidates into a single canonical candidate."""

    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(
            "candidate_data_transformer.merger.MergeEngine"
        )
    )

    def merge(self, candidates: list[Candidate]) -> Candidate:
        """Merge a list of normalized candidates into one canonical record."""

        if not candidates:
            raise ValueError("At least one candidate is required for merging.")

        for candidate in candidates:
            if not isinstance(candidate, Candidate):
                raise TypeError("All items in candidates must be Candidate instances.")

        self.logger.info("Merging %s candidate record(s).", len(candidates))

        merged_candidate = Candidate(
            candidate_id=self._merge_scalar_field(candidates, "candidate_id"),
            full_name=self._merge_scalar_field(candidates, "full_name"),
            emails=self.merge_emails(candidates),
            phones=self.merge_phones(candidates),
            location=self._merge_scalar_field(candidates, "location"),
            links=self.merge_links(candidates),
            headline=self._merge_scalar_field(candidates, "headline"),
            years_experience=self._merge_scalar_field(candidates, "years_experience"),
            skills=self.merge_skills(candidates),
            experience=self.merge_experience(candidates),
            education=self.merge_education(candidates),
            provenance=self._merge_provenance(candidates),
        )

        self.logger.info(
            "Merged candidate produced with %s email(s), %s phone(s), %s skill(s), "
            "%s experience entry(ies), and %s education entry(ies).",
            len(merged_candidate.emails),
            len(merged_candidate.phones),
            len(merged_candidate.skills),
            len(merged_candidate.experience),
            len(merged_candidate.education),
        )
        return merged_candidate

    def merge_emails(self, candidates: list[Candidate]) -> list[str]:
        """Merge email addresses, removing duplicates while preserving priority order."""

        return self._merge_unique_strings(candidates, field_name="emails")

    def merge_phones(self, candidates: list[Candidate]) -> list[str]:
        """Merge phone numbers, removing duplicates while preserving priority order."""

        return self._merge_unique_strings(candidates, field_name="phones")

    def merge_skills(self, candidates: list[Candidate]) -> list[str]:
        """Merge skills, removing duplicates and returning canonical ordering."""

        merged_skills = self._merge_unique_strings(candidates, field_name="skills")
        return sorted(merged_skills, key=str.casefold)

    def merge_experience(self, candidates: list[Candidate]) -> list[Experience]:
        """Merge experience entries while preserving the highest-priority data."""

        ordered_entries = self._ordered_experience_entries(candidates)
        merged_entries: list[Experience] = []

        for entry in ordered_entries:
            matched_index = self._find_matching_experience_index(merged_entries, entry)

            if matched_index is None:
                merged_entries.append(self._copy_experience(entry))
                continue

            merged_entries[matched_index] = self._merge_experience_entries(
                merged_entries[matched_index],
                entry,
            )

        return merged_entries

    def merge_education(self, candidates: list[Candidate]) -> list[Education]:
        """Merge education entries while preserving the highest-priority data."""

        ordered_entries = self._ordered_education_entries(candidates)
        merged_entries: list[Education] = []

        for entry in ordered_entries:
            matched_index = self._find_matching_education_index(merged_entries, entry)

            if matched_index is None:
                merged_entries.append(self._copy_education(entry))
                continue

            merged_entries[matched_index] = self._merge_education_entries(
                merged_entries[matched_index],
                entry,
            )

        return merged_entries

    def merge_links(self, candidates: list[Candidate]) -> list[Link]:
        """Merge profile links while removing duplicates and preserving priority order."""

        merged_links: list[Link] = []

        for candidate in self._ordered_candidates_for_field(candidates, "links"):
            for link in candidate.links:
                matched_index = self._find_matching_link_index(merged_links, link)

                if matched_index is None:
                    merged_links.append(self._copy_link(link))
                    continue

                merged_links[matched_index] = self._merge_link_entries(
                    merged_links[matched_index],
                    link,
                )

        return merged_links

    def _merge_scalar_field(
        self,
        candidates: list[Candidate],
        field_name: str,
    ) -> str | float | None:
        """Merge a scalar candidate field using source-priority conflict resolution."""

        for candidate in self._ordered_candidates_for_field(candidates, field_name):
            field_value = getattr(candidate, field_name)

            if not is_empty_value(field_value):
                return field_value

        return None

    def _merge_unique_strings(
        self,
        candidates: list[Candidate],
        field_name: str,
    ) -> list[str]:
        """Merge a list of strings while removing duplicates and preserving order."""

        merged_values: list[str] = []
        seen_values: set[str] = set()

        for candidate in self._ordered_candidates_for_field(candidates, field_name):
            for value in getattr(candidate, field_name):
                canonical_key = value.casefold()

                if canonical_key in seen_values:
                    continue

                seen_values.add(canonical_key)
                merged_values.append(value)

        return merged_values

    def _ordered_candidates_for_field(
        self,
        candidates: list[Candidate],
        field_name: str,
    ) -> list[Candidate]:
        """Return candidates ordered by field source priority and input position."""

        indexed_candidates = list(enumerate(candidates))
        indexed_candidates.sort(
            key=lambda item: (
                -source_priority(best_field_source(item[1], field_name)),
                item[0],
            )
        )
        return [candidate for _, candidate in indexed_candidates]

    def _ordered_experience_entries(
        self,
        candidates: list[Candidate],
    ) -> list[Experience]:
        """Return experience entries ordered by candidate source priority."""

        ordered_entries: list[Experience] = []

        for candidate in self._ordered_candidates_for_field(candidates, "experience"):
            ordered_entries.extend(candidate.experience)

        return ordered_entries

    def _ordered_education_entries(
        self,
        candidates: list[Candidate],
    ) -> list[Education]:
        """Return education entries ordered by candidate source priority."""

        ordered_entries: list[Education] = []

        for candidate in self._ordered_candidates_for_field(candidates, "education"):
            ordered_entries.extend(candidate.education)

        return ordered_entries

    def _find_matching_experience_index(
        self,
        existing_entries: list[Experience],
        incoming_entry: Experience,
    ) -> int | None:
        """Find an existing experience entry compatible with the incoming one."""

        for index, existing_entry in enumerate(existing_entries):
            if self._experience_entries_match(existing_entry, incoming_entry):
                return index

        return None

    def _find_matching_education_index(
        self,
        existing_entries: list[Education],
        incoming_entry: Education,
    ) -> int | None:
        """Find an existing education entry compatible with the incoming one."""

        for index, existing_entry in enumerate(existing_entries):
            if self._education_entries_match(existing_entry, incoming_entry):
                return index

        return None

    def _find_matching_link_index(
        self,
        existing_links: list[Link],
        incoming_link: Link,
    ) -> int | None:
        """Find an existing link entry compatible with the incoming one."""

        for index, existing_link in enumerate(existing_links):
            if self._link_entries_match(existing_link, incoming_link):
                return index

        return None

    def _experience_entries_match(
        self,
        left: Experience,
        right: Experience,
    ) -> bool:
        """Return whether two experience entries describe the same role."""

        anchor_match = (
            self._same_non_empty_text(left.company, right.company)
            or self._same_non_empty_text(left.title, right.title)
        )

        if not anchor_match:
            return False

        return (
            self._compatible_text(left.company, right.company)
            and self._compatible_text(left.title, right.title)
            and self._compatible_text(left.start_date, right.start_date)
            and self._compatible_text(left.end_date, right.end_date)
        )

    def _education_entries_match(
        self,
        left: Education,
        right: Education,
    ) -> bool:
        """Return whether two education entries describe the same education record."""

        anchor_match = (
            self._same_non_empty_text(left.institution, right.institution)
            or self._same_non_empty_text(left.degree, right.degree)
            or self._same_non_empty_text(left.field, right.field)
            or (
                left.end_year is not None
                and right.end_year is not None
                and left.end_year == right.end_year
            )
        )

        if not anchor_match:
            return False

        return (
            self._compatible_text(left.institution, right.institution)
            and self._compatible_text(left.degree, right.degree)
            and self._compatible_text(left.field, right.field)
            and self._compatible_scalar(left.end_year, right.end_year)
        )

    def _link_entries_match(self, left: Link, right: Link) -> bool:
        """Return whether two links represent the same destination."""

        if self._same_non_empty_text(left.url, right.url):
            return True

        return (
            self._same_non_empty_text(left.type, right.type)
            and self._compatible_text(left.url, right.url)
        )

    def _merge_experience_entries(
        self,
        primary: Experience,
        secondary: Experience,
    ) -> Experience:
        """Merge two matching experience entries without overwriting primary data."""

        return Experience(
            company=primary.company or secondary.company,
            title=primary.title or secondary.title,
            start_date=primary.start_date or secondary.start_date,
            end_date=primary.end_date or secondary.end_date,
            summary=primary.summary or secondary.summary,
        )

    def _merge_education_entries(
        self,
        primary: Education,
        secondary: Education,
    ) -> Education:
        """Merge two matching education entries without overwriting primary data."""

        return Education(
            institution=primary.institution or secondary.institution,
            degree=primary.degree or secondary.degree,
            field=primary.field or secondary.field,
            end_year=primary.end_year or secondary.end_year,
        )

    def _merge_link_entries(self, primary: Link, secondary: Link) -> Link:
        """Merge two matching links without overwriting primary data."""

        return Link(
            type=primary.type or secondary.type,
            url=primary.url or secondary.url,
        )

    def _merge_provenance(self, candidates: list[Candidate]) -> list[ProvenanceEntry]:
        """Merge provenance entries while preserving input order and uniqueness."""

        merged_entries: list[ProvenanceEntry] = []
        seen_entries: set[tuple[str | None, str | None, str | None]] = set()

        for candidate in candidates:
            for entry in candidate.provenance:
                entry_key = (
                    entry.field.casefold() if entry.field else None,
                    entry.source.casefold() if entry.source else None,
                    entry.method.casefold() if entry.method else None,
                )

                if entry_key in seen_entries:
                    continue

                seen_entries.add(entry_key)
                merged_entries.append(self._copy_provenance(entry))

        return merged_entries

    def _compatible_text(self, left: str | None, right: str | None) -> bool:
        """Return whether two text values are compatible for merging."""

        if left is None or right is None:
            return True

        return left.casefold() == right.casefold()

    def _compatible_scalar(
        self,
        left: int | float | None,
        right: int | float | None,
    ) -> bool:
        """Return whether two scalar values are compatible for merging."""

        if left is None or right is None:
            return True

        return left == right

    def _same_non_empty_text(self, left: str | None, right: str | None) -> bool:
        """Return whether two non-empty text values are equal ignoring case."""

        if left is None or right is None:
            return False

        return left.casefold() == right.casefold()

    def _copy_experience(self, value: Experience) -> Experience:
        """Create a detached copy of an experience entry."""

        return Experience(
            company=value.company,
            title=value.title,
            start_date=value.start_date,
            end_date=value.end_date,
            summary=value.summary,
        )

    def _copy_education(self, value: Education) -> Education:
        """Create a detached copy of an education entry."""

        return Education(
            institution=value.institution,
            degree=value.degree,
            field=value.field,
            end_year=value.end_year,
        )

    def _copy_link(self, value: Link) -> Link:
        """Create a detached copy of a link entry."""

        return Link(type=value.type, url=value.url)

    def _copy_provenance(self, value: ProvenanceEntry) -> ProvenanceEntry:
        """Create a detached copy of a provenance entry."""

        return ProvenanceEntry(
            field=value.field,
            source=value.source,
            method=value.method,
        )
