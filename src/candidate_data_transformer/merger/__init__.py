"""Merge engine components for consolidating candidate profiles."""

from __future__ import annotations

from candidate_data_transformer.merger.engine import MergeEngine
from candidate_data_transformer.merger.service import (
    MergeService,
    build_merge_service,
)

__all__ = ["MergeEngine", "MergeService", "build_merge_service"]
