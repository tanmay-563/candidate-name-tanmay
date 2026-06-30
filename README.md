# Multi-Source Candidate Data Transformer

Production-style Python project scaffold for an engineering internship assignment focused on transforming candidate data from multiple upstream sources into a canonical internal representation.

## Highlights

- Python 3.11+ oriented structure
- `src/`-based layout for clean imports and packaging
- Modular pipeline boundaries for parsing, normalization, merging, confidence scoring, provenance, projection, and validation
- Lightweight application shell ready for future implementation
- Test scaffold and architecture notes for maintainability

## Project Structure

```text
.
├── .gitignore
├── README.md
├── data/
│   └── README.md
├── docs/
│   └── architecture.md
├── main.py
├── requirements.txt
├── src/
│   └── candidate_data_transformer/
│       ├── __init__.py
│       ├── app.py
│       ├── pipeline.py
│       ├── confidence/
│       ├── config/
│       ├── merger/
│       ├── models/
│       ├── normalizers/
│       ├── parsers/
│       ├── projector/
│       ├── provenance/
│       ├── utils/
│       └── validator/
└── tests/
    ├── conftest.py
    └── test_smoke.py
```

## Getting Started

1. Create a Python 3.11+ virtual environment.
2. Install dependencies with `pip install -r requirements.txt`.
3. Run the placeholder entrypoint with `python main.py`.
4. Run scaffold checks with `pytest`.

## Architectural Direction

- `models`: Shared domain objects and pipeline result contracts
- `parsers`: Source-specific raw payload parsing interfaces
- `normalizers`: Canonicalization contracts for parsed source documents
- `merger`: Candidate record consolidation interfaces
- `confidence`: Confidence scoring interfaces for transformed records
- `provenance`: Traceability interfaces for source attribution
- `projector`: Output projection interfaces for downstream consumers
- `validator`: Validation interfaces for quality and schema checks
- `config`: Application settings and project path management
- `utils`: Cross-cutting infrastructure helpers such as logging

No business logic has been implemented yet. The current scaffold focuses on maintainable boundaries, type safety, and extension points.
