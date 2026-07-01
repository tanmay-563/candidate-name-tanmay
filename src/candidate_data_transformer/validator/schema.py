"""Schema definition models for output payload validation."""

from __future__ import annotations

import json
from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from candidate_data_transformer.validator.exceptions import (
    InvalidSchemaDefinitionError,
)

SUPPORTED_SCHEMA_TYPES = frozenset(
    {"string", "number", "integer", "boolean", "object", "list", "any", "null"}
)


@dataclass(slots=True)
class FieldSchema:
    """Recursive schema definition for a projected output field."""

    field_type: str
    required: bool = False
    items: FieldSchema | None = None
    properties: dict[str, FieldSchema] = field(default_factory=dict)
    allow_extra_fields: bool = True

    def __post_init__(self) -> None:
        """Validate the schema field configuration."""

        if self.field_type not in SUPPORTED_SCHEMA_TYPES:
            raise InvalidSchemaDefinitionError(
                f"Unsupported schema field type '{self.field_type}'."
            )


@dataclass(slots=True)
class OutputSchema:
    """Root object schema for validating a projected output payload."""

    properties: dict[str, FieldSchema] = field(default_factory=dict)
    allow_extra_fields: bool = True

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any] | object) -> OutputSchema:
        """Build an output schema from a JSON-style mapping."""

        if not isinstance(payload, Mapping):
            raise InvalidSchemaDefinitionError("Schema definition must be an object.")

        field_type = payload.get("type", "object")

        if field_type != "object":
            raise InvalidSchemaDefinitionError(
                "Root schema type must be 'object'."
            )

        raw_properties = payload.get("properties", {})

        if not isinstance(raw_properties, Mapping):
            raise InvalidSchemaDefinitionError("Schema 'properties' must be an object.")

        properties = {
            field_name: cls._field_schema_from_mapping(field_name, field_schema)
            for field_name, field_schema in raw_properties.items()
        }

        allow_extra_fields = payload.get("allow_extra_fields", True)

        if not isinstance(allow_extra_fields, bool):
            raise InvalidSchemaDefinitionError(
                "allow_extra_fields must be a boolean value."
            )

        return cls(
            properties=properties,
            allow_extra_fields=allow_extra_fields,
        )

    @classmethod
    def from_json_path(cls, path: Path) -> OutputSchema:
        """Build an output schema from a JSON schema file path."""

        if not isinstance(path, Path):
            raise TypeError("path must be provided as a pathlib.Path instance.")

        if not path.exists():
            raise InvalidSchemaDefinitionError(f"Schema file does not exist: {path}")

        if not path.is_file():
            raise InvalidSchemaDefinitionError(f"Schema path is not a file: {path}")

        try:
            with path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except OSError as error:
            raise InvalidSchemaDefinitionError(
                f"Unable to read schema file '{path}'."
            ) from error
        except json.JSONDecodeError as error:
            raise InvalidSchemaDefinitionError(
                f"Schema file '{path}' contains invalid JSON."
            ) from error

        return cls.from_mapping(payload)

    @classmethod
    def _field_schema_from_mapping(
        cls,
        field_name: str,
        payload: Mapping[str, Any] | object,
    ) -> FieldSchema:
        """Recursively build a field schema from a JSON-style mapping."""

        if not isinstance(payload, Mapping):
            raise InvalidSchemaDefinitionError(
                f"Schema definition for field '{field_name}' must be an object."
            )

        raw_field_type = payload.get("type")

        if not isinstance(raw_field_type, str):
            raise InvalidSchemaDefinitionError(
                f"Schema definition for field '{field_name}' must declare a string 'type'."
            )

        required = payload.get("required", False)

        if not isinstance(required, bool):
            raise InvalidSchemaDefinitionError(
                f"'required' for field '{field_name}' must be a boolean value."
            )

        allow_extra_fields = payload.get("allow_extra_fields", True)

        if not isinstance(allow_extra_fields, bool):
            raise InvalidSchemaDefinitionError(
                f"'allow_extra_fields' for field '{field_name}' must be a boolean."
            )

        raw_items = payload.get("items")
        items = (
            cls._field_schema_from_mapping(f"{field_name}[]", raw_items)
            if raw_items is not None
            else None
        )

        raw_properties = payload.get("properties", {})

        if raw_properties is None:
            raw_properties = {}

        if not isinstance(raw_properties, Mapping):
            raise InvalidSchemaDefinitionError(
                f"'properties' for field '{field_name}' must be an object."
            )

        properties = {
            child_name: cls._field_schema_from_mapping(child_name, child_schema)
            for child_name, child_schema in raw_properties.items()
        }

        return FieldSchema(
            field_type=raw_field_type,
            required=required,
            items=items,
            properties=properties,
            allow_extra_fields=allow_extra_fields,
        )
