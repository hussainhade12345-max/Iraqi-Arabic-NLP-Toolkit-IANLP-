"""Local staging helpers and acquisition report integration."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple

from .adapters import apply_record_policy, detect_duplicates, map_to_staging_record
from .reports import ImportReport
from .schema import validate_staging_record


def process_records(
    records: Iterable[Mapping[str, Any]], *, dataset_id: str, source_url: str,
    source_type: str, revision: str, split_or_file: str,
    dataset_license: Mapping[str, Any], retrieved_at_utc: Optional[str] = None,
    text_field: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], ImportReport, Dict[str, Any]]:
    """Map in-memory/local fixture records, apply quarantine policy, and report duplicates.

    This is pure processing: it does not fetch files, write record data, or mutate
    the source iterable. Outputs preserve every source field.
    """
    retrieved = retrieved_at_utc or datetime.now(timezone.utc).isoformat()
    staged: List[Dict[str, Any]] = []
    report = ImportReport(source_id=dataset_id, status="processed_local_or_mock", mode="dry-run")
    for index, original in enumerate(records):
        report.source_records_discovered += 1
        source_id = str(original.get("id", original.get("record_id", index)))
        record = map_to_staging_record(
            original, dataset_id=dataset_id, source_url=source_url, source_type=source_type,
            revision=revision, split_or_file=split_or_file, source_record_id=source_id,
            dataset_license=dataset_license, retrieved_at_utc=retrieved, text_field=text_field,
        )
        record = apply_record_policy(record)
        validate_staging_record(record)
        staged.append(record)
        report.records_downloaded += 0
        report.quarantined_records += int(record["disposition"] == "quarantine")
        if record["disposition"] == "restricted":
            report.warnings.append("Restricted records are segregated; record {} is not accepted.".format(record["record_id"]))
        if not record["raw_text"].strip():
            report.rejected_records.append({"record_id": record["record_id"], "reason": "missing_or_empty_text"})
    duplicates = detect_duplicates(staged)
    report.duplicates = duplicates["duplicate_group_count"]
    report.license_status = str(dataset_license.get("status", "unknown"))
    report.warnings.append("Processing was limited to supplied local/mock records; no network request was made.")
    return staged, report, duplicates
