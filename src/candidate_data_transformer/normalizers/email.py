"""Email normalization utilities for candidate contact data."""

from __future__ import annotations

import re

from candidate_data_transformer.normalizers.base import BaseNormalizer


class EmailNormalizer(BaseNormalizer[str | None, str | None]):
    """Normalize raw email strings into a lowercase canonical format."""

    _EMAIL_PATTERN = re.compile(
        r"^[A-Z0-9._%+\-]+@[A-Z0-9.\-]+\.[A-Z]{2,}$",
        re.IGNORECASE,
    )

    def normalize(self, value: str | None) -> str | None:
        """Trim, lowercase, and validate an email address."""

        if value is None:
            return None

        normalized_value = value.strip().lower()

        if not normalized_value:
            return None

        if not self._EMAIL_PATTERN.fullmatch(normalized_value):
            return None

        return normalized_value
