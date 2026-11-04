"""Resumable, chunk-oriented local-file processing and import profile reports."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .adapters import AcquisitionError, apply_record_policy, map_to_staging_record
from .profiling import DatasetProfiler
from .reports import ImportReport
from .schema import validate_staging_record
from .streaming import file_fingerprint, iter_local_records


class ResumeError(ValueError):
    """Checkpoint does not match the selected source/configuration."""


def _atomic_checkpoint(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp-{}".format(os.getpid()))
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, sort_keys=True)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(str(tmp), str(path))


def profile_local_file(
    input_path: Path | str, *, dataset_id: str, source_url: str, source_type: str,
    revision: str, dataset_license: Mapping[str, Any], chunk_size: int = 1000,
    checkpoint_path: Optional[Path | str] = None, resume: bool = False,
    interrupted_after: Optional[int] = None,
) -> tuple[ImportReport, Dict[str, Any]]:
    """Profile a local file in dry-run chunks, writing only resumable metadata checkpoints.

    No staged records or source data are written. ``interrupted_after`` exists for
    deterministic integration tests and simulates interruption after N processed rows.
    """
    path = Path(input_path)
    fingerprint = file_fingerprint(path)
    checkpoint = Path(checkpoint_path) if checkpoint_path else None
    config = {"chunk_size": chunk_size, "schema_version": "1.0.0", "policy": "quarantine_unless_review_cleared"}
    skip = 0
    if resume:
        if checkpoint is None or not checkpoint.is_file():
            raise ResumeError("resume requested but checkpoint is unavailable")
        try:
            saved = json.loads(checkpoint.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ResumeError("checkpoint is invalid") from exc
        if saved.get("input_fingerprint") != fingerprint or saved.get("dataset_id") != dataset_id or saved.get("configuration") != config:
            raise ResumeError("checkpoint source or processing configuration does not match")
        skip = int(saved.get("records_processed", 0))
    profiler = DatasetProfiler()
    report = ImportReport(
        source_id=dataset_id, mode="dry-run", status="profiling_local_file",
        source_revision=revision, provenance={"source_url": source_url, "source_type": source_type, "input_file": str(path), "input_sha256": fingerprint},
        licensing_status=str(dataset_license.get("status", "unknown")),
        processing_configuration=config,
    )
    processed = 0
    try:
        for _, source_record in iter_local_records(path, chunk_size=chunk_size):
            if processed < skip:
                processed += 1
                continue
            profiler.add(source_record)
            record_id = str(source_record.get("id", source_record.get("record_id", processed)))
            staged = map_to_staging_record(
                source_record, dataset_id=dataset_id, source_url=source_url, source_type=source_type,
                revision=revision, split_or_file=path.name, source_record_id=record_id,
                dataset_license=dataset_license, retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
            )
            staged = apply_record_policy(staged)
            validate_staging_record(staged)
            report.source_records_discovered += 1
            report.quarantined_records += int(staged["disposition"] == "quarantine")
            report.rejected_records += ([{"record_id": staged["record_id"], "reason": "missing_or_empty_text"}] if not staged["raw_text"].strip() else [])
            processed += 1
            if checkpoint is not None and processed % chunk_size == 0:
                _atomic_checkpoint(checkpoint, {"dataset_id": dataset_id, "input_fingerprint": fingerprint, "configuration": config, "records_processed": processed})
            if interrupted_after is not None and processed - skip >= interrupted_after:
                if checkpoint is not None:
                    _atomic_checkpoint(checkpoint, {"dataset_id": dataset_id, "input_fingerprint": fingerprint, "configuration": config, "records_processed": processed})
                report.status = "interrupted_checkpointed"
                report.profiling = profiler.to_dict()
                return report, report.profiling
    except (OSError, UnicodeError, AcquisitionError) as exc:
        report.errors.append("input processing failed: {}".format(type(exc).__name__))
        report.status = "failed"
        report.profiling = profiler.to_dict()
        return report, report.profiling
    report.status = "profiled_local_file"
    report.profiling = profiler.to_dict()
    report.warnings.extend([
        "Dry-run profile only; no records were accepted or written.",
        "Dialect and region values are source metadata only; no speaker attributes were inferred.",
        "Code-switching is a script-presence heuristic, not validated language identification.",
    ])
    report.records_accepted = 0
    report.records_downloaded = 0
    if checkpoint is not None:
        _atomic_checkpoint(checkpoint, {"dataset_id": dataset_id, "input_fingerprint": fingerprint, "configuration": config, "records_processed": processed})
    return report, report.profiling
