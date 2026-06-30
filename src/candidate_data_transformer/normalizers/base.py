"""Abstract base classes for the data normalization layer."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

InputType = TypeVar("InputType")
OutputType = TypeVar("OutputType")


class BaseNormalizer(ABC, Generic[InputType, OutputType]):
    """Abstract contract for transforming a value into canonical form."""

    @abstractmethod
    def normalize(self, value: InputType) -> OutputType:
        """Normalize the provided value into its canonical representation."""
