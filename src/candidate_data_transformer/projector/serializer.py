"""Serialization helpers for converting projection values into output payloads."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any


class ProjectionSerializer:
    """Convert projected values into JSON-serializable Python structures."""

    def serialize(self, value: object, normalize_output: bool = True) -> Any:
        """Serialize a projected value into a JSON-compatible structure."""

        if is_dataclass(value):
            return self.serialize(asdict(value), normalize_output=normalize_output)

        if isinstance(value, dict):
            return {
                key: self.serialize(item, normalize_output=normalize_output)
                for key, item in value.items()
            }

        if isinstance(value, list):
            return [
                self.serialize(item, normalize_output=normalize_output)
                for item in value
            ]

        if isinstance(value, str) and normalize_output:
            return " ".join(value.split())

        return value
