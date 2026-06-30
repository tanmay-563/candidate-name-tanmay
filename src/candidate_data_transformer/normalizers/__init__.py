"""Normalization components for canonicalizing candidate profile data."""

from __future__ import annotations

from candidate_data_transformer.normalizers.base import BaseNormalizer
from candidate_data_transformer.normalizers.candidate import CandidateNormalizer
from candidate_data_transformer.normalizers.date import DateNormalizer
from candidate_data_transformer.normalizers.email import EmailNormalizer
from candidate_data_transformer.normalizers.location import LocationNormalizer
from candidate_data_transformer.normalizers.phone import PhoneNormalizer
from candidate_data_transformer.normalizers.service import (
    NormalizationService,
    build_normalization_service,
)
from candidate_data_transformer.normalizers.skill import SkillNormalizer

__all__ = [
    "BaseNormalizer",
    "CandidateNormalizer",
    "DateNormalizer",
    "EmailNormalizer",
    "LocationNormalizer",
    "NormalizationService",
    "PhoneNormalizer",
    "SkillNormalizer",
    "build_normalization_service",
]
