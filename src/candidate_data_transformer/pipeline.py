"""Pipeline contracts for the end-to-end candidate transformation workflow."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from candidate_data_transformer.confidence import ConfidenceService, build_confidence_service
from candidate_data_transformer.merger import MergeService, build_merge_service
from candidate_data_transformer.models import RawCandidatePayload, TransformationResult
from candidate_data_transformer.normalizers import (
    NormalizationService,
    build_normalization_service,
)
from candidate_data_transformer.parsers import ParserRegistry, build_parser_registry
from candidate_data_transformer.projector import (
    ProjectionService,
    build_projection_service,
)
from candidate_data_transformer.provenance import (
    ProvenanceService,
    build_provenance_service,
)
from candidate_data_transformer.validator import (
    ValidationService,
    build_validation_service,
)


@dataclass(slots=True)
class CandidateTransformationPipeline:
    """Coordinator for the future multi-stage transformation process."""

    parser_registry: ParserRegistry
    normalization_service: NormalizationService
    merge_service: MergeService
    confidence_service: ConfidenceService
    provenance_service: ProvenanceService
    projection_service: ProjectionService
    validation_service: ValidationService

    def transform(
        self,
        payloads: Sequence[RawCandidatePayload],
    ) -> TransformationResult:
        """Transform raw candidate payloads into a final projected result."""

        raise NotImplementedError(
            "CandidateTransformationPipeline.transform is not implemented yet."
        )


def build_pipeline() -> CandidateTransformationPipeline:
    """Create a pipeline instance with placeholder stage services."""

    return CandidateTransformationPipeline(
        parser_registry=build_parser_registry(),
        normalization_service=build_normalization_service(),
        merge_service=build_merge_service(),
        confidence_service=build_confidence_service(),
        provenance_service=build_provenance_service(),
        projection_service=build_projection_service(),
        validation_service=build_validation_service(),
    )
