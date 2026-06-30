"""CSV parser for recruiter-supplied candidate exports."""

from __future__ import annotations

import csv
from collections.abc import Mapping
from pathlib import Path
from typing import ClassVar

from candidate_data_transformer.models import Candidate, Experience
from candidate_data_transformer.parsers.base import BaseParser
from candidate_data_transformer.parsers.exceptions import (
    EmptyParseResultError,
    MultipleCandidatesError,
    ParserFileError,
    ParserInputError,
)


class RecruiterCSVParser(BaseParser):
    """Parse recruiter CSV files into one or more candidate models."""

    parser_name: ClassVar[str] = "recruiter_csv"
    supported_suffixes: ClassVar[tuple[str, ...]] = (".csv",)
    expected_columns: ClassVar[tuple[str, ...]] = (
        "name",
        "email",
        "phone",
        "current_company",
        "title",
    )

    def parse(self, path: Path) -> Candidate:
        """Parse a recruiter CSV file and return a single candidate."""

        candidates = self.parse_many(path)

        if not candidates:
            raise EmptyParseResultError(
                f"Recruiter CSV file '{path}' did not contain any candidate rows."
            )

        if len(candidates) > 1:
            raise MultipleCandidatesError(
                f"Recruiter CSV file '{path}' contains {len(candidates)} candidates. "
                "Use parse_many() for batch ingestion."
            )

        return candidates[0]

    def parse_many(self, path: Path) -> list[Candidate]:
        """Parse a recruiter CSV file and return all extracted candidates."""

        csv_path = self.validate_path(path)
        self._logger.info("Parsing recruiter CSV file '%s'.", csv_path)

        try:
            with csv_path.open("r", encoding="utf-8-sig", newline="") as file_handle:
                reader = csv.DictReader(file_handle)

                if reader.fieldnames is None:
                    self._logger.warning(
                        "Recruiter CSV file '%s' is empty or missing a header row.",
                        csv_path,
                    )
                    return []

                self._log_missing_columns(reader.fieldnames, csv_path)

                candidates: list[Candidate] = []

                for row_number, row in enumerate(reader, start=2):
                    if self._is_empty_row(row):
                        self._logger.debug(
                            "Skipping empty recruiter CSV row %s in '%s'.",
                            row_number,
                            csv_path,
                        )
                        continue

                    candidate = self._build_candidate_from_row(
                        row=row,
                        row_number=row_number,
                        path=csv_path,
                    )

                    if candidate is None:
                        self._logger.debug(
                            "Skipping recruiter CSV row %s in '%s' because no "
                            "supported candidate fields were present.",
                            row_number,
                            csv_path,
                        )
                        continue

                    candidates.append(candidate)

        except OSError as error:
            raise ParserFileError(
                f"Unable to read recruiter CSV file '{csv_path}'."
            ) from error
        except csv.Error as error:
            raise ParserInputError(
                f"Recruiter CSV file '{csv_path}' could not be parsed."
            ) from error

        self._logger.info(
            "Parsed %s candidate record(s) from recruiter CSV file '%s'.",
            len(candidates),
            csv_path,
        )
        return candidates

    def _log_missing_columns(self, fieldnames: list[str] | None, path: Path) -> None:
        """Log any expected columns that are not present in the CSV header."""

        if fieldnames is None:
            return

        normalized_fieldnames = {fieldname.strip() for fieldname in fieldnames if fieldname}
        missing_columns = [
            column
            for column in self.expected_columns
            if column not in normalized_fieldnames
        ]

        if missing_columns:
            self._logger.warning(
                "Recruiter CSV file '%s' is missing expected columns: %s.",
                path,
                ", ".join(missing_columns),
            )

    def _build_candidate_from_row(
        self,
        row: Mapping[str | None, object],
        row_number: int,
        path: Path,
    ) -> Candidate | None:
        """Create a candidate model from a recruiter CSV row."""

        name = self._get_text_value(row, "name")
        email = self._get_text_value(row, "email")
        phone = self._get_text_value(row, "phone")
        current_company = self._get_text_value(row, "current_company")
        title = self._get_text_value(row, "title")

        if not any([name, email, phone, current_company, title]):
            return None

        experience: list[Experience] = []

        if current_company or title:
            experience.append(Experience(company=current_company, title=title))

        try:
            return Candidate(
                full_name=name,
                emails=[email] if email else [],
                phones=[phone] if phone else [],
                experience=experience,
            )
        except (TypeError, ValueError) as error:
            raise ParserInputError(
                f"Recruiter CSV row {row_number} in '{path}' is invalid."
            ) from error

    def _get_text_value(
        self,
        row: Mapping[str | None, object],
        column_name: str,
    ) -> str | None:
        """Extract an optional text value from a CSV row by column name."""

        return self.to_optional_text(row.get(column_name))

    def _is_empty_row(self, row: Mapping[str | None, object]) -> bool:
        """Return whether a recruiter CSV row contains no meaningful values."""

        for value in row.values():
            if isinstance(value, list):
                if any(self.to_optional_text(item) for item in value):
                    return False
                continue

            if self.to_optional_text(value) is not None:
                return False

        return True
