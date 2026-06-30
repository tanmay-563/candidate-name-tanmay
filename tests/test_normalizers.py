"""Unit tests for the data normalization layer."""

from __future__ import annotations

from candidate_data_transformer.models import Candidate, Experience
from candidate_data_transformer.normalizers import (
    CandidateNormalizer,
    DateNormalizer,
    EmailNormalizer,
    LocationNormalizer,
    PhoneNormalizer,
    SkillNormalizer,
)


def test_email_normalizer_returns_lowercase_valid_email() -> None:
    """Email normalization should trim whitespace and lowercase the value."""

    assert EmailNormalizer().normalize(" Tanmay@Gmail.com ") == "tanmay@gmail.com"


def test_email_normalizer_returns_none_for_invalid_email() -> None:
    """Email normalization should reject malformed addresses."""

    assert EmailNormalizer().normalize("not-an-email") is None


def test_phone_normalizer_converts_indian_mobile_to_e164() -> None:
    """Phone normalization should convert Indian mobile numbers to E.164."""

    assert PhoneNormalizer().normalize("9876543210") == "+919876543210"
    assert PhoneNormalizer().normalize("(+91) 98765-43210") == "+919876543210"


def test_skill_normalizer_maps_aliases_to_canonical_values() -> None:
    """Skill normalization should map aliases to their canonical skill names."""

    normalizer = SkillNormalizer()

    assert normalizer.normalize("cpp") == "C++"
    assert normalizer.normalize("javascript") == "JavaScript"
    assert normalizer.normalize("python3") == "Python"


def test_date_normalizer_returns_canonical_formats() -> None:
    """Date normalization should produce year or year-month representations."""

    normalizer = DateNormalizer()

    assert normalizer.normalize("Jan 2024") == "2024-01"
    assert normalizer.normalize("2023") == "2023"
    assert normalizer.normalize("2023-7-15") == "2023-07"


def test_location_normalizer_collapses_extra_whitespace() -> None:
    """Location normalization should return a clean comma-separated location."""

    assert (
        LocationNormalizer().normalize("  Bengaluru ,  Karnataka , India  ")
        == "Bengaluru, Karnataka, India"
    )


def test_candidate_normalizer_normalizes_supported_fields() -> None:
    """Candidate normalization should normalize contact, skills, dates, and location."""

    candidate = Candidate(
        full_name="Tanmay",
        emails=[" Tanmay@Gmail.com ", "bad-email", "tanmay@gmail.com"],
        phones=["9876543210", "(+91) 98765-43210", "invalid-phone"],
        location="  Bengaluru ,  Karnataka , India  ",
        skills=["cpp", "javascript", "python3", "cpp"],
        experience=[
            Experience(
                company="ACME",
                title="Engineer",
                start_date="Jan 2024",
                end_date="2023-7-15",
            )
        ],
    )

    normalized_candidate = CandidateNormalizer().normalize(candidate)

    assert normalized_candidate.emails == ["tanmay@gmail.com"]
    assert normalized_candidate.phones == ["+919876543210"]
    assert normalized_candidate.skills == ["C++", "JavaScript", "Python"]
    assert normalized_candidate.location == "Bengaluru, Karnataka, India"
    assert normalized_candidate.experience[0].start_date == "2024-01"
    assert normalized_candidate.experience[0].end_date == "2023-07"
