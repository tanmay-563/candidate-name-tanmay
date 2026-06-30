"""Custom exceptions used by the parser layer."""

from __future__ import annotations


class ParserError(Exception):
    """Base exception for parser-related failures."""


class ParserFileError(ParserError):
    """Raised when a parser cannot access or validate an input file."""


class ParserInputError(ParserError):
    """Raised when an input file contains invalid or unsupported content."""


class EmptyParseResultError(ParserError):
    """Raised when a parser cannot produce any candidate records."""


class MultipleCandidatesError(ParserError):
    """Raised when a single-candidate parse request yields multiple candidates."""


class UnsupportedParserError(ParserError):
    """Raised when no parser is available for the requested file type."""
