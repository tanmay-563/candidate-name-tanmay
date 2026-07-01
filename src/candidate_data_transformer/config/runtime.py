"""Runtime configuration models and loaders for the integrated pipeline."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from candidate_data_transformer.projector import ProjectionConfig, ProjectionConfigLoader
from candidate_data_transformer.validator import OutputSchema


class RuntimeConfigError(Exception):
    """Raised when pipeline runtime configuration cannot be loaded or validated."""


@dataclass(slots=True)
class RuntimeConfig:
    """Runtime configuration for projection and schema validation."""

    projection: ProjectionConfig
    schema: OutputSchema


class RuntimeConfigLoader:
    """Load runtime pipeline configuration from JSON files or mappings."""

    def __init__(self, logger: logging.Logger | None = None) -> None:
        """Initialize the loader with an optional logger."""

        self._logger = logger or logging.getLogger(
            "candidate_data_transformer.config.RuntimeConfigLoader"
        )
        self._projection_loader = ProjectionConfigLoader(logger=self._logger)

    def load(self, path: Path) -> RuntimeConfig:
        """Load runtime configuration from a JSON file path."""

        if not isinstance(path, Path):
            raise TypeError("path must be provided as a pathlib.Path instance.")

        if not path.exists():
            raise RuntimeConfigError(f"Runtime config file does not exist: {path}")

        if not path.is_file():
            raise RuntimeConfigError(f"Runtime config path is not a file: {path}")

        try:
            with path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except OSError as error:
            raise RuntimeConfigError(
                f"Unable to read runtime config file '{path}'."
            ) from error
        except json.JSONDecodeError as error:
            raise RuntimeConfigError(
                f"Runtime config file '{path}' contains invalid JSON."
            ) from error

        config = self.from_mapping(payload, config_directory=path.parent)
        self._logger.info("Loaded runtime config from '%s'.", path)
        return config

    def from_mapping(
        self,
        payload: Mapping[str, Any] | object,
        *,
        config_directory: Path | None = None,
    ) -> RuntimeConfig:
        """Build runtime configuration from a JSON-style mapping."""

        if not isinstance(payload, Mapping):
            raise RuntimeConfigError("Runtime config must be a JSON object.")

        projection_payload = payload.get("projection", {})
        schema_payload = payload.get("schema")
        schema_path = payload.get("schema_path")

        if schema_payload is not None and schema_path is not None:
            raise RuntimeConfigError(
                "Runtime config must define either 'schema' or 'schema_path', not both."
            )

        if schema_payload is None and schema_path is None:
            raise RuntimeConfigError(
                "Runtime config must define a 'schema' or 'schema_path' section."
            )

        projection = self._projection_loader.from_mapping(projection_payload)
        schema = self._load_schema(schema_payload, schema_path, config_directory)
        return RuntimeConfig(projection=projection, schema=schema)

    def _load_schema(
        self,
        schema_payload: object,
        schema_path: object,
        config_directory: Path | None,
    ) -> OutputSchema:
        """Load schema configuration from either inline JSON or a file path."""

        if schema_payload is not None:
            try:
                return OutputSchema.from_mapping(schema_payload)
            except Exception as error:
                raise RuntimeConfigError(
                    "Inline runtime schema configuration is invalid."
                ) from error

        if not isinstance(schema_path, str) or not schema_path.strip():
            raise RuntimeConfigError("schema_path must be a non-empty string value.")

        resolved_path = Path(schema_path.strip())

        if not resolved_path.is_absolute() and config_directory is not None:
            resolved_path = config_directory / resolved_path

        try:
            return OutputSchema.from_json_path(resolved_path)
        except Exception as error:
            raise RuntimeConfigError(
                f"Runtime schema file '{resolved_path}' is invalid."
            ) from error
