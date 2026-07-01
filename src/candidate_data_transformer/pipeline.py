"""Integrated pipeline orchestration for the candidate data transformer."""

from __future__ import annotations

import logging
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from candidate_data_transformer.confidence import (
    ConfidenceService,
    build_confidence_service,
)
from candidate_data_transformer.config.runtime import RuntimeConfig, RuntimeConfigLoader
from candidate_data_transformer.merger import MergeService, build_merge_service
from candidate_data_transformer.models import Candidate, TransformationResult, ValidationIssue
from candidate_data_transformer.normalizers import (
    NormalizationService,
    build_normalization_service,
)
from candidate_data_transformer.parsers import (
    ParserFactory,
    ParserRegistry,
    build_parser_registry,
)
from candidate_data_transformer.parsers.exceptions import ParserError, UnsupportedParserError
from candidate_data_transformer.pipeline_exceptions import (
    PipelineConfigurationError,
    PipelineInputError,
    PipelineOutputError,
    PipelineProcessingError,
)
from candidate_data_transformer.projector import (
    ProjectionService,
    build_projection_service,
)
from candidate_data_transformer.projector.exceptions import ProjectionError
from candidate_data_transformer.provenance import (
    ProvenanceService,
    build_provenance_service,
)
from candidate_data_transformer.validator import (
    ValidationService,
    build_validation_service,
)
from candidate_data_transformer.validator.exceptions import (
    InvalidSchemaDefinitionError,
    SchemaValidationError,
)


@dataclass(slots=True)
class Pipeline:
    """Coordinate the full candidate ingestion and transformation workflow."""

    parser_registry: ParserRegistry
    normalization_service: NormalizationService
    merge_service: MergeService
    confidence_service: ConfidenceService
    provenance_service: ProvenanceService
    projection_service: ProjectionService
    validation_service: ValidationService
    logger: logging.Logger = field(
        default_factory=lambda: logging.getLogger(
            "candidate_data_transformer.pipeline.Pipeline"
        )
    )
    parser_factory: ParserFactory = field(init=False)
    config_loader: RuntimeConfigLoader = field(init=False)

    def __post_init__(self) -> None:
        """Initialize dependent helpers derived from injected services."""

        self.parser_factory = ParserFactory(
            registry=self.parser_registry,
            logger=self.logger,
        )
        self.config_loader = RuntimeConfigLoader(logger=self.logger)

    def run(
        self,
        inputs: Sequence[Path | str],
        config_path: Path | str,
    ) -> dict[str, Any]:
        """Run the full pipeline and return the projected JSON-ready payload."""

        result = self.transform(inputs=inputs, config_path=config_path)
        return dict(result.projected_payload or {})

    def transform(
        self,
        inputs: Sequence[Path | str],
        config_path: Path | str,
    ) -> TransformationResult:
        """Run the full pipeline and return the rich transformation result."""

        input_paths = self._resolve_input_paths(inputs)
        runtime_config = self._load_runtime_config(config_path)

        parsed_candidates, warnings = self._parse_inputs(input_paths)

        if not parsed_candidates:
            raise PipelineInputError(
                "No candidate records could be parsed from the provided inputs."
            )

        normalized_candidates = self._normalize_candidates(parsed_candidates, warnings)

        if not normalized_candidates:
            raise PipelineInputError(
                "No candidate records remained after normalization."
            )

        try:
            merged_candidate = self.merge_service.merge_records(normalized_candidates)
            provenance_entries = self.provenance_service.collect_entries(merged_candidate)
            confidence_assessment = self.confidence_service.score_candidate(
                merged_candidate
            )
            merged_candidate.overall_confidence = (
                confidence_assessment.overall_score or 0.0
            )
        except Exception as error:
            raise PipelineProcessingError(
                "Pipeline processing failed during merge, provenance, or confidence steps."
            ) from error

        projected_payload = self._project_candidate(
            merged_candidate,
            runtime_config,
            confidence_assessment,
            provenance_entries,
        )
        self._validate_output(projected_payload, runtime_config)

        return TransformationResult(
            candidate=merged_candidate,
            projected_payload=projected_payload,
            confidence=confidence_assessment,
            provenance=provenance_entries,
            validation_issues=warnings,
        )

    def load_runtime_config(self, config_path: Path | str) -> RuntimeConfig:
        """Load runtime pipeline configuration from a JSON file path."""

        return self._load_runtime_config(config_path)

    def detect_source_type(self, input_path: Path | str) -> str:
        """Detect the source type associated with a given input file path."""

        resolved_path = Path(input_path)
        parser = self.parser_factory.create(resolved_path)
        return getattr(parser, "parser_name", resolved_path.suffix.lstrip("."))

    def _resolve_input_paths(self, inputs: Sequence[Path | str]) -> list[Path]:
        """Normalize CLI or API input values into path objects."""

        if not inputs:
            raise PipelineInputError("At least one input path must be provided.")

        resolved_paths: list[Path] = []

        for raw_input in inputs:
            if isinstance(raw_input, Path):
                resolved_paths.append(raw_input)
                continue

            if not isinstance(raw_input, str) or not raw_input.strip():
                raise PipelineInputError(
                    "Every input value must be a non-empty file path."
                )

            resolved_paths.append(Path(raw_input.strip()))

        return resolved_paths

    def _load_runtime_config(self, config_path: Path | str) -> RuntimeConfig:
        """Load and validate runtime configuration for the pipeline."""

        resolved_path = config_path if isinstance(config_path, Path) else Path(config_path)

        try:
            return self.config_loader.load(resolved_path)
        except Exception as error:
            raise PipelineConfigurationError(
                f"Unable to load runtime config from '{resolved_path}'."
            ) from error

    def _parse_inputs(
        self,
        input_paths: Sequence[Path],
    ) -> tuple[list[Candidate], list[ValidationIssue]]:
        """Parse every input file into one or more candidate objects."""

        parsed_candidates: list[Candidate] = []
        warnings: list[ValidationIssue] = []

        for input_path in input_paths:
            try:
                source_type = self.detect_source_type(input_path)
                candidates = self._parse_source(input_path)
            except UnsupportedParserError as error:
                self.logger.warning("Skipping unsupported input '%s': %s", input_path, error)
                warnings.append(
                    self._warning_issue(
                        code="unsupported_source",
                        message=str(error),
                        field_name=str(input_path),
                    )
                )
                continue
            except ParserError as error:
                self.logger.warning("Skipping malformed input '%s': %s", input_path, error)
                warnings.append(
                    self._warning_issue(
                        code="parse_error",
                        message=str(error),
                        field_name=str(input_path),
                    )
                )
                continue

            if not candidates:
                self.logger.warning("Input '%s' did not yield any candidate records.", input_path)
                warnings.append(
                    self._warning_issue(
                        code="empty_source",
                        message=f"Input '{input_path}' did not yield any candidate records.",
                        field_name=str(input_path),
                    )
                )
                continue

            self.logger.info(
                "Parsed %s candidate record(s) from '%s' as source '%s'.",
                len(candidates),
                input_path,
                source_type,
            )
            parsed_candidates.extend(candidates)

        return parsed_candidates, warnings

    def _parse_source(self, input_path: Path) -> list[Candidate]:
        """Parse a single input source into one or more candidate objects."""

        parser = self.parser_factory.create(input_path)
        parse_many_method = getattr(parser, "parse_many", None)

        if callable(parse_many_method):
            parsed_candidates = parse_many_method(input_path)
        else:
            parsed_candidates = [parser.parse(input_path)]

        if any(not isinstance(candidate, Candidate) for candidate in parsed_candidates):
            raise PipelineProcessingError(
                f"Parser for '{input_path}' returned a non-candidate result."
            )

        return list(parsed_candidates)

    def _normalize_candidates(
        self,
        candidates: Sequence[Candidate],
        warnings: list[ValidationIssue],
    ) -> list[Candidate]:
        """Normalize parsed candidates while skipping malformed records."""

        normalized_candidates: list[Candidate] = []

        for index, candidate in enumerate(candidates):
            try:
                normalized_candidates.append(
                    self.normalization_service.normalize_candidate(candidate)
                )
            except Exception as error:
                self.logger.warning(
                    "Skipping candidate at position %s during normalization: %s",
                    index,
                    error,
                )
                warnings.append(
                    self._warning_issue(
                        code="normalization_error",
                        message=f"Candidate at position {index} could not be normalized.",
                        field_name=str(index),
                    )
                )

        return normalized_candidates

    def _project_candidate(
        self,
        candidate: Candidate,
        runtime_config: RuntimeConfig,
        confidence_assessment: Any,
        provenance_entries: Any,
    ) -> dict[str, Any]:
        """Project the merged candidate into the configured output payload."""

        try:
            projected_payload = self.projection_service.project_candidate(
                candidate,
                runtime_config.projection,
                confidence=confidence_assessment,
                provenance=provenance_entries,
            )
        except ProjectionError as error:
            raise PipelineOutputError("Projection failed for the merged candidate.") from error
        except Exception as error:
            raise PipelineOutputError(
                "Unexpected error occurred while projecting the merged candidate."
            ) from error

        if not isinstance(projected_payload, Mapping):
            raise PipelineOutputError("Projection layer did not return a mapping payload.")

        return dict(projected_payload)

    def _validate_output(
        self,
        payload: Mapping[str, Any],
        runtime_config: RuntimeConfig,
    ) -> None:
        """Validate the projected payload against the configured output schema."""

        try:
            self.validation_service.validate_output(payload, runtime_config.schema)
        except (SchemaValidationError, InvalidSchemaDefinitionError) as error:
            raise PipelineOutputError("Projected payload failed schema validation.") from error
        except Exception as error:
            raise PipelineOutputError(
                "Unexpected error occurred while validating the projected payload."
            ) from error

    def _warning_issue(
        self,
        code: str,
        message: str,
        field_name: str | None = None,
    ) -> ValidationIssue:
        """Create a standardized warning issue for non-fatal pipeline events."""

        return ValidationIssue(
            code=code,
            message=message,
            field_name=field_name,
            severity="warning",
        )


CandidateTransformationPipeline = Pipeline


def build_pipeline() -> CandidateTransformationPipeline:
    """Create a fully wired pipeline instance for application use."""

    return CandidateTransformationPipeline(
        parser_registry=build_parser_registry(),
        normalization_service=build_normalization_service(),
        merge_service=build_merge_service(),
        confidence_service=build_confidence_service(),
        provenance_service=build_provenance_service(),
        projection_service=build_projection_service(),
        validation_service=build_validation_service(),
    )
