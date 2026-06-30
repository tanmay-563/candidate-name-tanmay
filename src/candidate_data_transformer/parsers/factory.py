"""Factory for selecting the correct parser implementation for a source file."""

from __future__ import annotations

import logging
from pathlib import Path

from candidate_data_transformer.parsers.base import BaseParser
from candidate_data_transformer.parsers.exceptions import UnsupportedParserError
from candidate_data_transformer.parsers.registry import (
    ParserRegistry,
    build_parser_registry,
)


class ParserFactory:
    """Factory responsible for returning parsers based on input file type."""

    def __init__(
        self,
        registry: ParserRegistry | None = None,
        logger: logging.Logger | None = None,
    ) -> None:
        """Initialize the factory with an optional registry and logger."""

        self._registry = registry or build_parser_registry()
        self._logger = logger or logging.getLogger(
            f"{__name__}.{self.__class__.__name__}"
        )

    def create(self, path: Path) -> BaseParser:
        """Return a parser instance appropriate for the provided file path."""

        if not isinstance(path, Path):
            raise TypeError("path must be provided as a pathlib.Path instance.")

        suffix = path.suffix.lower()

        if suffix == ".csv":
            parser = self._registry.get("recruiter_csv")
        elif suffix == ".json":
            parser = self._registry.get("github_json")
        else:
            raise UnsupportedParserError(
                f"No parser is registered for files with extension '{path.suffix}'."
            )

        self._logger.info(
            "Selected parser '%s' for input file '%s'.",
            parser.__class__.__name__,
            path,
        )
        return parser
