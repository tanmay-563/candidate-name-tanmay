# Multi-Source Candidate Data Transformer

## Project Overview

The Multi-Source Candidate Data Transformer is a Python 3.11+ data ingestion pipeline that converts heterogeneous candidate data into a canonical internal representation and then projects that record into a runtime-configurable JSON output.

The current implementation supports:

- Recruiter CSV input
- GitHub profile JSON input
- canonical normalization of key fields
- deterministic merge, confidence, provenance, projection, and validation stages
- a CLI entrypoint for end-to-end execution

This repository is structured as a backend engineering assignment and is intentionally organized like a maintainable production codebase rather than a single-script prototype.

## Architecture Overview

The pipeline is split into focused layers:

- `parsers`: convert raw files into `Candidate` models
- `normalizers`: clean inconsistent field values into canonical form
- `merger`: combine multiple normalized candidate records
- `confidence`: compute deterministic field-level and overall confidence
- `provenance`: produce final field-level origin metadata
- `projector`: map the internal model into configurable output payloads
- `validator`: enforce the final output schema before serialization
- `pipeline`: orchestrate the full flow without embedding domain logic in the CLI

See [ARCHITECTURE.md](ARCHITECTURE.md) for the concise architecture handoff document.

## Features

- Python 3.11+ standard-library-first implementation
- `src/` layout for clean imports and future packaging
- dataclass-based domain models with validation in `__post_init__`
- deterministic merge and confidence behavior
- runtime-configurable output field selection and renaming
- schema validation before JSON output is written
- graceful handling of unsupported files, malformed data, and missing values
- testable service and engine boundaries

## Folder Structure

```text
.
├── .gitignore
├── ARCHITECTURE.md
├── DEMO.md
├── README.md
├── config/
│   ├── default.json
│   ├── minimal.json
│   ├── no_confidence.json
│   └── rename_fields.json
├── data/
│   ├── README.md
│   ├── github.json
│   └── recruiter.csv
├── docs/
│   └── architecture.md
├── main.py
├── output/
│   └── result.json
├── requirements.txt
├── src/
│   └── candidate_data_transformer/
│       ├── __init__.py
│       ├── app.py
│       ├── pipeline.py
│       ├── pipeline_exceptions.py
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
    ├── test_merge_and_confidence.py
    ├── test_normalizers.py
    ├── test_parsers.py
    ├── test_pipeline_integration.py
    ├── test_provenance_projection_validator.py
    └── test_smoke.py
```

## Pipeline Flow

1. The CLI receives input file paths, a runtime config path, and an output path.
2. The `Pipeline` loads runtime projection and schema configuration.
3. The `ParserFactory` selects a parser based on file suffix.
4. Each parser converts raw source data into one or more `Candidate` models.
5. The `CandidateNormalizer` canonicalizes contact details, skills, dates, and location.
6. The `MergeEngine` merges normalized candidates into one canonical candidate.
7. The `ProvenanceEngine` synthesizes final field-level provenance entries.
8. The `ConfidenceEngine` calculates field-level and overall confidence scores.
9. The `ProjectionEngine` builds the configured output payload.
10. The `SchemaValidator` validates the projected payload.
11. The CLI writes schema-valid JSON to disk.

## Canonical Schema

The internal canonical model is the `Candidate` dataclass:

```json
{
  "candidate_id": "str | null",
  "full_name": "str | null",
  "emails": ["str"],
  "phones": ["str"],
  "location": "str | null",
  "links": [
    {
      "type": "str | null",
      "url": "str | null"
    }
  ],
  "headline": "str | null",
  "years_experience": "float | null",
  "skills": ["str"],
  "experience": [
    {
      "company": "str | null",
      "title": "str | null",
      "start_date": "str | null",
      "end_date": "str | null",
      "summary": "str | null"
    }
  ],
  "education": [
    {
      "institution": "str | null",
      "degree": "str | null",
      "field": "str | null",
      "end_year": "int | null"
    }
  ],
  "provenance": [
    {
      "field": "str | null",
      "source": "str | null",
      "method": "str | null"
    }
  ],
  "overall_confidence": "float"
}
```

The final serialized output schema is runtime-configurable and validated through the `validator` layer.

## Merge Strategy

Conflict resolution is deterministic and modular:

- Preferred source priority is `Recruiter CSV > GitHub > Unknown > Missing`
- Scalar fields choose the first non-empty value from the highest-priority candidate
- `emails` and `phones` are deduplicated while preserving order
- `skills` are deduplicated and then sorted case-insensitively
- `experience` and `education` entries are matched by compatible anchor fields and merged without overwriting higher-priority data
- `links` are deduplicated by URL and type compatibility
- existing provenance entries are preserved and merged without duplication

Important current behavior:

- The merge engine can honor source priority when candidate provenance exists
- The current parsers do not attach per-field provenance
- As a result, many fields in the default sample flow are treated as `Unknown` for provenance and confidence purposes
- When provenance is absent, merge order falls back to input order among equally ranked records

## Confidence Strategy

Confidence is deterministic and field-based:

- `Recruiter CSV`: `0.95`
- `GitHub`: `0.80`
- `Unknown`: `0.50`
- `Missing`: `0.00`

Implementation details:

- each tracked field receives a score based on its best available provenance source
- empty values always receive `0.00`
- overall confidence is the arithmetic mean of tracked field scores, rounded to four decimals

Because the current sample inputs do not inject explicit field-level provenance, non-empty fields in the sample output typically score `0.50`.

## Provenance Tracking

The provenance layer emits final field-level records with:

- `field`
- `source`
- `method`

Behavior:

- if explicit provenance exists, the engine emits ordered merged provenance entries by source priority
- if the field is empty, it emits `source = "Missing"` and `method = "missing"`
- if the field is populated but explicit provenance is unavailable, it emits `source = "Unknown"` and `method = "merged"`

This keeps provenance deterministic and prevents silent loss of lineage information, while also making current limitations visible.

## Runtime Configuration

Runtime config is JSON-based and supports:

- `projection.select_fields` or `projection.fields`
- `projection.rename_fields`
- `projection.include_confidence`
- `projection.include_provenance`
- `projection.missing_value_policy`
- `projection.normalization`
- top-level inline `schema`
- top-level `schema_path`

Supported missing value policies:

- `null`: include the field with a `null` value
- `omit`: drop the field from the output
- `error`: fail projection immediately

Projection-time normalization is output-focused. It controls whether projected string values are whitespace-normalized during serialization. It does not mutate the internal `Candidate` model.

Example config variants are provided in `config/`.

## Sample Input

Sample recruiter CSV:

```csv
name,email,phone,current_company,title
Tanmay Sharma,tanmay.sharma@gmail.com,9876543210,Eightfold AI,Backend Engineer
```

Sample GitHub JSON:

```json
{
  "login": "tanmay-sharma",
  "name": "Tanmay S.",
  "bio": "Senior   Backend Engineer building scalable data platforms",
  "languages": ["python3", "js"],
  "email": "tanmay.sharma@gmail.com",
  "location": " Bengaluru , Karnataka , India ",
  "html_url": "https://github.com/tanmay-sharma"
}
```

Full samples are available in [data/recruiter.csv](data/recruiter.csv) and [data/github.json](data/github.json).

## Sample Output

Running the default config generates [output/result.json](output/result.json), which looks like:

```json
{
  "full_name": "Tanmay Sharma",
  "headline": "Senior Backend Engineer building scalable data platforms",
  "primary_email": "tanmay.sharma@gmail.com",
  "primary_phone": "+919876543210",
  "location": "Bengaluru, Karnataka, India",
  "skills": ["Go", "JavaScript", "Python", "SQL"],
  "links": [
    {
      "type": "github",
      "url": "https://github.com/tanmay-sharma"
    }
  ],
  "confidence": {
    "overall": 0.3636,
    "fields": {
      "full_name": 0.5,
      "emails": 0.5,
      "phones": 0.5
    }
  },
  "provenance": [
    {
      "field": "full_name",
      "source": "Unknown",
      "method": "merged"
    }
  ]
}
```

The full output file includes experience, education, and complete confidence and provenance payloads.

## Installation

1. Create a Python 3.11+ virtual environment.
2. Activate the environment.
3. Install dependencies:

```bash
pip install -r requirements.txt
```

The project uses only the Python standard library at runtime. `pytest` is included for testing.

## Running the CLI

Run the pipeline end to end:

```bash
python main.py --inputs data/recruiter.csv data/github.json --config config/default.json --output output/result.json
```

Expected result:

- the CLI prints a success message
- the pipeline writes `output/result.json`
- malformed or unsupported inputs are reported as meaningful warnings or errors

## Running Tests

Execute the test suite with:

```bash
python -m pytest
```

The repository includes:

- parser tests
- normalizer tests
- merge and confidence tests
- provenance, projection, and validator tests
- pipeline integration tests

## Assumptions

- all provided input files belong to the same real-world candidate
- a recruiter CSV may contain multiple rows, but the current pipeline merges all parsed candidates into one canonical output
- file type detection is based on file extension, not content sniffing
- runtime output shape is driven by the provided config and schema
- source-specific provenance is only as rich as the upstream candidate records provide

## Edge Cases Handled

- empty CLI input list
- unsupported input file extensions
- malformed JSON and unreadable files
- recruiter CSV files with missing columns
- empty rows in recruiter CSV files
- invalid emails being dropped during normalization
- invalid phone numbers being dropped during normalization
- duplicate emails, phones, skills, and links
- missing projected values through `null`, `omit`, and `error` policies
- schema mismatches before output is written

## Future Improvements

- attach explicit field-level provenance during parsing so confidence and merge priority can reflect true source origin
- add batch mode that outputs one canonical candidate per identity group instead of always merging into a single record
- extend parser support to LinkedIn exports, ATS payloads, and resume documents
- add richer date parsing and international phone handling
- support external schema files as first-class examples
- add CI, linting, coverage reporting, and packaging metadata
