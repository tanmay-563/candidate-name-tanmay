"""Custom exceptions used by the schema validation layer."""

from __future__ import annotations


class SchemaValidationError(Exception):
    """Raised when an output payload does not satisfy its schema."""


class InvalidSchemaDefinitionError(Exception):
    """Raised when a supplied schema definition is malformed or unsupported."""
