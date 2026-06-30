"""Domain model for a candidate's professional experience entry."""

from __future__ import annotations

from dataclasses import dataclass

from candidate_data_transformer.models._validation import normalize_optional_text


@dataclass(slots=True)
class Experience:
    """Represents a single work experience associated with a candidate."""

    company: str | None = None
    title: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    summary: str | None = None

    def __post_init__(self) -> None:
        """Normalize optional text fields captured for the experience entry."""

        self.company = normalize_optional_text(self.company, "company")
        self.title = normalize_optional_text(self.title, "title")
        self.start_date = normalize_optional_text(self.start_date, "start_date")
        self.end_date = normalize_optional_text(self.end_date, "end_date")
        self.summary = normalize_optional_text(self.summary, "summary")

    def is_current(self) -> bool:
        """Return whether the experience appears to describe a current role."""

        return self.end_date is None

    def has_summary(self) -> bool:
        """Return whether the experience includes descriptive summary text."""

        return self.summary is not None

    def __repr__(self) -> str:
        """Return a concise developer-friendly representation of the experience."""

        return (
            "Experience("
            f"company={self.company!r}, "
            f"title={self.title!r}, "
            f"start_date={self.start_date!r}, "
            f"end_date={self.end_date!r})"
        )
