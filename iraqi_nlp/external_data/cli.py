"""External-data dry-run CLI. Remote downloads remain disabled by policy."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

from .integration import ResumeError, profile_local_file
from .registry import RegistryError, load_registry
from .reports import ImportReport, ReportOutputError, write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Profile approved local fixtures and plan registered sources; no external downloads are enabled.")
    parser.add_argument("--source", help="Registered dataset ID; omit to list sources only.")
    parser.add_argument("--registry", type=Path, help="Optional path to source registry JSON.")
    parser.add_argument("--input", type=Path, help="Local fixture/source file to profile. Network access is not used.")
    parser.add_argument("--revision", help="Pinned source revision for provenance in the report (required with --input).")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--checkpoint", type=Path, help="Optional local processing checkpoint for interrupted-file resumption.")
    parser.add_argument("--resume", action="store_true", help="Resume from a matching checkpoint.")
    parser.add_argument("--report-prefix", type=Path, default=Path("staging/external_import_reports/import-report"))
    parser.add_argument("--download", action="store_true", help="Always refused; real external downloads require separate authorization.")
    parser.add_argument("--approve-downloads", action="store_true", help="Reserved and not sufficient to enable external downloads.")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    if args.download:
        print("External dataset downloads are disabled; no network request was made.", file=sys.stderr)
        return 2
    if args.chunk_size < 1:
        print("--chunk-size must be positive", file=sys.stderr)
        return 2
    try:
        registry = load_registry(args.registry)
    except RegistryError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    sources = registry["sources"]
    source = None
    if args.source:
        source = next((item for item in sources if item["dataset_id"] == args.source), None)
        if source is None:
            print("Source is not in the registered source list: {}".format(args.source), file=sys.stderr)
            return 2
    if args.input:
        if source is None:
            print("--source must name a registered source when --input is used", file=sys.stderr)
            return 2
        revision = args.revision or source.get("revision", {}).get("value")
        if not revision:
            print("A revision is required for input provenance; no source records were fetched.", file=sys.stderr)
            return 2
        try:
            report, _ = profile_local_file(
                args.input, dataset_id=source["dataset_id"], source_url=source["url"],
                source_type=source["source_type"], revision=revision,
                dataset_license=source["dataset_license"], chunk_size=args.chunk_size,
                checkpoint_path=args.checkpoint, resume=args.resume,
            )
        except (ResumeError, OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2
    else:
        if source is None:
            print("Registered sources: " + ", ".join(item["dataset_id"] for item in sources))
            return 0
        report = ImportReport(
            source_id=source["dataset_id"], status="planned_no_download", mode="dry-run",
            source_revision=source.get("revision", {}).get("value"),
            provenance={"source_url": source["url"], "source_type": source["source_type"]},
            licensing_status=source["dataset_license"]["status"],
            warnings=["No records were read or downloaded.", "Record-level licensing and privacy review is required."],
        )
    try:
        json_path, markdown_path = write_reports(report, args.report_prefix)
    except ReportOutputError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print("Report created: {} and {}".format(json_path, markdown_path))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
