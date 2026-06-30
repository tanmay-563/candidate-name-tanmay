"""JSON parser for GitHub profile payloads."""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any, ClassVar

from candidate_data_transformer.models import Candidate, Link
from candidate_data_transformer.parsers.base import BaseParser
from candidate_data_transformer.parsers.exceptions import (
    ParserFileError,
    ParserInputError,
)


class GitHubJSONParser(BaseParser):
    """Parse a GitHub profile JSON document into a candidate model."""

    parser_name: ClassVar[str] = "github_json"
    supported_suffixes: ClassVar[tuple[str, ...]] = (".json",)

    def parse(self, path: Path) -> Candidate:
        """Parse a GitHub profile JSON file into a single candidate."""

        json_path = self.validate_path(path)
        self._logger.info("Parsing GitHub JSON file '%s'.", json_path)

        try:
            with json_path.open("r", encoding="utf-8") as file_handle:
                payload = json.load(file_handle)
        except OSError as error:
            raise ParserFileError(f"Unable to read GitHub JSON file '{json_path}'.") from error
        except json.JSONDecodeError as error:
            raise ParserInputError(
                f"GitHub JSON file '{json_path}' contains invalid JSON."
            ) from error

        if not isinstance(payload, Mapping):
            raise ParserInputError(
                f"GitHub JSON file '{json_path}' must contain a top-level object."
            )

        candidate = self._build_candidate_from_payload(payload)
        self._logger.info("Parsed candidate from GitHub JSON file '%s'.", json_path)
        return candidate

    def _build_candidate_from_payload(self, payload: Mapping[str, Any]) -> Candidate:
        """Create a candidate model from a GitHub profile payload."""

        candidate = Candidate(
            full_name=self._extract_name(payload),
            headline=self.to_optional_text(payload.get("bio")),
            emails=self._single_value_list(payload.get("email")),
            location=self.to_optional_text(payload.get("location")),
        )

        for skill in self._extract_skills(payload):
            candidate.add_skill(skill)

        github_url = self._extract_github_url(payload)

        if github_url is not None:
            candidate.add_link(Link(type="github", url=github_url))

        return candidate

    def _extract_name(self, payload: Mapping[str, Any]) -> str | None:
        """Extract the most descriptive available GitHub profile name."""

        return self.to_optional_text(payload.get("name")) or self.to_optional_text(
            payload.get("login")
        )

    def _extract_skills(self, payload: Mapping[str, Any]) -> list[str]:
        """Extract candidate skills from GitHub language metadata."""

        ordered_skills: list[str] = []
        seen_values: set[str] = set()

        self._collect_language_values(
            raw_value=payload.get("languages"),
            destination=ordered_skills,
            seen_values=seen_values,
        )

        repos = payload.get("repos")

        if isinstance(repos, Sequence) and not isinstance(repos, (str, bytes, bytearray)):
            for repo in repos:
                if not isinstance(repo, Mapping):
                    continue

                self._collect_language_values(
                    raw_value=repo.get("language"),
                    destination=ordered_skills,
                    seen_values=seen_values,
                )
                self._collect_language_values(
                    raw_value=repo.get("languages"),
                    destination=ordered_skills,
                    seen_values=seen_values,
                )

        return ordered_skills

    def _collect_language_values(
        self,
        raw_value: object,
        destination: list[str],
        seen_values: set[str],
    ) -> None:
        """Extract language values from a raw JSON field into a destination list."""

        if raw_value is None:
            return

        if isinstance(raw_value, str):
            self._append_skill(raw_value, destination, seen_values)
            return

        if isinstance(raw_value, Mapping):
            for language_name in raw_value.keys():
                self._append_skill(language_name, destination, seen_values)
            return

        if isinstance(raw_value, Iterable) and not isinstance(
            raw_value,
            (str, bytes, bytearray),
        ):
            for item in raw_value:
                if isinstance(item, Mapping):
                    self._append_skill(item.get("name"), destination, seen_values)
                    continue

                self._append_skill(item, destination, seen_values)

    def _append_skill(
        self,
        raw_value: object,
        destination: list[str],
        seen_values: set[str],
    ) -> None:
        """Append a language-derived skill if it contains meaningful text."""

        skill = self.to_optional_text(raw_value)

        if skill is None:
            return

        normalized_key = skill.casefold()

        if normalized_key in seen_values:
            return

        seen_values.add(normalized_key)
        destination.append(skill)

    def _extract_github_url(self, payload: Mapping[str, Any]) -> str | None:
        """Extract a public GitHub profile URL from the JSON payload."""

        for key in ("html_url", "profile_url", "github_url"):
            value = self.to_optional_text(payload.get(key))

            if value is not None:
                return value

        login = self.to_optional_text(payload.get("login"))

        if login is not None:
            return f"https://github.com/{login}"

        return None

    def _single_value_list(self, raw_value: object) -> list[str]:
        """Convert an optional scalar value into a single-item list when present."""

        value = self.to_optional_text(raw_value)
        return [value] if value else []
