"""Date normalization utilities for canonical candidate timeline fields."""

from __future__ import annotations

import re
from datetime import datetime

from candidate_data_transformer.normalizers.base import BaseNormalizer


class DateNormalizer(BaseNormalizer[str | int | None, str | None]):
    """Normalize raw date values into year or year-month string formats."""

    _YEAR_PATTERN = re.compile(r"^(?P<year>\d{4})$")
    _YEAR_MONTH_PATTERN = re.compile(
        r"^(?P<year>\d{4})[-/.\s](?P<month>\d{1,2})(?:[-/.\s]\d{1,2})?$"
    )
    _MONTH_YEAR_PATTERN = re.compile(
        r"^(?P<month>\d{1,2})[-/.\s](?P<year>\d{4})$"
    )
    _TEXTUAL_MONTH_YEAR_PATTERN = re.compile(
        r"^(?P<month>[A-Za-z]+)[,\s-]+(?P<year>\d{4})$"
    )
    _MONTH_LOOKUP = {
        "jan": 1,
        "january": 1,
        "feb": 2,
        "february": 2,
        "mar": 3,
        "march": 3,
        "apr": 4,
        "april": 4,
        "may": 5,
        "jun": 6,
        "june": 6,
        "jul": 7,
        "july": 7,
        "aug": 8,
        "august": 8,
        "sep": 9,
        "sept": 9,
        "september": 9,
        "oct": 10,
        "october": 10,
        "nov": 11,
        "november": 11,
        "dec": 12,
        "december": 12,
    }
    _DATE_FORMATS = (
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%d %b %Y",
        "%d %B %Y",
        "%b %d %Y",
        "%B %d %Y",
    )

    def normalize(self, value: str | int | None) -> str | None:
        """Normalize a raw date into ``YYYY`` or ``YYYY-MM`` when possible."""

        if value is None:
            return None

        if isinstance(value, int):
            return self._normalize_year_value(value)

        if not isinstance(value, str):
            return None

        cleaned_value = " ".join(value.strip().split())

        if not cleaned_value:
            return None

        normalized_date = self._normalize_with_patterns(cleaned_value)

        if normalized_date is not None:
            return normalized_date

        return self._normalize_with_datetime(cleaned_value)

    def _normalize_year_value(self, value: int) -> str | None:
        """Normalize an integer year into its string representation."""

        if 1000 <= value <= 9999:
            return str(value)

        return None

    def _normalize_with_patterns(self, value: str) -> str | None:
        """Normalize date strings using explicit regex-based patterns."""

        year_match = self._YEAR_PATTERN.fullmatch(value)

        if year_match is not None:
            return year_match.group("year")

        year_month_match = self._YEAR_MONTH_PATTERN.fullmatch(value)

        if year_month_match is not None:
            return self._format_year_month(
                year=int(year_month_match.group("year")),
                month=int(year_month_match.group("month")),
            )

        month_year_match = self._MONTH_YEAR_PATTERN.fullmatch(value)

        if month_year_match is not None:
            return self._format_year_month(
                year=int(month_year_match.group("year")),
                month=int(month_year_match.group("month")),
            )

        textual_month_year_match = self._TEXTUAL_MONTH_YEAR_PATTERN.fullmatch(value)

        if textual_month_year_match is not None:
            month_value = self._MONTH_LOOKUP.get(
                textual_month_year_match.group("month").casefold()
            )

            if month_value is None:
                return None

            return self._format_year_month(
                year=int(textual_month_year_match.group("year")),
                month=month_value,
            )

        return None

    def _normalize_with_datetime(self, value: str) -> str | None:
        """Normalize date strings using a constrained list of date formats."""

        for date_format in self._DATE_FORMATS:
            try:
                parsed_date = datetime.strptime(value, date_format)
            except ValueError:
                continue

            return f"{parsed_date.year:04d}-{parsed_date.month:02d}"

        return None

    def _format_year_month(self, year: int, month: int) -> str | None:
        """Validate and format a year-month pair."""

        if not 1000 <= year <= 9999:
            return None

        if not 1 <= month <= 12:
            return None

        return f"{year:04d}-{month:02d}"
