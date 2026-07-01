"""Integration tests for the runtime pipeline and CLI wiring."""

from __future__ import annotations

import json
from pathlib import Path

from candidate_data_transformer.app import build_application


def build_runtime_config_payload() -> dict[str, object]:
    """Create a minimal runtime config payload for integration tests."""

    return {
        "projection": {
            "select_fields": [
                "full_name",
                "emails[0]",
                "phones[0]",
                "skills",
            ],
            "rename_fields": {
                "emails[0]": "primary_email",
                "phones[0]": "primary_phone",
            },
            "include_confidence": True,
            "include_provenance": True,
            "missing_value_policy": "omit",
        },
        "schema": {
            "type": "object",
            "allow_extra_fields": False,
            "properties": {
                "full_name": {"type": "string", "required": True},
                "primary_email": {"type": "string", "required": True},
                "primary_phone": {"type": "string", "required": True},
                "skills": {
                    "type": "list",
                    "required": True,
                    "items": {"type": "string"},
                },
                "confidence": {
                    "type": "object",
                    "required": True,
                    "allow_extra_fields": True,
                },
                "provenance": {
                    "type": "list",
                    "required": True,
                    "items": {
                        "type": "object",
                        "allow_extra_fields": True,
                    },
                },
            },
        },
    }


def test_pipeline_runs_end_to_end_from_sample_inputs(tmp_path: Path) -> None:
    """The integrated pipeline should produce a schema-valid JSON payload."""

    recruiter_path = tmp_path / "recruiter.csv"
    recruiter_path.write_text(
        (
            "name,email,phone,current_company,title\n"
            "Tanmay Sharma,tanmay.sharma@gmail.com,9876543210,Eightfold AI,Backend Engineer\n"
        ),
        encoding="utf-8",
    )

    github_path = tmp_path / "github.json"
    github_path.write_text(
        json.dumps(
            {
                "login": "tanmay-sharma",
                "name": "Tanmay S.",
                "bio": "Senior Backend Engineer",
                "languages": ["python3", "js"],
                "repos": [{"language": "Go"}],
                "email": "tanmay.sharma@gmail.com",
                "html_url": "https://github.com/tanmay-sharma",
            }
        ),
        encoding="utf-8",
    )

    config_path = tmp_path / "default.json"
    config_path.write_text(
        json.dumps(build_runtime_config_payload()),
        encoding="utf-8",
    )

    application = build_application(project_root=Path(__file__).resolve().parent.parent)
    result = application.pipeline.transform(
        inputs=[recruiter_path, github_path],
        config_path=config_path,
    )

    assert result.projected_payload is not None
    assert result.projected_payload["full_name"] == "Tanmay Sharma"
    assert result.projected_payload["primary_email"] == "tanmay.sharma@gmail.com"
    assert result.projected_payload["primary_phone"] == "+919876543210"
    assert "confidence" in result.projected_payload
    assert "provenance" in result.projected_payload


def test_cli_main_writes_output_file(tmp_path: Path) -> None:
    """The CLI entrypoint should write the final JSON output file."""

    from main import main as cli_main

    recruiter_path = tmp_path / "recruiter.csv"
    recruiter_path.write_text(
        (
            "name,email,phone,current_company,title\n"
            "Tanmay Sharma,tanmay.sharma@gmail.com,9876543210,Eightfold AI,Backend Engineer\n"
        ),
        encoding="utf-8",
    )

    github_path = tmp_path / "github.json"
    github_path.write_text(
        json.dumps(
            {
                "login": "tanmay-sharma",
                "name": "Tanmay S.",
                "bio": "Senior Backend Engineer",
                "languages": ["python3", "js"],
                "repos": [{"language": "Go"}],
                "email": "tanmay.sharma@gmail.com",
                "html_url": "https://github.com/tanmay-sharma",
            }
        ),
        encoding="utf-8",
    )

    config_path = tmp_path / "default.json"
    config_path.write_text(
        json.dumps(build_runtime_config_payload()),
        encoding="utf-8",
    )

    output_path = tmp_path / "result.json"
    exit_code = cli_main(
        [
            "--inputs",
            str(recruiter_path),
            str(github_path),
            "--config",
            str(config_path),
            "--output",
            str(output_path),
        ]
    )

    assert exit_code == 0
    assert output_path.exists()
