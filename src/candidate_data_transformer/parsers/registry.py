"""Registry utilities for managing available parser implementations."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from candidate_data_transformer.parsers.base import BaseParser
from candidate_data_transformer.parsers.exceptions import UnsupportedParserError
from candidate_data_transformer.parsers.github_json import GitHubJSONParser
from candidate_data_transformer.parsers.recruiter_csv import RecruiterCSVParser


@dataclass(slots=True)
class ParserRegistry:
    """Registry that stores parser instances by source identifier."""

    parsers: dict[str, BaseParser] = field(default_factory=dict)

    def register(self, source_name: str, parser: BaseParser) -> None:
        """Register a parser instance for a named source."""

        if not source_name.strip():
            raise ValueError("source_name must be a non-empty string.")

        if not isinstance(parser, BaseParser):
            raise TypeError("parser must be an instance of BaseParser.")

        self.parsers[source_name] = parser

    def get(self, source_name: str) -> BaseParser:
        """Retrieve the parser registered for a named source."""

        try:
            return self.parsers[source_name]
        except KeyError as error:
            raise UnsupportedParserError(
                f"No parser has been registered for source '{source_name}'."
            ) from error

    def snapshot(self) -> Mapping[str, BaseParser]:
        """Return a shallow copy of the registered parser mapping."""

        return dict(self.parsers)


def build_parser_registry() -> ParserRegistry:
    """Create a registry populated with the default parser implementations."""

    registry = ParserRegistry()
    registry.register("recruiter_csv", RecruiterCSVParser())
    registry.register("github_json", GitHubJSONParser())
    return registry
