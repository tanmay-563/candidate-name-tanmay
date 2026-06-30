"""File parsers for converting raw source inputs into candidate models."""

from __future__ import annotations

from candidate_data_transformer.parsers.base import BaseParser
from candidate_data_transformer.parsers.exceptions import (
    EmptyParseResultError,
    MultipleCandidatesError,
    ParserError,
    ParserFileError,
    ParserInputError,
    UnsupportedParserError,
)
from candidate_data_transformer.parsers.factory import ParserFactory
from candidate_data_transformer.parsers.github_json import GitHubJSONParser
from candidate_data_transformer.parsers.recruiter_csv import RecruiterCSVParser
from candidate_data_transformer.parsers.registry import (
    ParserRegistry,
    build_parser_registry,
)

__all__ = [
    "BaseParser",
    "EmptyParseResultError",
    "GitHubJSONParser",
    "MultipleCandidatesError",
    "ParserError",
    "ParserFactory",
    "ParserFileError",
    "ParserInputError",
    "ParserRegistry",
    "RecruiterCSVParser",
    "UnsupportedParserError",
    "build_parser_registry",
]
