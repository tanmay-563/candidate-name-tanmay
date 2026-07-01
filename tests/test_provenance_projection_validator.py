"""Unit tests for provenance, projection, and schema validation layers."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from candidate_data_transformer.confidence import ConfidenceEngine
from candidate_data_transformer.merger import MergeEngine
from candidate_data_transformer.models import (
    Candidate,
    Link,
    ProvenanceEntry,
)
from candidate_data_transformer.projector import (
    ConfigurableProjector,
    MissingProjectionValueError,
    ProjectionConfig,
    ProjectionConfigLoader,
    ProjectionFieldConfig,
)
from candidate_data_transformer.provenance import ProvenanceEngine
from candidate_data_transformer.validator import (
    InvalidSchemaDefinitionError,
    SchemaValidationError,
    SchemaValidator,
)


def build_recruiter_candidate() -> Candidate:
    """Create a recruiter-sourced candidate fixture."""

    return Candidate(
        full_name="Tanmay Sharma",
        emails=["tanmay@gmail.com"],
        phones=["+919876543210"],
        location="Bengaluru, Karnataka, India",
        skills=["Python", "SQL"],
        provenance=[
            ProvenanceEntry(field="full_name", source="Recruiter CSV", method="csv"),
            ProvenanceEntry(field="emails", source="Recruiter CSV", method="csv"),
            ProvenanceEntry(field="phones", source="Recruiter CSV", method="csv"),
            ProvenanceEntry(field="location", source="Recruiter CSV", method="csv"),
            ProvenanceEntry(field="skills", source="Recruiter CSV", method="csv"),
        ],
    )


def build_github_candidate() -> Candidate:
    """Create a GitHub-sourced candidate fixture."""

    return Candidate(
        full_name="Tanmay S.",
        emails=["tanmay@gmail.com", "tanmay@users.noreply.github.com"],
        links=[Link(type="github", url="https://github.com/tanmay")],
        headline="Senior   Backend Engineer",
        skills=["Python", "Go"],
        provenance=[
            ProvenanceEntry(field="full_name", source="GitHub", method="profile"),
            ProvenanceEntry(field="emails", source="GitHub", method="profile"),
            ProvenanceEntry(field="headline", source="GitHub", method="profile"),
            ProvenanceEntry(field="skills", source="GitHub", method="profile"),
            ProvenanceEntry(field="links", source="GitHub", method="profile"),
        ],
    )


def test_provenance_engine_collects_field_level_entries() -> None:
    """The provenance engine should synthesize final field-level source entries."""

    merged_candidate = MergeEngine().merge(
        [build_recruiter_candidate(), build_github_candidate()]
    )

    provenance_entries = ProvenanceEngine().collect(merged_candidate)
    provenance_by_field = {
        entry.field: [] for entry in provenance_entries if entry.field is not None
    }

    for entry in provenance_entries:
        if entry.field is not None:
            provenance_by_field[entry.field].append((entry.source, entry.method))

    assert ("Recruiter CSV", "merged") in provenance_by_field["full_name"]
    assert ("GitHub", "merged") in provenance_by_field["emails"]
    assert provenance_by_field["candidate_id"] == [("Missing", "missing")]


def test_projection_config_loader_reads_runtime_json_config(tmp_path: Path) -> None:
    """Projection config loader should build a runtime config from JSON."""

    config_path = tmp_path / "projection.json"
    config_path.write_text(
        json.dumps(
            {
                "select_fields": ["full_name", "headline", "emails[0]", "candidate_id"],
                "rename_fields": {"emails[0]": "primary_email"},
                "include_confidence": True,
                "include_provenance": True,
                "missing_value_policy": "null",
                "normalization": {"headline": True},
            }
        ),
        encoding="utf-8",
    )

    config = ProjectionConfigLoader().load(config_path)

    assert [field_config.source_path for field_config in config.fields] == [
        "full_name",
        "headline",
        "emails[0]",
        "candidate_id",
    ]
    assert config.fields[2].target_name == "primary_email"
    assert config.include_confidence is True
    assert config.include_provenance is True
    assert config.missing_value_policy == "null"


def test_projector_projects_configured_output_payload() -> None:
    """The projector should rename fields and include confidence and provenance."""

    merged_candidate = MergeEngine().merge(
        [build_recruiter_candidate(), build_github_candidate()]
    )
    confidence = ConfidenceEngine().assess(merged_candidate)
    provenance = ProvenanceEngine().collect(merged_candidate)

    config = ProjectionConfig(
        fields=[
            ProjectionFieldConfig("full_name", "full_name"),
            ProjectionFieldConfig("headline", "headline"),
            ProjectionFieldConfig("emails[0]", "primary_email"),
            ProjectionFieldConfig("candidate_id", "candidate_id"),
        ],
        include_confidence=True,
        include_provenance=True,
        missing_value_policy="null",
    )

    payload = ConfigurableProjector().project(
        merged_candidate,
        config,
        confidence=confidence,
        provenance=provenance,
    )

    assert payload["full_name"] == "Tanmay Sharma"
    assert payload["headline"] == "Senior Backend Engineer"
    assert payload["primary_email"] == "tanmay@gmail.com"
    assert payload["candidate_id"] is None
    assert payload["confidence"]["overall"] == confidence.overall_score
    assert any(entry["field"] == "full_name" for entry in payload["provenance"])


def test_projector_honors_missing_value_error_policy() -> None:
    """Missing projected values should raise when policy is configured as error."""

    config = ProjectionConfig(
        fields=[ProjectionFieldConfig("candidate_id", "candidate_id")],
        missing_value_policy="error",
    )

    with pytest.raises(MissingProjectionValueError):
        ConfigurableProjector().project(build_recruiter_candidate(), config)


def test_schema_validator_accepts_valid_payload() -> None:
    """Schema validation should succeed for a payload matching the schema."""

    payload = {
        "full_name": "Tanmay Sharma",
        "primary_email": "tanmay@gmail.com",
        "confidence": {"overall": 0.95, "fields": {"full_name": 0.95}},
        "provenance": [{"field": "full_name", "source": "Recruiter CSV", "method": "merged"}],
    }
    schema = {
        "type": "object",
        "allow_extra_fields": False,
        "properties": {
            "full_name": {"type": "string", "required": True},
            "primary_email": {"type": "string", "required": True},
            "confidence": {
                "type": "object",
                "required": True,
                "allow_extra_fields": True,
                "properties": {
                    "overall": {"type": "number", "required": True},
                    "fields": {"type": "object", "required": True},
                },
            },
            "provenance": {
                "type": "list",
                "required": True,
                "items": {
                    "type": "object",
                    "allow_extra_fields": False,
                    "properties": {
                        "field": {"type": "string", "required": True},
                        "source": {"type": "string", "required": True},
                        "method": {"type": "string", "required": True},
                    },
                },
            },
        },
    }

    SchemaValidator().validate(payload, schema)


def test_schema_validator_raises_for_missing_or_invalid_values() -> None:
    """Schema validation should fail for missing required fields or wrong types."""

    schema = {
        "type": "object",
        "allow_extra_fields": False,
        "properties": {
            "full_name": {"type": "string", "required": True},
            "score": {"type": "number", "required": True},
        },
    }

    with pytest.raises(SchemaValidationError):
        SchemaValidator().validate({"full_name": None, "score": 1.0}, schema)

    with pytest.raises(SchemaValidationError):
        SchemaValidator().validate({"full_name": "Tanmay", "score": "high"}, schema)


def test_schema_validator_rejects_invalid_schema_definition() -> None:
    """Malformed schema definitions should raise a meaningful exception."""

    invalid_schema = {
        "type": "object",
        "properties": {
            "full_name": {"required": True},
        },
    }

    with pytest.raises(InvalidSchemaDefinitionError):
        SchemaValidator().validate({"full_name": "Tanmay"}, invalid_schema)
