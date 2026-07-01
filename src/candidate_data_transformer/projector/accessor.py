"""Field path resolution helpers for candidate projection."""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import is_dataclass
from typing import Any

MISSING_VALUE = object()

_PATH_TOKEN_PATTERN = re.compile(r"([^.[]+)|\[(\d+)\]")


class FieldPathAccessor:
    """Resolve dotted and indexed field paths against nested Python objects."""

    def extract(self, root: object, path: str) -> object:
        """Extract a value from an object graph using a field path expression."""

        if not isinstance(path, str) or not path.strip():
            return MISSING_VALUE

        current_value: object = root

        for token_name, token_index in _PATH_TOKEN_PATTERN.findall(path):
            if token_name:
                current_value = self._resolve_named_token(current_value, token_name)
            else:
                current_value = self._resolve_index_token(
                    current_value,
                    int(token_index),
                )

            if current_value is MISSING_VALUE:
                return MISSING_VALUE

        return current_value

    def _resolve_named_token(self, value: object, token_name: str) -> object:
        """Resolve an attribute or mapping key token against a current value."""

        if isinstance(value, Mapping):
            return value.get(token_name, MISSING_VALUE)

        if is_dataclass(value) and hasattr(value, token_name):
            return getattr(value, token_name)

        if hasattr(value, token_name):
            return getattr(value, token_name)

        return MISSING_VALUE

    def _resolve_index_token(self, value: object, index: int) -> object:
        """Resolve a list index token against a current value."""

        if not isinstance(value, Sequence) or isinstance(
            value,
            (str, bytes, bytearray),
        ):
            return MISSING_VALUE

        if index < 0 or index >= len(value):
            return MISSING_VALUE

        return value[index]
