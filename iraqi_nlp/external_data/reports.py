"""Machine-readable and human-readable external import reports."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


class ReportOutputError(FileExistsError):
    """Raised if report output would overwrite an existing file."""


@dataclass
class ImportReport:
    source_id: str
    mode: str = "dry-run"
    status: str = "planned"
    source_records_discovered: int = 0
    records_downloaded: int = 0
    records_accepted: int = 0
    duplicates: int = 0
    rejected_records: List[Dict[str, Any]] = field(default_factory=list)
    quarantined_records: int = 0
    license_status: str = "not_verified_no_download"
    output_files: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    generated_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def render_markdown(report: ImportReport) -> str:
    data = report.to_dict()
    lines = ["# External data import report", "", "- Source: `{}`".format(report.source_id),
             "- Mode: `{}`".format(report.mode), "- Status: `{}`".format(report.status),
             "- Generated (UTC): `{}`".format(report.generated_at_utc), "",
             "## Counts", "", "| Measure | Count |", "|---|---:|",
             "| Source records discovered | {} |".format(report.source_records_discovered),
             "| Records downloaded | {} |".format(report.records_downloaded),
             "| Records accepted | {} |".format(report.records_accepted),
             "| Duplicates | {} |".format(report.duplicates),
             "| Quarantined | {} |".format(report.quarantined_records),
             "| Rejected | {} |".format(len(report.rejected_records)), "",
             "## Licensing", "", "Status: `{}`".format(report.license_status), "",
             "## Output files", ""]
    lines.extend(["- `{}`".format(path) for path in report.output_files] or ["- None"])
    lines.extend(["", "## Rejected records", ""])
    lines.extend(["- `{}` — {}".format(item.get("record_id", "unknown"), item.get("reason", "unspecified")) for item in report.rejected_records] or ["- None"])
    lines.extend(["", "## Warnings", ""])
    lines.extend(["- {}".format(item) for item in report.warnings] or ["- None"])
    lines.extend(["", "## Errors", ""])
    lines.extend(["- {}".format(item) for item in report.errors] or ["- None"])
    lines.append("")
    return "\n".join(lines)


def _preflight(paths: Tuple[Path, Path]) -> None:
    for path in paths:
        if path.exists():
            raise ReportOutputError("refusing to overwrite existing report: {}".format(path))


def write_reports(report: ImportReport, prefix: Path | str) -> Tuple[Path, Path]:
    """Write JSON and Markdown reports without replacing existing paths."""
    base = Path(prefix)
    base.parent.mkdir(parents=True, exist_ok=True)
    json_path = Path(str(base) + ".json")
    markdown_path = Path(str(base) + ".md")
    _preflight((json_path, markdown_path))
    payload = json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n"
    # O_EXCL makes the no-overwrite guarantee hold even if a file appears after preflight.
    created: List[Path] = []
    try:
        for path, content in ((json_path, payload), (markdown_path, render_markdown(report))):
            descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            created.append(path)
            with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
                handle.write(content)
    except OSError as exc:
        # Do not remove any report output: deletion is intentionally avoided.
        raise ReportOutputError("could not create reports without overwrite: {}".format(exc)) from exc
    return json_path, markdown_path
