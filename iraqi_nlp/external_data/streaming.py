"""Streaming record readers for external data files."""

from __future__ import annotations

import csv
import hashlib
import io
import json
from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional, Tuple

from .adapters import AcquisitionError, _decode_records


def iter_local_records(path: Path | str, fmt: Optional[str] = None, chunk_size: int = 1000) -> Iterator[Tuple[int, Dict[str, Any]]]:
    """Yield ``(zero_based_index, record)`` with bounded record buffering where possible.

    CSV and JSONL are streamed line/row-wise. JSON arrays use the standard JSON
    parser and therefore require the parsed JSON document in memory. Parquet is
    read in pandas batches only when a compatible optional engine is installed.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be positive")
    file_path = Path(path)
    if not file_path.is_file():
        raise AcquisitionError("local source file does not exist: {}".format(file_path))
    file_format = (fmt or file_path.suffix.lstrip(".")).lower()
    if file_format == "csv":
        with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            for index, row in enumerate(reader):
                yield index, dict(row)
        return
    if file_format == "jsonl":
        with file_path.open("r", encoding="utf-8-sig") as handle:
            index = 0
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AcquisitionError("invalid JSONL at line {}: {}".format(line_number, exc)) from exc
                if not isinstance(record, dict):
                    raise AcquisitionError("JSONL line {} must contain an object".format(line_number))
                yield index, record
                index += 1
        return
    if file_format == "json":
        # JSON parsing is not streaming in the Python standard library. Keep this
        # explicit rather than implying bounded memory for a single JSON array.
        try:
            value = json.loads(file_path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as exc:
            raise AcquisitionError("invalid JSON source: {}".format(exc)) from exc
        if isinstance(value, dict):
            value = value.get("data", value.get("records", value.get("samples", [value])))
        if not isinstance(value, list):
            raise AcquisitionError("JSON source must contain an array of records")
        for index, record in enumerate(value):
            if not isinstance(record, dict):
                raise AcquisitionError("JSON record {} must be an object".format(index))
            yield index, record
        return
    if file_format == "parquet":
        try:
            import pandas as pd
            import pyarrow.parquet as pq
        except ImportError as exc:
            raise AcquisitionError("streaming Parquet requires optional pyarrow") from exc
        parquet = pq.ParquetFile(str(file_path))
        index = 0
        for batch in parquet.iter_batches(batch_size=chunk_size):
            for record in batch.to_pylist():
                yield index, record
                index += 1
        return
    raise AcquisitionError("unsupported file format: {}".format(file_format))


def file_fingerprint(path: Path | str, block_size: int = 1024 * 1024) -> str:
    """Compute a stable SHA-256 input fingerprint using bounded memory."""
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        while True:
            block = handle.read(block_size)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()
