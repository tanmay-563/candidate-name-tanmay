"""Location normalization utilities for candidate profile data."""

from __future__ import annotations

import re

from candidate_data_transformer.normalizers.base import BaseNormalizer


class LocationNormalizer(BaseNormalizer[str | None, str | None]):
    """Normalize raw location text into a canonical comma-separated format."""

    _WHITESPACE_PATTERN = re.compile(r"\s+")

    def normalize(self, value: str | None) -> str | None:
        """Normalize a location into ordered location components when possible."""

        if value is None:
            return None

        stripped_value = value.strip()

        if not stripped_value:
            return None

        parts: list[str] = []

        for part in stripped_value.split(","):
            normalized_part = self._normalize_part(part)

            if normalized_part is not None:
                parts.append(normalized_part)

        if not parts:
            return None

        if len(parts) == 1:
            return parts[0]

        return ", ".join(parts)

    def _normalize_part(self, value: str) -> str | None:
        """Normalize a single location component."""

        normalized_value = self._WHITESPACE_PATTERN.sub(" ", value.strip())
        return normalized_value or None
