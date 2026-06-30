"""Domain model for a candidate's education entry."""

from __future__ import annotations

from dataclasses import dataclass

from candidate_data_transformer.models._validation import (
    normalize_optional_text,
    normalize_year,
)


@dataclass(slots=True)
class Education:
    """Represents a single academic record associated with a candidate."""

    institution: str | None = None
    degree: str | None = None
    field: str | None = None
    end_year: int | None = None

    def __post_init__(self) -> None:
        """Normalize optional text fields and validate the recorded year."""

        self.institution = normalize_optional_text(self.institution, "institution")
        self.degree = normalize_optional_text(self.degree, "degree")
        self.field = normalize_optional_text(self.field, "field")
        self.end_year = normalize_year(self.end_year, "end_year")

    def has_completion_year(self) -> bool:
        """Return whether the education entry includes an end year."""

        return self.end_year is not None

    def display_label(self) -> str:
        """Build a readable label for logging, debugging, or UI display."""

        parts = [value for value in [self.degree, self.field, self.institution] if value]
        return " | ".join(parts)

    def __repr__(self) -> str:
        """Return a concise developer-friendly representation of the education."""

        return (
            "Education("
            f"institution={self.institution!r}, "
            f"degree={self.degree!r}, "
            f"field={self.field!r}, "
            f"end_year={self.end_year!r})"
        )
