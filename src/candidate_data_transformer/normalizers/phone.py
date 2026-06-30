"""Phone number normalization utilities for candidate contact data."""

from __future__ import annotations

import re

from candidate_data_transformer.normalizers.base import BaseNormalizer


class PhoneNormalizer(BaseNormalizer[str | None, str | None]):
    """Normalize raw phone numbers into E.164 format when possible."""

    _SEPARATOR_PATTERN = re.compile(r"[\s().-]+")
    _INDIAN_MOBILE_START_DIGITS = frozenset({"6", "7", "8", "9"})
    _MIN_E164_DIGITS = 10
    _MAX_E164_DIGITS = 15

    def normalize(self, value: str | None) -> str | None:
        """Normalize a phone number and return an E.164-compatible value."""

        if value is None:
            return None

        raw_value = value.strip()

        if not raw_value:
            return None

        cleaned_value = self._SEPARATOR_PATTERN.sub("", raw_value)

        if cleaned_value.startswith("00"):
            cleaned_value = f"+{cleaned_value[2:]}"

        if cleaned_value.startswith("+"):
            return self._normalize_international_number(cleaned_value)

        if not cleaned_value.isdigit():
            return None

        if self._is_indian_mobile_number(cleaned_value):
            return f"+91{cleaned_value}"

        if (
            len(cleaned_value) == 11
            and cleaned_value.startswith("0")
            and self._is_indian_mobile_number(cleaned_value[1:])
        ):
            return f"+91{cleaned_value[1:]}"

        if (
            len(cleaned_value) == 12
            and cleaned_value.startswith("91")
            and self._is_indian_mobile_number(cleaned_value[2:])
        ):
            return f"+{cleaned_value}"

        return None

    def _normalize_international_number(self, value: str) -> str | None:
        """Validate and normalize an explicitly international number."""

        digits = value[1:]

        if not digits.isdigit():
            return None

        if not self._MIN_E164_DIGITS <= len(digits) <= self._MAX_E164_DIGITS:
            return None

        if digits.startswith("91") and len(digits) == 12:
            if not self._is_indian_mobile_number(digits[2:]):
                return None

        return f"+{digits}"

    def _is_indian_mobile_number(self, value: str) -> bool:
        """Return whether a value matches a valid Indian mobile number shape."""

        return (
            len(value) == 10
            and value.isdigit()
            and value[0] in self._INDIAN_MOBILE_START_DIGITS
        )
