"""Local readers and pinned remote adapters for external dataset files.

Remote access is opt-in and adapters require an immutable commit/revision. The
module never modifies IANLP corpus or lexicon files and has no publishing code.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Dict, Iterable, Iterator, List, Mapping, Optional, Sequence, Tuple


class AcquisitionError(RuntimeError):
    """Raised when safe acquisition or decoding fails."""


class RevisionRequiredError(AcquisitionError):
    """Raised when an external source is not pinned to an immutable revision."""


@dataclass(frozen=True)
class RetryPolicy:
    attempts: int = 3
    timeout_seconds: float = 20.0
    backoff_seconds: float = 0.25
    max_bytes: int = 50 * 1024 * 1024

    def __post_init__(self) -> None:
        if self.attempts < 1 or self.attempts > 5:
            raise ValueError("attempts must be between 1 and 5")
        if self.timeout_seconds <= 0 or self.timeout_seconds > 120:
            raise ValueError("timeout_seconds must be in (0, 120]")
        if self.backoff_seconds < 0 or self.backoff_seconds > 10:
            raise ValueError("backoff_seconds must be between 0 and 10")
        if self.max_bytes <= 0:
            raise ValueError("max_bytes must be positive")


def _safe_relative_path(path: str) -> str:
    candidate = PurePosixPath(path)
    if candidate.is_absolute() or not candidate.parts or any(part in ("", ".", "..") for part in candidate.parts):
        raise AcquisitionError("unsafe source file path")
    return str(candidate)


def _decode_records(payload: bytes, fmt: str) -> List[Dict[str, Any]]:
    try:
        text = payload.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AcquisitionError("source file is not valid UTF-8") from exc
    fmt = fmt.lower().lstrip(".")
    try:
        if fmt == "csv":
            return [dict(row) for row in csv.DictReader(io.StringIO(text))]
        if fmt == "jsonl":
            rows = []
            for line_number, line in enumerate(text.splitlines(), 1):
                if line.strip():
                    value = json.loads(line)
                    if not isinstance(value, dict):
                        raise AcquisitionError("JSONL line {} must be an object".format(line_number))
                    rows.append(value)
            return rows
        if fmt == "json":
            value = json.loads(text)
            if isinstance(value, list):
                rows = value
            elif isinstance(value, dict):
                rows = value.get("data", value.get("records", value.get("samples", [value])))
            else:
                raise AcquisitionError("JSON root must be object or array")
            if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
                raise AcquisitionError("JSON record collection must contain objects")
            return rows
        if fmt == "parquet":
            try:
                import pandas as pd
            except ImportError as exc:  # pragma: no cover - package already has pandas
                raise AcquisitionError("Parquet requires optional pandas and pyarrow/fastparquet") from exc
            try:
                frame = pd.read_parquet(io.BytesIO(payload))
            except (ImportError, ValueError, OSError) as exc:
                raise AcquisitionError("Parquet support needs pyarrow or fastparquet") from exc
            return frame.to_dict(orient="records")
    except (json.JSONDecodeError, csv.Error) as exc:
        raise AcquisitionError("invalid {} data: {}".format(fmt, exc)) from exc
    raise AcquisitionError("unsupported file format: {}".format(fmt))


def read_local_file(path: Path | str, fmt: Optional[str] = None) -> List[Dict[str, Any]]:
    """Read CSV/JSON/JSONL, or optional Parquet, from a local fixture/file."""
    file_path = Path(path)
    if not file_path.is_file():
        raise AcquisitionError("local source file does not exist: {}".format(file_path))
    return _decode_records(file_path.read_bytes(), fmt or file_path.suffix.lstrip("."))


Fetcher = Callable[[str, RetryPolicy], bytes]


def http_fetch(url: str, policy: RetryPolicy) -> bytes:
    """Fetch one file with bounded retries, timeout, and response size limit."""
    last_error: Optional[BaseException] = None
    for attempt in range(policy.attempts):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": "IANLP-external-data/1.0"})
            with urllib.request.urlopen(request, timeout=policy.timeout_seconds) as response:
                body = response.read(policy.max_bytes + 1)
            if len(body) > policy.max_bytes:
                raise AcquisitionError("download exceeds configured max_bytes")
            return body
        except (urllib.error.URLError, TimeoutError, OSError, AcquisitionError) as exc:
            last_error = exc
            if isinstance(exc, AcquisitionError) and "max_bytes" in str(exc):
                raise
            if attempt + 1 < policy.attempts:
                time.sleep(policy.backoff_seconds * (2 ** attempt))
    raise AcquisitionError("fetch failed after {} attempt(s): {}".format(policy.attempts, type(last_error).__name__)) from last_error


@dataclass
class PinnedFileAdapter:
    """Base behavior for fetching explicitly enumerated files at a pinned revision."""
    fetcher: Fetcher = http_fetch
    retry_policy: RetryPolicy = RetryPolicy()
    cache_dir: Optional[Path] = None

    def _get_payload(self, url: str, cache_key: str) -> bytes:
        if self.cache_dir is None:
            return self.fetcher(url, self.retry_policy)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        cache_path = self.cache_dir / (hashlib.sha256(cache_key.encode("utf-8")).hexdigest() + ".blob")
        if cache_path.exists():
            payload = cache_path.read_bytes()
            if len(payload) <= self.retry_policy.max_bytes:
                return payload
            raise AcquisitionError("cached source file exceeds max_bytes")
        payload = self.fetcher(url, self.retry_policy)
        # Atomic exclusive creation; a completed cache entry can resume a later run.
        temp_path = cache_path.with_suffix(".tmp-{}".format(os.getpid()))
        with temp_path.open("xb") as handle:
            handle.write(payload)
        try:
            os.replace(str(temp_path), str(cache_path))
        except OSError:
            if not cache_path.exists():
                raise
            temp_path.unlink(missing_ok=True)
        return payload

    def read_files(self, files: Sequence[str], revision: str) -> Iterator[Tuple[str, List[Dict[str, Any]]]]:
        if not revision or revision.lower() in {"main", "master", "latest", "head"}:
            raise RevisionRequiredError("an immutable commit/revision is required; branch names are not accepted")
        for file_name in files:
            safe_path = _safe_relative_path(file_name)
            url = self.file_url(safe_path, revision)
            payload = self._get_payload(url, url)
            yield safe_path, _decode_records(payload, Path(safe_path).suffix.lstrip("."))

    def file_url(self, file_path: str, revision: str) -> str:
        raise NotImplementedError


@dataclass
class HuggingFaceAdapter(PinnedFileAdapter):
    """Read explicit dataset files from Hugging Face Hub at a pinned commit SHA."""
    dataset_id: str = ""

    def file_url(self, file_path: str, revision: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", revision):
            raise RevisionRequiredError("Hugging Face revision must be an immutable commit SHA")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", self.dataset_id):
            raise AcquisitionError("dataset_id must use owner/name form")
        encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in file_path.split("/"))
        return "https://huggingface.co/datasets/{}/resolve/{}/{}?download=true".format(self.dataset_id, revision, encoded_path)


@dataclass
class GitHubAdapter(PinnedFileAdapter):
    """Read explicit repository files from GitHub raw content at a pinned commit."""
    owner: str = ""
    repo: str = ""

    def file_url(self, file_path: str, revision: str) -> str:
        if not re.fullmatch(r"[0-9a-fA-F]{7,64}", revision):
            raise RevisionRequiredError("GitHub revision must be an immutable commit SHA")
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", self.owner) or not re.fullmatch(r"[A-Za-z0-9_.-]+", self.repo):
            raise AcquisitionError("owner and repo are required")
        encoded_path = "/".join(urllib.parse.quote(part, safe="") for part in file_path.split("/"))
        return "https://raw.githubusercontent.com/{}/{}/{}/{}".format(self.owner, self.repo, revision, encoded_path)


_ARABIC_TEXT_FIELDS = ("text", "raw_text", "sentence", "content", "tweet", "post", "word", "iraqi_term")
_LABEL_FIELDS = ("label", "labels", "label_primary", "dialect", "dialect_label", "sentiment", "intent")


def map_to_staging_record(
    record: Mapping[str, Any], *, dataset_id: str, source_url: str,
    source_type: str, revision: str, split_or_file: str,
    source_record_id: str, dataset_license: Mapping[str, Any], retrieved_at_utc: str,
    text_field: Optional[str] = None,
) -> Dict[str, Any]:
    """Preserve every source field and map known raw text/labels without inference."""
    original = dict(record)
    selected = text_field or next((key for key in _ARABIC_TEXT_FIELDS if isinstance(original.get(key), str)), None)
    raw_text = original.get(selected) if selected else None
    if not isinstance(raw_text, str):
        raw_text = ""
    labels = {key: original[key] for key in _LABEL_FIELDS if key in original}
    per_record_license = next((original[key] for key in ("license", "licence", "license_id") if key in original), None)
    evidence = []
    if per_record_license is not None:
        evidence.append({"field": "license", "value": per_record_license})
    dataset_license_value = dataset_license.get("spdx_id")
    license_status = "unknown"
    redistribution_allowed = None
    commercial_allowed = None
    attribution_required = None
    # Do not infer per-record clearance from dataset-level CC0; record-level rights
    # need explicit review, except where a reviewer supplies a cleared policy record.
    if isinstance(per_record_license, str) and per_record_license.strip():
        license_status = "needs_review"
    record_id = str(original.get("id", original.get("record_id", source_record_id)))
    privacy_flags = []
    if re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", raw_text):
        privacy_flags.append("email_like_text")
    if re.search(r"(?:\+?\d[\d ()-]{7,}\d)", raw_text):
        privacy_flags.append("phone_like_text")
    privacy_status = "needs_review" if privacy_flags else "not_assessed"
    return {
        "schema_version": "1.0.0",
        "record_id": "{}:{}".format(dataset_id, record_id),
        "raw_text": raw_text,
        "source": {
            "dataset_id": dataset_id, "source_url": source_url, "source_type": source_type,
            "revision": revision, "split_or_file": split_or_file,
            "source_record_id": source_record_id, "retrieved_at_utc": retrieved_at_utc,
        },
        "original_fields": original,
        "labels": labels,
        "licensing": {
            "dataset_license": dataset_license_value,
            "record_license": per_record_license,
            "license_evidence": evidence,
            "status": license_status,
            "commercial_use_allowed": commercial_allowed,
            "redistribution_allowed": redistribution_allowed,
            "attribution_required": attribution_required,
        },
        "privacy": {"status": privacy_status, "review_notes": privacy_flags},
        "disposition": "quarantine",
    }


def detect_duplicates(records: Iterable[Mapping[str, Any]]) -> Dict[str, Any]:
    """Report exact and whitespace/case-normalized text duplicates without dropping rows."""
    seen: Dict[str, List[str]] = {}
    exact_seen: Dict[str, List[str]] = {}
    duplicates: List[Dict[str, Any]] = []
    count = 0
    for record in records:
        count += 1
        text = record.get("raw_text", "")
        text = text if isinstance(text, str) else ""
        rid = str(record.get("record_id", "unknown"))
        exact = hashlib.sha256(text.encode("utf-8")).hexdigest()
        normalized = " ".join(text.split()).casefold()
        exact_seen.setdefault(exact, []).append(rid)
        seen.setdefault(normalized, []).append(rid)
    for key, ids in exact_seen.items():
        if len(ids) > 1:
            duplicates.append({"kind": "exact", "fingerprint": key, "record_ids": ids})
    exact_count = len(duplicates)
    for key, ids in seen.items():
        if len(ids) > 1:
            exact_ids = exact_seen.get(hashlib.sha256(next((r.get("raw_text", "").encode("utf-8") for r in records if str(r.get("record_id", "unknown")) == ids[0]), b"")).hexdigest(), [])
            if len(ids) > 1 and len(exact_ids) != len(ids):
                duplicates.append({"kind": "normalized", "fingerprint": hashlib.sha256(key.encode("utf-8")).hexdigest(), "record_ids": ids})
    return {"record_count": count, "duplicate_groups": duplicates, "duplicate_group_count": len(duplicates), "records_preserved": True}


def apply_record_policy(record: Dict[str, Any], *, reviewer_cleared: bool = False) -> Dict[str, Any]:
    """Conservative record policy. Only explicit reviewer clearance permits acceptance."""
    licensing = record.get("licensing", {})
    privacy = record.get("privacy", {})
    if reviewer_cleared and licensing.get("redistribution_allowed") is True and privacy.get("status") == "cleared":
        licensing["status"] = "cleared"
        record["disposition"] = "accepted"
    elif licensing.get("commercial_use_allowed") is False:
        record["disposition"] = "restricted"
    else:
        record["disposition"] = "quarantine"
    return record


def records_from_files(adapter: PinnedFileAdapter, files: Sequence[str], revision: str) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """Yield source file path and original source record; never writes dataset files."""
    for file_path, records in adapter.read_files(files, revision):
        for record in records:
            yield file_path, record
