"""Domain model for the canonical candidate profile."""

from __future__ import annotations

from dataclasses import dataclass, field

from candidate_data_transformer.models._validation import (
    normalize_confidence_score,
    normalize_model_list,
    normalize_non_negative_float,
    normalize_optional_text,
    normalize_required_text,
    normalize_string_list,
)
from candidate_data_transformer.models.education import Education
from candidate_data_transformer.models.experience import Experience
from candidate_data_transformer.models.link import Link
from candidate_data_transformer.models.provenance import ProvenanceEntry


@dataclass(slots=True)
class Candidate:
    """Represents the canonical candidate profile used throughout the transformer."""

    candidate_id: str | None = None
    full_name: str | None = None
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    location: str | None = None
    links: list[Link] = field(default_factory=list)
    headline: str | None = None
    years_experience: float | None = None
    skills: list[str] = field(default_factory=list)
    experience: list[Experience] = field(default_factory=list)
    education: list[Education] = field(default_factory=list)
    provenance: list[ProvenanceEntry] = field(default_factory=list)
    overall_confidence: float = 0.0

    def __post_init__(self) -> None:
        """Normalize optional fields and validate nested model collections."""

        self.candidate_id = normalize_optional_text(self.candidate_id, "candidate_id")
        self.full_name = normalize_optional_text(self.full_name, "full_name")
        self.emails = normalize_string_list(self.emails, "emails")
        self.phones = normalize_string_list(self.phones, "phones")
        self.location = normalize_optional_text(self.location, "location")
        self.links = normalize_model_list(self.links, Link, "links")
        self.headline = normalize_optional_text(self.headline, "headline")
        self.years_experience = normalize_non_negative_float(
            self.years_experience,
            "years_experience",
        )
        self.skills = normalize_string_list(self.skills, "skills")
        self.experience = normalize_model_list(
            self.experience,
            Experience,
            "experience",
        )
        self.education = normalize_model_list(self.education, Education, "education")
        self.provenance = normalize_model_list(
            self.provenance,
            ProvenanceEntry,
            "provenance",
        )
        self.overall_confidence = normalize_confidence_score(
            self.overall_confidence,
            "overall_confidence",
        )

    def add_email(self, email: str) -> None:
        """Add an email address when it is not already present."""

        normalized_email = normalize_required_text(email, "email")

        if normalized_email.casefold() not in {
            existing_email.casefold() for existing_email in self.emails
        }:
            self.emails.append(normalized_email)

    def add_phone(self, phone: str) -> None:
        """Add a phone number when it is not already present."""

        normalized_phone = normalize_required_text(phone, "phone")

        if normalized_phone not in self.phones:
            self.phones.append(normalized_phone)

    def add_skill(self, skill: str) -> None:
        """Add a skill when it is not already present."""

        normalized_skill = normalize_required_text(skill, "skill")

        if normalized_skill.casefold() not in {
            existing_skill.casefold() for existing_skill in self.skills
        }:
            self.skills.append(normalized_skill)

    def add_link(self, link: Link) -> None:
        """Attach a link entry to the candidate when it is not already present."""

        if not isinstance(link, Link):
            raise TypeError("link must be an instance of Link.")

        if link not in self.links:
            self.links.append(link)

    def add_experience(self, experience_entry: Experience) -> None:
        """Attach an experience entry to the candidate."""

        if not isinstance(experience_entry, Experience):
            raise TypeError("experience_entry must be an instance of Experience.")

        self.experience.append(experience_entry)

    def add_education(self, education_entry: Education) -> None:
        """Attach an education entry to the candidate."""

        if not isinstance(education_entry, Education):
            raise TypeError("education_entry must be an instance of Education.")

        self.education.append(education_entry)

    def add_provenance(self, provenance_entry: ProvenanceEntry) -> None:
        """Attach a provenance entry to the candidate."""

        if not isinstance(provenance_entry, ProvenanceEntry):
            raise TypeError("provenance_entry must be an instance of ProvenanceEntry.")

        self.provenance.append(provenance_entry)

    def primary_email(self) -> str | None:
        """Return the first available email address, if one exists."""

        return self.emails[0] if self.emails else None

    def primary_phone(self) -> str | None:
        """Return the first available phone number, if one exists."""

        return self.phones[0] if self.phones else None

    def has_contact_details(self) -> bool:
        """Return whether the candidate has at least one email or phone number."""

        return bool(self.emails or self.phones)

    def __repr__(self) -> str:
        """Return a concise developer-friendly representation of the candidate."""

        return (
            "Candidate("
            f"candidate_id={self.candidate_id!r}, "
            f"full_name={self.full_name!r}, "
            f"emails={len(self.emails)}, "
            f"phones={len(self.phones)}, "
            f"skills={len(self.skills)}, "
            f"experience={len(self.experience)}, "
            f"education={len(self.education)}, "
            f"overall_confidence={self.overall_confidence:.2f})"
        )
