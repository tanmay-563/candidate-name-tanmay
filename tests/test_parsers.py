"""Unit tests for the parser layer."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from candidate_data_transformer.parsers import (
    GitHubJSONParser,
    MultipleCandidatesError,
    ParserFactory,
    RecruiterCSVParser,
    UnsupportedParserError,
)


def test_recruiter_csv_parser_creates_candidates_from_rows(tmp_path: Path) -> None:
    """Recruiter CSV parsing should create candidates and ignore empty rows."""

    csv_path = tmp_path / "recruiter.csv"
    csv_path.write_text(
        (
            "name,email,phone,current_company,title\n"
            "Ada Lovelace,ada@example.com,123,Analytical Engines Ltd,Engineer\n"
            ",,,,\n"
            "Grace Hopper,grace@example.com,456,US Navy,Rear Admiral\n"
        ),
        encoding="utf-8",
    )

    candidates = RecruiterCSVParser().parse_many(csv_path)

    assert len(candidates) == 2
    assert candidates[0].full_name == "Ada Lovelace"
    assert candidates[0].emails == ["ada@example.com"]
    assert candidates[0].experience[0].company == "Analytical Engines Ltd"
    assert candidates[1].full_name == "Grace Hopper"


def test_recruiter_csv_parser_handles_missing_columns_gracefully(
    tmp_path: Path,
) -> None:
    """Recruiter CSV parsing should still succeed when optional columns are missing."""

    csv_path = tmp_path / "recruiter_missing_columns.csv"
    csv_path.write_text(
        "name,email\nAda Lovelace,ada@example.com\n",
        encoding="utf-8",
    )

    candidate = RecruiterCSVParser().parse(csv_path)

    assert candidate.full_name == "Ada Lovelace"
    assert candidate.emails == ["ada@example.com"]
    assert candidate.experience == []


def test_recruiter_csv_parser_parse_raises_for_multiple_candidates(
    tmp_path: Path,
) -> None:
    """Single-candidate parsing should fail for batch recruiter CSV input."""

    csv_path = tmp_path / "recruiter.csv"
    csv_path.write_text(
        "name,email\nAda Lovelace,ada@example.com\nGrace Hopper,grace@example.com\n",
        encoding="utf-8",
    )

    with pytest.raises(MultipleCandidatesError):
        RecruiterCSVParser().parse(csv_path)


def test_github_json_parser_extracts_candidate_data(tmp_path: Path) -> None:
    """GitHub JSON parsing should populate candidate fields from profile data."""

    json_path = tmp_path / "github.json"
    json_path.write_text(
        json.dumps(
            {
                "name": "Linus Torvalds",
                "bio": "Software engineer",
                "languages": ["C", "Python"],
                "repos": [{"language": "C"}, {"languages": ["Python", "Go"]}],
                "email": "linus@example.com",
                "location": "Portland",
                "html_url": "https://github.com/torvalds",
            }
        ),
        encoding="utf-8",
    )

    candidate = GitHubJSONParser().parse(json_path)

    assert candidate.full_name == "Linus Torvalds"
    assert candidate.headline == "Software engineer"
    assert candidate.emails == ["linus@example.com"]
    assert candidate.location == "Portland"
    assert candidate.skills == ["C", "Python", "Go"]
    assert candidate.links[0].url == "https://github.com/torvalds"


def test_parser_factory_selects_parser_by_file_extension(tmp_path: Path) -> None:
    """The parser factory should choose the appropriate parser for a file."""

    factory = ParserFactory()

    csv_path = tmp_path / "input.csv"
    json_path = tmp_path / "input.json"
    text_path = tmp_path / "input.txt"

    assert isinstance(factory.create(csv_path), RecruiterCSVParser)
    assert isinstance(factory.create(json_path), GitHubJSONParser)

    with pytest.raises(UnsupportedParserError):
        factory.create(text_path)
