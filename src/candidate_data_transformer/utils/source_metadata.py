"""Shared source-priority and provenance helpers used by pipeline engines."""

from __future__ import annotations

from collections.abc import Iterable

from candidate_data_transformer.models import Candidate

CANONICAL_SOURCE_PRIORITY: dict[str, int] = {
    "Missing": 0,
    "Unknown": 1,
    "GitHub": 2,
    "Recruiter CSV": 3,
}

CANONICAL_SOURCE_CONFIDENCE: dict[str, float] = {
    "Missing": 0.00,
    "Unknown": 0.50,
    "GitHub": 0.80,
    "Recruiter CSV": 0.95,
}

FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "candidate_id": ("candidate_id", "candidate id", "id"),
    "full_name": ("full_name", "full name", "name"),
    "emails": ("emails", "email"),
    "phones": ("phones", "phone", "mobile"),
    "location": ("location",),
    "links": ("links", "link", "url", "profile"),
    "headline": ("headline", "bio", "summary"),
    "years_experience": ("years_experience", "years experience", "experience_years"),
    "skills": ("skills", "skill", "languages"),
    "experience": ("experience", "work_experience", "employment"),
    "education": ("education", "academic", "studies"),
}


def canonical_source_name(source_name: str | None) -> str:
    """Convert a raw source label into one of the engine's canonical source names."""

    if source_name is None:
        return "Unknown"

    cleaned_source_name = source_name.strip()

    if not cleaned_source_name:
        return "Unknown"

    lowered_source_name = cleaned_source_name.casefold()

    if lowered_source_name == "missing":
        return "Missing"

    if lowered_source_name == "unknown":
        return "Unknown"

    if "recruiter" in lowered_source_name and "csv" in lowered_source_name:
        return "Recruiter CSV"

    if "github" in lowered_source_name:
        return "GitHub"

    return "Unknown"


def source_priority(source_name: str | None) -> int:
    """Return the merge priority associated with a source label."""

    return CANONICAL_SOURCE_PRIORITY[canonical_source_name(source_name)]


def source_confidence(source_name: str | None) -> float:
    """Return the deterministic confidence associated with a source label."""

    return CANONICAL_SOURCE_CONFIDENCE[canonical_source_name(source_name)]


def is_empty_value(value: object) -> bool:
    """Return whether a value should be treated as empty during engine processing."""

    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    if isinstance(value, (list, tuple, set, frozenset, dict)):
        return len(value) == 0

    return False


def field_aliases(field_name: str) -> tuple[str, ...]:
    """Return the accepted provenance aliases for a candidate field name."""

    return FIELD_ALIASES.get(field_name, (field_name,))


def field_sources(candidate: Candidate, field_name: str) -> list[str]:
    """Collect canonical provenance sources associated with a candidate field."""

    aliases = {alias.casefold() for alias in field_aliases(field_name)}
    sources: list[str] = []
    seen_sources: set[str] = set()

    for entry in candidate.provenance:
        if entry.field is None:
            continue

        if entry.field.casefold() not in aliases:
            continue

        canonical_source = canonical_source_name(entry.source)

        if canonical_source in seen_sources:
            continue

        seen_sources.add(canonical_source)
        sources.append(canonical_source)

    return sources


def best_field_source(candidate: Candidate, field_name: str) -> str:
    """Return the highest-priority provenance source for a candidate field."""

    sources = field_sources(candidate, field_name)

    if not sources:
        field_value = getattr(candidate, field_name, None)

        if is_empty_value(field_value):
            return "Missing"

        return "Unknown"

    return max(sources, key=source_priority)
