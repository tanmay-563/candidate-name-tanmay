"""Configuration models and loader for runtime candidate projection."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from candidate_data_transformer.projector.exceptions import (
    ProjectionConfigurationError,
)

DEFAULT_SELECTED_FIELDS: tuple[str, ...] = (
    "candidate_id",
    "full_name",
    "emails",
    "phones",
    "location",
    "links",
    "headline",
    "years_experience",
    "skills",
    "experience",
    "education",
)
SUPPORTED_MISSING_VALUE_POLICIES = frozenset({"null", "omit", "error"})


@dataclass(slots=True)
class ProjectionFieldConfig:
    """Projection settings for a single selected field path."""

    source_path: str
    target_name: str
    normalize_output: bool = True


@dataclass(slots=True)
class ProjectionConfig:
    """Runtime configuration for projecting a candidate into output payloads."""

    fields: list[ProjectionFieldConfig] = field(default_factory=list)
    include_confidence: bool = False
    include_provenance: bool = False
    missing_value_policy: str = "null"

    def __post_init__(self) -> None:
        """Validate the overall projection configuration."""

        if self.missing_value_policy not in SUPPORTED_MISSING_VALUE_POLICIES:
            raise ProjectionConfigurationError(
                "missing_value_policy must be one of: "
                f"{', '.join(sorted(SUPPORTED_MISSING_VALUE_POLICIES))}."
            )

        if any(not isinstance(field_config, ProjectionFieldConfig) for field_config in self.fields):
            raise ProjectionConfigurationError(
                "fields must contain ProjectionFieldConfig instances only."
            )

        seen_target_names: set[str] = set()

        for field_config in self.fields:
            if not field_config.source_path.strip():
                raise ProjectionConfigurationError(
                    "Projection field source_path values must be non-empty strings."
                )

            if not field_config.target_name.strip():
                raise ProjectionConfigurationError(
                    "Projection field target_name values must be non-empty strings."
                )

            if field_config.target_name in seen_target_names:
                raise ProjectionConfigurationError(
                    f"Duplicate projected target name '{field_config.target_name}' is not allowed."
                )

            seen_target_names.add(field_config.target_name)


class ProjectionConfigLoader:
    """Load and validate projection configuration from JSON files."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize the loader with an optional logger."""

        self._logger = logger or logging.getLogger(
            "candidate_data_transformer.projector.ProjectionConfigLoader"
        )

    def load(self, path: Path) -> ProjectionConfig:
        """Load a projection configuration from a JSON file path."""

        if not isinstance(path, Path):
            raise TypeError("path must be provided as a pathlib.Path instance.")

        if not path.exists():
            raise ProjectionConfigurationError(
                f"Projection configuration file does not exist: {path}"
            )

        if not path.is_file():
            raise ProjectionConfigurationError(
                f"Projection configuration path is not a file: {path}"
            )

        try:
            with path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except OSError as error:
            raise ProjectionConfigurationError(
                f"Unable to read projection configuration file '{path}'."
            ) from error
        except json.JSONDecodeError as error:
            raise ProjectionConfigurationError(
                f"Projection configuration file '{path}' contains invalid JSON."
            ) from error

        config = self.from_mapping(payload)
        self._logger.info("Loaded projection configuration from '%s'.", path)
        return config

    def from_mapping(self, payload: Mapping[str, Any] | object) -> ProjectionConfig:
        """Construct a projection configuration from an in-memory mapping."""

        if not isinstance(payload, Mapping):
            raise ProjectionConfigurationError(
                "Projection configuration must be a JSON object."
            )

        select_fields = self._extract_select_fields(payload)
        rename_fields = self._extract_string_mapping(payload, "rename_fields")
        normalization = self._extract_bool_mapping(payload, "normalization")
        include_confidence = self._extract_bool(payload, "include_confidence", False)
        include_provenance = self._extract_bool(payload, "include_provenance", False)
        missing_value_policy = payload.get("missing_value_policy", "null")

        if not isinstance(missing_value_policy, str):
            raise ProjectionConfigurationError(
                "missing_value_policy must be a string value."
            )

        normalized_field_paths = self._deduplicate_preserving_order(
            list(select_fields or DEFAULT_SELECTED_FIELDS)
        )

        for source_path in rename_fields:
            if source_path not in normalized_field_paths:
                normalized_field_paths.append(source_path)

        field_configs = [
            ProjectionFieldConfig(
                source_path=source_path,
                target_name=rename_fields.get(
                    source_path,
                    self._default_target_name(source_path),
                ),
                normalize_output=normalization.get(source_path, True),
            )
            for source_path in normalized_field_paths
        ]

        return ProjectionConfig(
            fields=field_configs,
            include_confidence=include_confidence,
            include_provenance=include_provenance,
            missing_value_policy=missing_value_policy,
        )

    def _deduplicate_preserving_order(self, values: list[str]) -> list[str]:
        """Return a list of unique strings preserving the original order."""

        deduplicated_values: list[str] = []
        seen_values: set[str] = set()

        for value in values:
            if value in seen_values:
                continue

            seen_values.add(value)
            deduplicated_values.append(value)

        return deduplicated_values

    def _extract_select_fields(self, payload: Mapping[str, Any]) -> list[str]:
        """Extract selected field paths from supported configuration keys."""

        has_fields = "fields" in payload
        has_select_fields = "select_fields" in payload

        if has_fields and has_select_fields:
            raise ProjectionConfigurationError(
                "Use either 'fields' or 'select_fields', not both."
            )

        raw_fields = payload.get("fields", payload.get("select_fields", []))

        if raw_fields in (None, []):
            return []

        if not isinstance(raw_fields, list):
            raise ProjectionConfigurationError(
                "fields/select_fields must be provided as a list of strings."
            )

        normalized_fields: list[str] = []

        for index, raw_field in enumerate(raw_fields):
            if not isinstance(raw_field, str) or not raw_field.strip():
                raise ProjectionConfigurationError(
                    f"fields/select_fields[{index}] must be a non-empty string."
                )

            normalized_fields.append(raw_field.strip())

        return normalized_fields

    def _extract_string_mapping(
        self,
        payload: Mapping[str, Any],
        key: str,
    ) -> dict[str, str]:
        """Extract a string-to-string mapping from projection config payload."""

        raw_value = payload.get(key, {})

        if raw_value in (None, {}):
            return {}

        if not isinstance(raw_value, Mapping):
            raise ProjectionConfigurationError(f"{key} must be a JSON object.")

        normalized_mapping: dict[str, str] = {}

        for raw_key, raw_item in raw_value.items():
            if not isinstance(raw_key, str) or not raw_key.strip():
                raise ProjectionConfigurationError(f"{key} keys must be non-empty strings.")

            if not isinstance(raw_item, str) or not raw_item.strip():
                raise ProjectionConfigurationError(
                    f"{key}['{raw_key}'] must be a non-empty string."
                )

            normalized_mapping[raw_key.strip()] = raw_item.strip()

        return normalized_mapping

    def _extract_bool_mapping(
        self,
        payload: Mapping[str, Any],
        key: str,
    ) -> dict[str, bool]:
        """Extract a string-to-boolean mapping from projection config payload."""

        raw_value = payload.get(key, {})

        if raw_value in (None, {}):
            return {}

        if not isinstance(raw_value, Mapping):
            raise ProjectionConfigurationError(f"{key} must be a JSON object.")

        normalized_mapping: dict[str, bool] = {}

        for raw_key, raw_item in raw_value.items():
            if not isinstance(raw_key, str) or not raw_key.strip():
                raise ProjectionConfigurationError(f"{key} keys must be non-empty strings.")

            if not isinstance(raw_item, bool):
                raise ProjectionConfigurationError(
                    f"{key}['{raw_key}'] must be a boolean value."
                )

            normalized_mapping[raw_key.strip()] = raw_item

        return normalized_mapping

    def _extract_bool(
        self,
        payload: Mapping[str, Any],
        key: str,
        default: bool,
    ) -> bool:
        """Extract a boolean option from the projection config payload."""

        raw_value = payload.get(key, default)

        if not isinstance(raw_value, bool):
            raise ProjectionConfigurationError(f"{key} must be a boolean value.")

        return raw_value

    def _default_target_name(self, source_path: str) -> str:
        """Build a stable target key name for a source path without explicit rename."""

        collapsed_value = re.sub(r"[\[\].]+", "_", source_path).strip("_")
        return collapsed_value or source_path
