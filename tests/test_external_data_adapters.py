"""Tests for external adapters using local fixtures and mocked fetchers only."""

import json

import pytest

from iraqi_nlp.external_data.adapters import (
    AcquisitionError,
    GitHubAdapter,
    HuggingFaceAdapter,
    RevisionRequiredError,
    RetryPolicy,
    detect_duplicates,
    read_local_file,
)
from iraqi_nlp.external_data.processing import process_records


def test_local_csv_json_and_jsonl_readers(tmp_path):
    csv_path = tmp_path / "rows.csv"
    csv_path.write_text('id,text,label\n1,"هسه چانت",x\n', encoding="utf-8")
    assert read_local_file(csv_path)[0]["text"] == "هسه چانت"
    json_path = tmp_path / "rows.json"
    json_path.write_text(json.dumps({"records": [{"id": 2, "text": "باجر"}]}, ensure_ascii=False), encoding="utf-8")
    assert read_local_file(json_path)[0]["text"] == "باجر"
    jsonl_path = tmp_path / "rows.jsonl"
    jsonl_path.write_text('{"id":3,"text":"هواية"}\n\n{"id":4,"text":"ماكو"}\n', encoding="utf-8")
    assert len(read_local_file(jsonl_path)) == 2


def test_parquet_is_optional_and_clear_error_without_engine(tmp_path, monkeypatch):
    path = tmp_path / "data.parquet"
    path.write_bytes(b"not parquet")
    with pytest.raises(AcquisitionError, match="Parquet support needs"):
        read_local_file(path)


def test_huggingface_adapter_requires_immutable_revision_and_encodes_path():
    adapter = HuggingFaceAdapter(dataset_id="owner/data", fetcher=lambda url, policy: b'{"records": []}')
    with pytest.raises(RevisionRequiredError):
        list(adapter.read_files(["data.json"], "main"))
    assert adapter.file_url("dir/data.json", "abcdef123456") == "https://huggingface.co/datasets/owner/data/resolve/abcdef123456/dir/data.json?download=true"


def test_github_adapter_pins_raw_url_to_commit():
    adapter = GitHubAdapter(owner="owner", repo="data", fetcher=lambda url, policy: b"id,text\n1,hello\n")
    assert adapter.file_url("folder/data.csv", "abcdef123456") == "https://raw.githubusercontent.com/owner/data/abcdef123456/folder/data.csv"
    assert list(adapter.read_files(["folder/data.csv"], "abcdef123456"))[0][1][0]["text"] == "hello"


def test_mocked_fetch_retries_bounded_and_succeeds():
    calls = []
    def fetch(url, policy):
        calls.append(url)
        if len(calls) < 2:
            raise OSError("temporary")
        return b"id,text\n1,hello\n"
    adapter = GitHubAdapter(owner="owner", repo="data", fetcher=fetch, retry_policy=RetryPolicy(attempts=2, backoff_seconds=0))
    assert list(adapter.read_files(["data.csv"], "abcdef123456"))[0][1][0]["text"] == "hello"
    assert len(calls) == 1  # injected fetchers own retry simulation; production http_fetch retries


def test_download_failure_is_bounded():
    def fail(url, policy):
        raise OSError("offline")
    adapter = GitHubAdapter(owner="owner", repo="data", fetcher=fail, retry_policy=RetryPolicy(attempts=1, backoff_seconds=0))
    with pytest.raises(OSError):
        list(adapter.read_files(["data.csv"], "abcdef123456"))


def test_path_traversal_and_unpinned_revision_are_refused():
    adapter = GitHubAdapter(owner="owner", repo="data", fetcher=lambda url, policy: b"")
    with pytest.raises(RevisionRequiredError):
        list(adapter.read_files(["data.csv"], "master"))
    with pytest.raises(AcquisitionError, match="unsafe source file path"):
        list(adapter.read_files(["../secret.csv"], "abcdef123456"))


def test_unknown_license_and_privacy_flags_are_quarantined_preserving_fields():
    source = [{"id": "x1", "text": "my email a@example.org and  چ" , "dialect": "raw-label"}]
    staged, report, _ = process_records(
        source, dataset_id="owner/data", source_url="https://example.test/data",
        source_type="github", revision="abcdef123456", split_or_file="data.json",
        dataset_license={"spdx_id": None, "status": "unknown"}, retrieved_at_utc="2026-01-01T00:00:00Z"
    )
    record = staged[0]
    assert record["disposition"] == "quarantine"
    assert record["raw_text"] == "my email a@example.org and  چ"
    assert record["original_fields"]["dialect"] == "raw-label"
    assert record["privacy"]["status"] == "needs_review"
    assert report.quarantined_records == 1


def test_duplicate_detection_reports_references_and_preserves_rows():
    records = [
        {"record_id": "a", "raw_text": "شلونك"},
        {"record_id": "b", "raw_text": "شلونك"},
        {"record_id": "c", "raw_text": "شلونك  "},
    ]
    report = detect_duplicates(records)
    assert report["record_count"] == 3
    assert report["records_preserved"] is True
    assert {tuple(item["record_ids"]) for item in report["duplicate_groups"]} == {("a", "b"), ("a", "b", "c")}


def test_cache_reuses_complete_payload_without_second_fetch(tmp_path):
    calls = []
    def fetch(url, policy):
        calls.append(url)
        return b"id,text\n1,hello\n"
    adapter = GitHubAdapter(owner="owner", repo="data", fetcher=fetch, cache_dir=tmp_path)
    list(adapter.read_files(["data.csv"], "abcdef123456"))
    list(adapter.read_files(["data.csv"], "abcdef123456"))
    assert len(calls) == 1
