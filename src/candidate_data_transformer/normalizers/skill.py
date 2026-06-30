"""Skill normalization utilities for canonical candidate skill names."""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate_data_transformer.normalizers.base import BaseNormalizer


def default_skill_aliases() -> dict[str, str]:
    """Build the default mapping of skill aliases to canonical names."""

    return {
        "cpp": "C++",
        "c++": "C++",
        "c plus plus": "C++",
        "js": "JavaScript",
        "javascript": "JavaScript",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "node js": "Node.js",
        "py": "Python",
        "python": "Python",
        "python3": "Python",
        "golang": "Go",
        "go": "Go",
        "ts": "TypeScript",
        "typescript": "TypeScript",
        "postgres": "PostgreSQL",
        "postgresql": "PostgreSQL",
        "sql": "SQL",
        "aws": "AWS",
    }


@dataclass(slots=True)
class SkillNormalizer(BaseNormalizer[str | None, str | None]):
    """Normalize raw skill labels into canonical skill names."""

    aliases: dict[str, str] = field(default_factory=default_skill_aliases)

    def normalize(self, value: str | None) -> str | None:
        """Normalize a raw skill label using the configured alias mapping."""

        if value is None:
            return None

        cleaned_value = " ".join(value.strip().split())

        if not cleaned_value:
            return None

        canonical_skill = self.aliases.get(cleaned_value.casefold())

        if canonical_skill is not None:
            return canonical_skill

        return cleaned_value
