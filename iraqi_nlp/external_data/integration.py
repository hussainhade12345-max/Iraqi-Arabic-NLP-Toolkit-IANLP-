"""Resumable, chunk-oriented local-file processing and import profile reports."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Mapping, Optional

from .adapters import AcquisitionError, map_to_staging_record
from .licensing import apply_record_policy
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


def _same_path(first: Path, second: Path) -> bool:
    try:
        return first.resolve(strict=False) == second.resolve(strict=False)
    except OSError:
        return os.path.abspath(first) == os.path.abspath(second)


def profile_local_file(input_path: Path | str, *, dataset_id: str, source_url: str,
                       source_type: str, revision: str, dataset_license: Mapping[str, Any],
                       chunk_size: int = 1000, checkpoint_path: Optional[Path | str] = None,
                       resume: bool = False, interrupted_after: Optional[int] = None):
    """Profile a local file dry-run; checkpoints store sufficient aggregate state.

    Checkpoints can contain token strings and dialect values needed to reproduce
    unique counts. Treat them as sensitive staging artifacts and protect access.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    path = Path(input_path)
    fingerprint = file_fingerprint(path)
    checkpoint = Path(checkpoint_path) if checkpoint_path else None
    if checkpoint is not None and _same_path(path, checkpoint):
        raise ResumeError("checkpoint path must not resolve to the input file")
    config = {"chunk_size": chunk_size, "schema_version": "1.0.0", "policy": "permission_matrix_quarantine_unless_cleared"}
    skip = 0
    profiler = DatasetProfiler()
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
        if skip < 0:
            raise ResumeError("checkpoint record count is invalid")
        try:
            profiler.restore_state(saved["profiler_state"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ResumeError("checkpoint profiler state is invalid") from exc
    report = ImportReport(
        source_id=dataset_id, mode="dry-run", status="profiling_local_file",
        source_revision=revision, provenance={"source_url": source_url, "source_type": source_type,
        "input_file": str(path), "input_sha256": fingerprint},
        licensing_status=str(dataset_license.get("status", "unknown")),
        processing_configuration=config,
    )
    processed = 0
    try:
        for _, source_record in iter_local_records(path, chunk_size=chunk_size):
            if processed < skip:
                processed += 1
                continue
            record_id = str(source_record.get("id", source_record.get("record_id", processed)))
            staged = map_to_staging_record(source_record, dataset_id=dataset_id, source_url=source_url,
                source_type=source_type, revision=revision, split_or_file=path.name,
                source_record_id=record_id, dataset_license=dataset_license,
                retrieved_at_utc=datetime.now(timezone.utc).isoformat())
            staged = apply_record_policy(staged)
            try:
                validate_staging_record(staged)
                canonical_valid = True
            except (ValueError, TypeError):
                canonical_valid = False
            profiler.add(source_record, canonical_valid=canonical_valid)
            report.source_records_discovered += 1
            report.quarantined_records += int(staged["disposition"] == "quarantine")
            if not staged["raw_text"].strip():
                report.rejected_records.append({"record_id": staged["record_id"], "reason": "missing_or_empty_text"})
            processed += 1
            if checkpoint is not None and processed % chunk_size == 0:
                _atomic_checkpoint(checkpoint, {"dataset_id": dataset_id, "input_fingerprint": fingerprint,
                    "configuration": config, "records_processed": processed, "profiler_state": profiler.to_state()})
            if interrupted_after is not None and processed - skip >= interrupted_after:
                if checkpoint is not None:
                    _atomic_checkpoint(checkpoint, {"dataset_id": dataset_id, "input_fingerprint": fingerprint,
                        "configuration": config, "records_processed": processed, "profiler_state": profiler.to_state()})
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
    report.warnings.extend(["Dry-run profile only; no records were accepted or written.",
        "Dialect and region values are source metadata only; no speaker attributes were inferred.",
        "Code-switching is a script-presence heuristic, not validated language identification."])
    report.records_accepted = 0
    report.records_downloaded = 0
    if checkpoint is not None:
        _atomic_checkpoint(checkpoint, {"dataset_id": dataset_id, "input_fingerprint": fingerprint,
            "configuration": config, "records_processed": processed, "profiler_state": profiler.to_state()})
    return report, report.profiling
