"""Domain model for field-level provenance metadata."""

from __future__ import annotations

from dataclasses import dataclass

from candidate_data_transformer.models._validation import normalize_optional_text


@dataclass(slots=True)
class ProvenanceEntry:
    """Represents how a specific candidate field was obtained."""

    field: str | None = None
    source: str | None = None
    method: str | None = None

    def __post_init__(self) -> None:
        """Normalize optional provenance metadata captured for a field."""

        self.field = normalize_optional_text(self.field, "field")
        self.source = normalize_optional_text(self.source, "source")
        self.method = normalize_optional_text(self.method, "method")

    def matches_field(self, field_name: str) -> bool:
        """Return whether the provenance entry describes the provided field name."""

        if self.field is None:
            return False

        return self.field == field_name.strip()

    def is_complete(self) -> bool:
        """Return whether the provenance entry has all expected metadata."""

        return (
            self.field is not None
            and self.source is not None
            and self.method is not None
        )

    def __repr__(self) -> str:
        """Return a concise developer-friendly representation of the provenance."""

        return (
            "ProvenanceEntry("
            f"field={self.field!r}, "
            f"source={self.source!r}, "
            f"method={self.method!r})"
        )
