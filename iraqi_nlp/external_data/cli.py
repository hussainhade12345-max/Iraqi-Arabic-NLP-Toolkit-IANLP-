"""Dry-run-first CLI scaffold; external network acquisition is not implemented."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .registry import RegistryError, load_registry
from .reports import ImportReport, ReportOutputError, write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Plan IANLP external data imports safely (no network access in Stage 1).")
    parser.add_argument("--source", help="Registered dataset ID; omit to validate and report all sources.")
    parser.add_argument("--registry", type=Path, help="Optional path to a source registry JSON file.")
    parser.add_argument("--report-prefix", type=Path, default=Path("staging/external_import_reports/import-report"),
                        help="Report filename prefix. JSON and Markdown files are created; existing files are never overwritten.")
    parser.add_argument("--download", action="store_true", help="Reserved for later stages; Stage 1 refuses all downloads.")
    parser.add_argument("--approve-downloads", action="store_true", help="Explicit approval required by future download implementation.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.download:
        print("External downloads are not implemented or enabled in Stage 1; no network request was made.", file=sys.stderr)
        return 2
    try:
        registry = load_registry(args.registry)
    except RegistryError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    sources = registry["sources"]
    if args.source:
        sources = [item for item in sources if item["dataset_id"] == args.source]
        if not sources:
            print("Source is not in the registered source list: {}".format(args.source), file=sys.stderr)
            return 2
    reports = []
    for source in sources:
        report = ImportReport(
            source_id=source["dataset_id"],
            mode="dry-run",
            status="planned_no_download",
            license_status=source["dataset_license"]["status"],
            warnings=[
                "Dry-run only: no records were fetched or changed.",
                "Record-level licensing and privacy must be reviewed before acceptance.",
                "Existing corpus and lexicon files are not import destinations.",
            ],
        )
        reports.append(report)
    # Stage 1 permits one source per report prefix, avoiding report-name collisions.
    if len(reports) > 1:
        print("Specify --source to emit a report for one source; no report was written.", file=sys.stderr)
        return 2
    try:
        json_path, markdown_path = write_reports(reports[0], args.report_prefix)
    except ReportOutputError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("Dry-run report created: {} and {}".format(json_path, markdown_path))
    print("No external records were downloaded; Hugging Face publishing is not available.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
