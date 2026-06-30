"""Abstract parser contract and shared helpers for file-based candidate ingestion."""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import ClassVar

from candidate_data_transformer.models import Candidate
from candidate_data_transformer.parsers.exceptions import ParserFileError


class BaseParser(ABC):
    """Abstract base class for file parsers that produce candidate models."""

    parser_name: ClassVar[str] = "base"
    supported_suffixes: ClassVar[tuple[str, ...]] = ()

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize the parser with an optional logger."""

        self._logger = logger or logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )

    @abstractmethod
    def parse(self, path: Path) -> Candidate:
        """Parse a file and return a single candidate model."""

    def parse_many(self, path: Path) -> list[Candidate]:
        """Parse a file and return one or more candidate models."""

        return [self.parse(path)]

    def validate_path(self, path: Path) -> Path:
        """Validate that a candidate input path exists and matches expectations."""

        if not isinstance(path, Path):
            raise TypeError("path must be provided as a pathlib.Path instance.")

        if not path.exists():
            raise ParserFileError(f"Input file does not exist: {path}")

        if not path.is_file():
            raise ParserFileError(f"Input path is not a file: {path}")

        if self.supported_suffixes and path.suffix.lower() not in self.supported_suffixes:
            supported = ", ".join(self.supported_suffixes)
            raise ParserFileError(
                f"Unsupported file extension '{path.suffix}' for parser "
                f"{self.__class__.__name__}. Expected one of: {supported}."
            )

        return path

    @staticmethod
    def to_optional_text(value: object) -> str | None:
        """Convert a raw value into stripped optional text without normalization."""

        if value is None:
            return None

        if isinstance(value, str):
            stripped_value = value.strip()
            return stripped_value or None

        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return str(value)

        return None
