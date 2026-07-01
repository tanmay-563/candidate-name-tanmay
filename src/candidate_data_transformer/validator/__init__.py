"""Schema validation components for projected output payloads."""

from __future__ import annotations

from candidate_data_transformer.validator.engine import SchemaValidator
from candidate_data_transformer.validator.exceptions import (
    InvalidSchemaDefinitionError,
    SchemaValidationError,
)
from candidate_data_transformer.validator.schema import FieldSchema, OutputSchema
from candidate_data_transformer.validator.service import (
    ValidationService,
    build_validation_service,
)

__all__ = [
    "FieldSchema",
    "InvalidSchemaDefinitionError",
    "OutputSchema",
    "SchemaValidationError",
    "SchemaValidator",
    "ValidationService",
    "build_validation_service",
]
