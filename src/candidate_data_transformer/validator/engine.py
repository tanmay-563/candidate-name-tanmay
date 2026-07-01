"""Recursive schema validator for projected output payloads."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from candidate_data_transformer.validator.exceptions import SchemaValidationError
from candidate_data_transformer.validator.schema import FieldSchema, OutputSchema


@dataclass(slots=True)
class SchemaValidator:
    """Validate projected output payloads against explicit schemas."""

    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(
            "candidate_data_transformer.validator.SchemaValidator"
        )
    )

    def validate(
        self,
        payload: Mapping[str, Any],
        schema: OutputSchema | Mapping[str, Any] | Path,
    ) -> None:
        """Validate a projected payload against a provided schema definition."""

        resolved_schema = self._resolve_schema(schema)

        if not isinstance(payload, Mapping):
            raise SchemaValidationError("Projected payload must be an object.")

        self._validate_object(
            payload=payload,
            schema=resolved_schema,
            path="$",
        )
        self.logger.info(
            "Validated projected payload with %s top-level field(s).",
            len(payload),
        )

    def _resolve_schema(
        self,
        schema: OutputSchema | Mapping[str, Any] | Path,
    ) -> OutputSchema:
        """Resolve supported schema inputs into an ``OutputSchema`` instance."""

        if isinstance(schema, OutputSchema):
            return schema

        if isinstance(schema, Path):
            return OutputSchema.from_json_path(schema)

        return OutputSchema.from_mapping(schema)

    def _validate_object(
        self,
        payload: Mapping[str, Any],
        schema: OutputSchema | FieldSchema,
        path: str,
    ) -> None:
        """Validate an object payload against its schema."""

        schema_properties = schema.properties
        allow_extra_fields = schema.allow_extra_fields

        for field_name, field_schema in schema_properties.items():
            child_path = f"{path}.{field_name}"

            if field_name not in payload or payload[field_name] is None:
                if field_schema.required:
                    raise SchemaValidationError(
                        f"Missing required value at '{child_path}'."
                    )

                continue

            self._validate_value(payload[field_name], field_schema, child_path)

        if not allow_extra_fields:
            extra_fields = set(payload.keys()) - set(schema_properties.keys())

            if extra_fields:
                formatted_extra_fields = ", ".join(sorted(extra_fields))
                raise SchemaValidationError(
                    f"Unexpected field(s) at '{path}': {formatted_extra_fields}."
                )

    def _validate_value(
        self,
        value: object,
        schema: FieldSchema,
        path: str,
    ) -> None:
        """Validate a scalar, list, or object value against a field schema."""

        if schema.field_type == "any":
            return

        if schema.field_type == "null":
            if value is not None:
                raise SchemaValidationError(f"Field '{path}' must be null.")
            return

        if schema.field_type == "string":
            if not isinstance(value, str):
                raise SchemaValidationError(f"Field '{path}' must be a string.")
            return

        if schema.field_type == "boolean":
            if not isinstance(value, bool):
                raise SchemaValidationError(f"Field '{path}' must be a boolean.")
            return

        if schema.field_type == "integer":
            if isinstance(value, bool) or not isinstance(value, int):
                raise SchemaValidationError(f"Field '{path}' must be an integer.")
            return

        if schema.field_type == "number":
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise SchemaValidationError(f"Field '{path}' must be a number.")
            return

        if schema.field_type == "list":
            if not isinstance(value, list):
                raise SchemaValidationError(f"Field '{path}' must be a list.")

            if schema.items is not None:
                for index, item in enumerate(value):
                    self._validate_value(item, schema.items, f"{path}[{index}]")

            return

        if schema.field_type == "object":
            if not isinstance(value, Mapping):
                raise SchemaValidationError(f"Field '{path}' must be an object.")

            self._validate_object(value, schema, path)
            return
