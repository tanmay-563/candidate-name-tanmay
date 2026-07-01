"""Projection engine for building configurable output payloads."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from candidate_data_transformer.models import (
    Candidate,
    ConfidenceAssessment,
    ProvenanceEntry,
)
from candidate_data_transformer.projector.accessor import (
    MISSING_VALUE,
    FieldPathAccessor,
)
from candidate_data_transformer.projector.config import (
    ProjectionConfig,
    ProjectionConfigLoader,
)
from candidate_data_transformer.projector.exceptions import (
    MissingProjectionValueError,
)
from candidate_data_transformer.projector.serializer import ProjectionSerializer


@dataclass(slots=True)
class ProjectionEngine:
    """Project a canonical candidate into a configurable output payload."""

    accessor: FieldPathAccessor = field(default_factory=FieldPathAccessor)
    serializer: ProjectionSerializer = field(default_factory=ProjectionSerializer)
    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(
            "candidate_data_transformer.projector.ProjectionEngine"
        )
    )

    def project(
        self,
        record: Candidate,
        config: ProjectionConfig,
        *,
        confidence: ConfidenceAssessment | None = None,
        provenance: list[ProvenanceEntry] | None = None,
    ) -> dict[str, Any]:
        """Project a candidate record into a configured output dictionary."""

        if not isinstance(record, Candidate):
            raise TypeError("record must be an instance of Candidate.")

        projected_payload: dict[str, Any] = {}

        for field_config in config.fields:
            raw_value = self.accessor.extract(record, field_config.source_path)

            if raw_value is MISSING_VALUE or raw_value is None:
                if not self._apply_missing_policy(
                    payload=projected_payload,
                    output_key=field_config.target_name,
                    config=config,
                    source_path=field_config.source_path,
                ):
                    continue
            else:
                projected_payload[field_config.target_name] = self.serializer.serialize(
                    raw_value,
                    normalize_output=field_config.normalize_output,
                )

        if config.include_confidence:
            confidence_payload = self._build_confidence_payload(confidence)

            if confidence_payload is None:
                self._apply_missing_policy(
                    payload=projected_payload,
                    output_key="confidence",
                    config=config,
                    source_path="confidence",
                )
            else:
                projected_payload["confidence"] = confidence_payload

        if config.include_provenance:
            provenance_payload = self._build_provenance_payload(
                provenance if provenance is not None else record.provenance
            )

            if provenance_payload is None:
                self._apply_missing_policy(
                    payload=projected_payload,
                    output_key="provenance",
                    config=config,
                    source_path="provenance",
                )
            else:
                projected_payload["provenance"] = provenance_payload

        self.logger.info(
            "Projected candidate into payload with %s top-level key(s).",
            len(projected_payload),
        )
        return projected_payload

    def _apply_missing_policy(
        self,
        payload: dict[str, Any],
        output_key: str,
        config: ProjectionConfig,
        source_path: str,
    ) -> bool:
        """Apply the configured missing-value policy for a projected field."""

        if config.missing_value_policy == "omit":
            return False

        if config.missing_value_policy == "null":
            payload[output_key] = None
            return True

        raise MissingProjectionValueError(
            f"Projected value for '{source_path}' is missing and policy is 'error'."
        )

    def _build_confidence_payload(
        self,
        confidence: ConfidenceAssessment | None,
    ) -> dict[str, Any] | None:
        """Build a serializable confidence payload when available."""

        if confidence is None:
            return None

        return {
            "overall": confidence.overall_score,
            "fields": dict(confidence.field_scores),
        }

    def _build_provenance_payload(
        self,
        provenance: list[ProvenanceEntry] | None,
    ) -> list[dict[str, Any]] | None:
        """Build a serializable provenance payload when available."""

        if provenance is None:
            return None

        return self.serializer.serialize(provenance, normalize_output=True)


@dataclass(slots=True)
class ConfigurableProjector:
    """Project a candidate using either a pre-built config or a JSON config path."""

    engine: ProjectionEngine = field(default_factory=ProjectionEngine)
    config_loader: ProjectionConfigLoader = field(default_factory=ProjectionConfigLoader)

    def project(
        self,
        record: Candidate,
        config: ProjectionConfig | Path,
        *,
        confidence: ConfidenceAssessment | None = None,
        provenance: list[ProvenanceEntry] | None = None,
    ) -> dict[str, Any]:
        """Project a candidate using the provided config object or config file path."""

        resolved_config = (
            self.config_loader.load(config)
            if isinstance(config, Path)
            else config
        )
        return self.engine.project(
            record,
            resolved_config,
            confidence=confidence,
            provenance=provenance,
        )
