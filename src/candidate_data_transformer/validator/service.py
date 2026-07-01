"""Service wrappers for projected output schema validation."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from candidate_data_transformer.validator.engine import SchemaValidator
from candidate_data_transformer.validator.schema import OutputSchema


@dataclass(slots=True)
class ValidationService:
    """Service wrapper around the schema validator."""

    validator: SchemaValidator = field(default_factory=SchemaValidator)

    def validate_output(
        self,
        payload: Mapping[str, Any],
        schema: OutputSchema | Mapping[str, Any] | Path,
    ) -> None:
        """Validate a projected output payload against a schema definition."""

        self.validator.validate(payload, schema)

    def validate_candidate(
        self,
        record: Mapping[str, Any],
        schema: OutputSchema | Mapping[str, Any] | Path,
    ) -> None:
        """Compatibility wrapper that validates a projected output record."""

        self.validate_output(record, schema)


def build_validation_service() -> ValidationService:
    """Create the default validation service for application wiring."""

    return ValidationService()
