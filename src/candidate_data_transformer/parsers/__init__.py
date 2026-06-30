"""Parsing contracts for converting raw source payloads into structured documents."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Protocol

from candidate_data_transformer.models import RawCandidatePayload, SourceDocument


class CandidateParser(Protocol):
    """Interface for source-specific payload parsers."""

    def parse(self, raw_payload: RawCandidatePayload) -> SourceDocument:
        """Convert a raw candidate payload into a structured source document."""


@dataclass(slots=True)
class ParserRegistry:
    """Registry for associating source names with parser implementations."""

    parsers: dict[str, CandidateParser] = field(default_factory=dict)

    def register(self, source_name: str, parser: CandidateParser) -> None:
        """Register a parser for a named source."""

        self.parsers[source_name] = parser

    def get(self, source_name: str) -> CandidateParser:
        """Retrieve the parser associated with a named source."""

        return self.parsers[source_name]

    def snapshot(self) -> Mapping[str, CandidateParser]:
        """Return a read-only style view of the registered parser mapping."""

        return dict(self.parsers)


def build_parser_registry() -> ParserRegistry:
    """Create an empty parser registry for future dependency wiring."""

    return ParserRegistry()
