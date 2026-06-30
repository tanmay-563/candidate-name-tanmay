"""Domain model for a candidate-related external link."""

from __future__ import annotations

from dataclasses import dataclass

from candidate_data_transformer.models._validation import normalize_optional_text


@dataclass(slots=True)
class Link:
    """Represents an external profile or reference URL associated with a candidate."""

    type: str | None = None
    url: str | None = None

    def __post_init__(self) -> None:
        """Normalize optional text fields and validate the link shape."""

        self.type = normalize_optional_text(self.type, "type")
        self.url = normalize_optional_text(self.url, "url")

    def is_type(self, link_type: str) -> bool:
        """Return whether the link matches the provided link type label."""

        if self.type is None:
            return False

        return self.type.casefold() == link_type.strip().casefold()

    def is_complete(self) -> bool:
        """Return whether the link contains both a type and a URL."""

        return self.type is not None and self.url is not None

    def __repr__(self) -> str:
        """Return a concise developer-friendly representation of the link."""

        return f"Link(type={self.type!r}, url={self.url!r})"
