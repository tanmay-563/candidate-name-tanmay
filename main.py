"""Command-line entry point for the integrated candidate data transformer."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path


def _bootstrap_source_path() -> Path:
    """Ensure the local ``src`` directory is importable during early development."""

    project_root = Path(__file__).resolve().parent
    source_directory = project_root / "src"

    if str(source_directory) not in sys.path:
        sys.path.insert(0, str(source_directory))

    return project_root


def _build_argument_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser for the transformation pipeline."""

    argument_parser = argparse.ArgumentParser(
        description="Run the Multi-Source Candidate Data Transformer pipeline.",
    )
    argument_parser.add_argument(
        "--inputs",
        nargs="+",
        required=True,
        help="One or more input files to transform.",
    )
    argument_parser.add_argument(
        "--config",
        required=True,
        help="Path to the runtime pipeline configuration JSON file.",
    )
    argument_parser.add_argument(
        "--output",
        required=True,
        help="Path where the final output JSON should be written.",
    )
    return argument_parser


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments, run the pipeline, and write the output JSON."""

    project_root = _bootstrap_source_path()
    argument_parser = _build_argument_parser()
    parsed_arguments = argument_parser.parse_args(argv)

    from candidate_data_transformer.app import build_application
    from candidate_data_transformer.pipeline_exceptions import PipelineError

    application = build_application(project_root=project_root)
    application.bootstrap()

    input_paths = [Path(raw_path) for raw_path in parsed_arguments.inputs]
    config_path = Path(parsed_arguments.config)
    output_path = Path(parsed_arguments.output)

    try:
        transformation_result = application.pipeline.transform(
            inputs=input_paths,
            config_path=config_path,
        )
    except PipelineError as error:
        print(f"Pipeline error: {error}", file=sys.stderr)
        return 1
    except Exception as error:
        print(f"Unexpected error: {error}", file=sys.stderr)
        return 1

    if transformation_result.projected_payload is None:
        print("Pipeline error: no output payload was produced.", file=sys.stderr)
        return 1

    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(
                transformation_result.projected_payload,
                indent=2,
                ensure_ascii=True,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError as error:
        print(f"Output error: unable to write '{output_path}': {error}", file=sys.stderr)
        return 1

    for warning in transformation_result.validation_issues:
        print(
            f"Warning: {warning.code}: {warning.message}",
            file=sys.stderr,
        )

    print(f"Success: wrote transformed output to {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
