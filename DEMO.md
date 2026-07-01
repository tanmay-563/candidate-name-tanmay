# Demo Guide

## Goal

Use this walkthrough to explain the project in about two minutes.

## What To Open

- `README.md`
- `ARCHITECTURE.md`
- `main.py`
- `src/candidate_data_transformer/pipeline.py`
- `config/default.json`
- `data/recruiter.csv`
- `data/github.json`
- `output/result.json`

## Commands To Run

Install test dependency:

```bash
pip install -r requirements.txt
```

Run the default pipeline:

```bash
python main.py --inputs data/recruiter.csv data/github.json --config config/default.json --output output/result.json
```

Optionally run tests:

```bash
python -m pytest
```

## What To Explain

- The project is a staged ingestion pipeline, not a script with all logic in `main.py`.
- Each module has one responsibility: parsing, normalization, merge, provenance, confidence, projection, and validation.
- The CLI is intentionally thin and only coordinates inputs, config, and output writing.
- Runtime config changes the final JSON shape without changing the internal `Candidate` model.

## Which Edge Case To Demonstrate

Demonstrate invalid or missing projected values with `config/minimal.json`:

- remove the `phone` value from `data/recruiter.csv`
- run the CLI with `config/minimal.json`
- explain that the pipeline fails cleanly because `missing_value_policy` is `error` and the schema requires `primary_phone`

This shows validation and configuration-driven behavior clearly in a short time.

## Which Design Decision To Explain

Explain why the internal canonical model is separated from the final output schema:

- normalization and merge operate on one stable `Candidate` structure
- projection adapts that structure for downstream consumers
- validation checks the projected contract at the edge

That separation keeps the pipeline easier to test, extend, and reason about.
