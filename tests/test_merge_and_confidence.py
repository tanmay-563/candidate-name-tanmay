"""Unit tests for the merge and confidence engines."""

from __future__ import annotations

from candidate_data_transformer.confidence import ConfidenceEngine
from candidate_data_transformer.merger import MergeEngine
from candidate_data_transformer.models import (
    Candidate,
    Education,
    Experience,
    Link,
    ProvenanceEntry,
)


def build_recruiter_candidate() -> Candidate:
    """Create a recruiter-sourced candidate fixture for engine tests."""

    return Candidate(
        full_name="Tanmay Sharma",
        emails=["tanmay@gmail.com"],
        phones=["+919876543210"],
        location="Bengaluru, Karnataka, India",
        links=[Link(type="linkedin", url="https://linkedin.com/in/tanmay")],
        skills=["Python", "SQL"],
        experience=[
            Experience(
                company="ACME",
                title="Backend Engineer",
                start_date="2024-01",
            )
        ],
        education=[
            Education(
                institution="VTU",
                degree="B.Tech",
            )
        ],
        provenance=[
            ProvenanceEntry(
                field="full_name",
                source="Recruiter CSV",
                method="csv_column",
            ),
            ProvenanceEntry(
                field="emails",
                source="Recruiter CSV",
                method="csv_column",
            ),
            ProvenanceEntry(
                field="phones",
                source="Recruiter CSV",
                method="csv_column",
            ),
            ProvenanceEntry(
                field="location",
                source="Recruiter CSV",
                method="csv_column",
            ),
            ProvenanceEntry(
                field="skills",
                source="Recruiter CSV",
                method="csv_column",
            ),
            ProvenanceEntry(
                field="experience",
                source="Recruiter CSV",
                method="csv_column",
            ),
            ProvenanceEntry(
                field="education",
                source="Recruiter CSV",
                method="csv_column",
            ),
            ProvenanceEntry(
                field="links",
                source="Recruiter CSV",
                method="csv_column",
            ),
        ],
    )


def build_github_candidate() -> Candidate:
    """Create a GitHub-sourced candidate fixture for engine tests."""

    return Candidate(
        full_name="Tanmay S.",
        emails=["tanmay@gmail.com", "tanmay@users.noreply.github.com"],
        location="Bengaluru, Karnataka, India",
        links=[Link(type="github", url="https://github.com/tanmay")],
        headline="Backend engineer and open-source contributor",
        skills=["Python", "Go"],
        experience=[
            Experience(
                company="ACME",
                title="Backend Engineer",
                start_date="2024-01",
                summary="Built backend APIs.",
            ),
            Experience(
                company="Open Source",
                title="Maintainer",
                start_date="2022-06",
            ),
        ],
        education=[
            Education(
                institution="VTU",
                degree="B.Tech",
                field="Computer Science",
                end_year=2024,
            )
        ],
        provenance=[
            ProvenanceEntry(field="full_name", source="GitHub", method="profile"),
            ProvenanceEntry(field="emails", source="GitHub", method="profile"),
            ProvenanceEntry(field="headline", source="GitHub", method="profile"),
            ProvenanceEntry(field="skills", source="GitHub", method="languages"),
            ProvenanceEntry(field="experience", source="GitHub", method="profile"),
            ProvenanceEntry(field="education", source="GitHub", method="profile"),
            ProvenanceEntry(field="links", source="GitHub", method="profile"),
        ],
    )


def test_merge_engine_prefers_higher_priority_scalar_fields() -> None:
    """Scalar field conflicts should resolve by source priority and non-empty value."""

    merged_candidate = MergeEngine().merge(
        [build_github_candidate(), build_recruiter_candidate()]
    )

    assert merged_candidate.full_name == "Tanmay Sharma"
    assert (
        merged_candidate.headline
        == "Backend engineer and open-source contributor"
    )
    assert merged_candidate.location == "Bengaluru, Karnataka, India"


def test_merge_engine_merges_lists_and_nested_records() -> None:
    """List and nested record merges should deduplicate while preserving data."""

    merged_candidate = MergeEngine().merge(
        [build_github_candidate(), build_recruiter_candidate()]
    )

    assert merged_candidate.emails == [
        "tanmay@gmail.com",
        "tanmay@users.noreply.github.com",
    ]
    assert merged_candidate.phones == ["+919876543210"]
    assert merged_candidate.skills == ["Go", "Python", "SQL"]
    assert len(merged_candidate.links) == 2
    assert len(merged_candidate.experience) == 2
    assert merged_candidate.experience[0].summary == "Built backend APIs."
    assert len(merged_candidate.education) == 1
    assert merged_candidate.education[0].field == "Computer Science"
    assert merged_candidate.education[0].end_year == 2024


def test_merge_engine_preserves_all_unique_provenance() -> None:
    """Merging should retain unique provenance entries from every input candidate."""

    merged_candidate = MergeEngine().merge(
        [build_recruiter_candidate(), build_github_candidate()]
    )

    merged_provenance = {
        (entry.field, entry.source, entry.method)
        for entry in merged_candidate.provenance
    }

    assert ("full_name", "Recruiter CSV", "csv_column") in merged_provenance
    assert ("full_name", "GitHub", "profile") in merged_provenance
    assert ("headline", "GitHub", "profile") in merged_provenance


def test_confidence_engine_scores_fields_deterministically() -> None:
    """Confidence scoring should map known sources to deterministic scores."""

    engine = ConfidenceEngine()

    assert engine.calculate_field_confidence("value", "Recruiter CSV") == 0.95
    assert engine.calculate_field_confidence("value", "GitHub") == 0.80
    assert engine.calculate_field_confidence("value", "Unknown") == 0.50
    assert engine.calculate_field_confidence(None, "Recruiter CSV") == 0.00


def test_confidence_engine_calculates_candidate_and_overall_scores() -> None:
    """Candidate confidence should use provenance sources and missing-value policy."""

    merged_candidate = MergeEngine().merge(
        [build_recruiter_candidate(), build_github_candidate()]
    )

    engine = ConfidenceEngine()
    field_scores = engine.calculate_candidate_confidence(merged_candidate)

    assert field_scores["full_name"] == 0.95
    assert field_scores["headline"] == 0.80
    assert field_scores["phones"] == 0.95
    assert field_scores["years_experience"] == 0.00

    overall_score = engine.overall_confidence(field_scores)

    assert 0.0 <= overall_score <= 1.0
    assert overall_score == engine.assess(merged_candidate).overall_score
