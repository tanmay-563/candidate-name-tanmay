# Architecture

## High-Level Architecture

The system is organized as a staged data pipeline. Each stage owns one responsibility and communicates through explicit domain models.

Flow:

1. `parsers` read raw files and emit `Candidate` models.
2. `normalizers` canonicalize field values such as email, phone, skills, dates, and location.
3. `merger` combines multiple normalized candidates into one canonical record.
4. `provenance` produces field-level lineage metadata.
5. `confidence` assigns deterministic field and overall confidence scores.
6. `projector` maps the internal model into a runtime-configurable output payload.
7. `validator` enforces the final schema before serialization.
8. `pipeline` orchestrates the end-to-end flow and the CLI remains thin.

## Component Responsibilities

- `models`: canonical dataclasses and result containers
- `parsers`: source-specific ingestion adapters
- `normalizers`: canonicalization rules
- `merger`: conflict resolution and deduplication
- `provenance`: field-level output lineage
- `confidence`: deterministic source-based scoring
- `projector`: configurable output selection, renaming, and missing-value handling
- `validator`: schema enforcement
- `config`: project and runtime configuration loading
- `utils`: shared helpers such as source-priority logic

## Data Flow

Raw file -> parser -> `Candidate` -> normalizer -> normalized `Candidate` -> merger -> merged `Candidate` -> provenance + confidence -> projector -> validator -> JSON output

## Design Decisions

- Dataclasses were used instead of heavier modeling libraries to keep the assignment dependency-light and explicit.
- Engines contain business behavior; service wrappers keep wiring simple and testable.
- Runtime configuration is JSON-based so output shape can change without code changes.
- Validation happens after projection, which guarantees the serialized contract is checked rather than only the internal model.

## Why The Architecture Is Modular

- Each layer can be unit-tested independently.
- New sources can be added by implementing another parser and registering it.
- Projection and validation are isolated from parsing and normalization concerns.
- The CLI does not own business logic, which keeps orchestration reusable from tests or future APIs.

## Trade-Offs

- File-type detection is extension-based, which is simple but less robust than content sniffing.
- The current pipeline merges all parsed candidates into one record, which is sufficient for the assignment but not full identity resolution.
- Confidence depends on provenance. Because current parsers do not populate detailed provenance, many populated fields currently resolve to `Unknown`.
- A custom schema validator keeps dependencies low, but it is narrower than full JSON Schema support.
