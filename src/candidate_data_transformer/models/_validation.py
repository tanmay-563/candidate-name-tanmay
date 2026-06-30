"""Validation helpers used by the domain model dataclasses."""

from __future__ import annotations

from collections.abc import Iterable
from typing import TypeVar

ModelType = TypeVar("ModelType")


def normalize_optional_text(value: str | None, field_name: str) -> str | None:
    """Normalize an optional text field by stripping surrounding whitespace."""

    if value is None:
        return None

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string or None.")

    stripped_value = value.strip()
    return stripped_value or None


def normalize_required_text(value: str, field_name: str) -> str:
    """Normalize a required text field and reject blank values."""

    if not isinstance(value, str):
        raise TypeError(f"{field_name} must be a string.")

    stripped_value = value.strip()

    if not stripped_value:
        raise ValueError(f"{field_name} cannot be blank.")

    return stripped_value


def normalize_string_list(
    values: Iterable[str] | None,
    field_name: str,
) -> list[str]:
    """Validate a collection of strings and return it as a concrete list."""

    if values is None:
        return []

    normalized_values: list[str] = []

    for index, value in enumerate(values):
        normalized_values.append(
            normalize_required_text(value, f"{field_name}[{index}]")
        )

    return normalized_values


def normalize_model_list(
    values: Iterable[ModelType] | None,
    expected_type: type[ModelType],
    field_name: str,
) -> list[ModelType]:
    """Validate a collection of model objects and return a copied list."""

    if values is None:
        return []

    normalized_values: list[ModelType] = []

    for index, value in enumerate(values):
        if not isinstance(value, expected_type):
            raise TypeError(
                f"{field_name}[{index}] must be an instance of "
                f"{expected_type.__name__}."
            )

        normalized_values.append(value)

    return normalized_values


def normalize_non_negative_float(
    value: float | int | None,
    field_name: str,
) -> float | None:
    """Validate that a numeric value is a non-negative floating-point number."""

    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a float, int, or None.")

    normalized_value = float(value)

    if normalized_value < 0.0:
        raise ValueError(f"{field_name} must be greater than or equal to 0.")

    return normalized_value


def normalize_confidence_score(value: float | int, field_name: str) -> float:
    """Validate that a confidence score is between 0.0 and 1.0 inclusive."""

    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a float or int.")

    normalized_value = float(value)

    if not 0.0 <= normalized_value <= 1.0:
        raise ValueError(f"{field_name} must be between 0.0 and 1.0.")

    return normalized_value


def normalize_year(value: int | None, field_name: str) -> int | None:
    """Validate that a year value uses a four-digit positive calendar year."""

    if value is None:
        return None

    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer year or None.")

    if value < 1000 or value > 9999:
        raise ValueError(f"{field_name} must be a four-digit year.")

    return value
