# Architecture Overview

## Goals

- Keep domain concerns isolated and easy to test independently
- Support multiple upstream candidate data providers without coupling their schemas together
- Make provenance, confidence scoring, and validation first-class pipeline stages
- Preserve room for future interfaces such as APIs, batch jobs, or workflow orchestration

## High-Level Flow

1. Raw source payloads enter the system through parser interfaces.
2. Parsed source documents move into normalization services that shape them into canonical candidate records.
3. Canonical records are merged into a single candidate view.
4. Confidence and provenance services enrich the merged record.
5. Validation services assess completeness and quality.
6. Projection services map the internal representation into downstream output contracts.

## Package Responsibilities

- `candidate_data_transformer.app`: application composition and dependency wiring
- `candidate_data_transformer.pipeline`: end-to-end orchestration contract
- `candidate_data_transformer.models`: shared domain models and result objects
- `candidate_data_transformer.config`: project settings and environment-aware configuration
- `candidate_data_transformer.utils`: reusable infrastructure helpers

## Testing Strategy

- Unit test each stage contract in isolation
- Add fixture-based tests per source parser when input schemas are known
- Add pipeline integration tests once transformation behavior exists
- Validate provenance and confidence outputs as explicit artifacts, not side effects
