"""Streaming HTTP CSV/JSONL reader for explicitly pinned external files."""

from __future__ import annotations

import csv
import io
import json
import urllib.request
from typing import Any, Dict, Iterator, Mapping

from .adapters import AcquisitionError, PinnedFileAdapter, RetryPolicy, RevisionRequiredError, _safe_relative_path


class _CappedReader:
    """File-like proxy enforcing a maximum number of bytes read."""
    def __init__(self, response: Any, maximum: int):
        self.response = response
        self.maximum = maximum
        self.count = 0

    def read(self, size: int = -1) -> bytes:
        remaining = self.maximum - self.count
        request_size = remaining + 1 if size < 0 else min(size, remaining + 1)
        data = self.response.read(request_size)
        self.count += len(data)
        if self.count > self.maximum:
            raise AcquisitionError("download exceeds configured max_bytes")
        return data

    def readable(self) -> bool:
        return True


def iter_remote_records(adapter: PinnedFileAdapter, file_path: str, revision: str) -> Iterator[Dict[str, Any]]:
    """Stream remote CSV/JSONL at a pinned revision; JSON remains size-bounded buffered."""
    if not revision or revision.lower() in {"main", "master", "latest", "head"}:
        raise RevisionRequiredError("an immutable revision is required")
    safe_path = _safe_relative_path(file_path)
    url = adapter.file_url(safe_path, revision)
    file_format = safe_path.rsplit(".", 1)[-1].lower()
    policy = adapter.retry_policy
    if file_format not in {"csv", "jsonl", "json"}:
        raise AcquisitionError("remote streaming currently supports CSV, JSONL, and bounded JSON only")
    last_error = None
    for attempt in range(policy.attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "IANLP-external-data/1.0"})
            response = urllib.request.urlopen(request, timeout=policy.timeout_seconds)
            break
        except Exception as exc:  # no response data has been consumed; retry only bounded opens
            last_error = exc
            if attempt + 1 == policy.attempts:
                raise AcquisitionError("remote stream open failed after bounded retries: {}".format(type(exc).__name__)) from exc
    else:  # pragma: no cover
        raise AcquisitionError("remote stream unavailable") from last_error

    with response:
        capped = _CappedReader(response, policy.max_bytes)
        if file_format == "csv":
            text = io.TextIOWrapper(io.BufferedReader(capped), encoding="utf-8-sig", newline="")
            try:
                for row in csv.DictReader(text):
                    yield dict(row)
            except (UnicodeError, csv.Error) as exc:
                raise AcquisitionError("invalid streamed CSV: {}".format(exc)) from exc
            return
        if file_format == "jsonl":
            text = io.TextIOWrapper(io.BufferedReader(capped), encoding="utf-8-sig")
            for line_number, line in enumerate(text, 1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise AcquisitionError("invalid streamed JSONL at line {}".format(line_number)) from exc
                if not isinstance(record, dict):
                    raise AcquisitionError("JSONL line {} must be an object".format(line_number))
                yield record
            return
        # Standard-library JSON has no incremental object-array parser. This path is
        # explicit and bounded by max_bytes; large datasets should use JSONL/CSV.
        payload = capped.read()
        try:
            value = json.loads(payload.decode("utf-8-sig"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AcquisitionError("invalid bounded JSON file") from exc
        if isinstance(value, dict):
            value = value.get("records", value.get("data", value.get("samples", [value])))
        if not isinstance(value, list) or any(not isinstance(item, dict) for item in value):
            raise AcquisitionError("JSON records must be an array of objects")
        yield from value
