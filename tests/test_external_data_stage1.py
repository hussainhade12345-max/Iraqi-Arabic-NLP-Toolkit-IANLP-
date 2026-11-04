import json

import pytest

from iraqi_nlp.external_data import (
    ImportReport,
    RegistryError,
    ReportOutputError,
    StagingRecordError,
    load_registry,
    validate_registry,
    validate_staging_record,
    write_reports,
)
from iraqi_nlp.external_data.cli import main


def test_packaged_registry_has_four_safe_unimported_sources():
    registry = load_registry()
    validate_registry(registry)
    assert len(registry["sources"]) == 4
    assert {item["import_status"] for item in registry["sources"]} == {"not_imported"}
    assert registry["policy"]["default_mode"] == "dry-run"
    assert registry["policy"]["downloads_enabled"] is False


def test_registry_rejects_enabled_downloads():
    registry = load_registry()
    registry["policy"]["downloads_enabled"] = True
    with pytest.raises(RegistryError, match="downloads must remain disabled"):
        validate_registry(registry)


def _record():
    return {
        "schema_version": "1.0.0",
        "record_id": "dataset:abc:1",
        "raw_text": "چانت #بغداد 😀",
        "source": {
            "dataset_id": "owner/dataset", "source_url": "https://example.test/data",
            "source_type": "huggingface", "revision": "abc123", "split_or_file": "train",
            "source_record_id": "1", "retrieved_at_utc": "2026-01-01T00:00:00Z"
        },
        "original_fields": {"text": "چانت #بغداد 😀", "label": "raw-label"},
        "labels": "raw-label",
        "licensing": {
            "dataset_license": "unknown", "record_license": None, "license_evidence": [],
            "status": "unknown", "commercial_use_allowed": None,
            "redistribution_allowed": None, "attribution_required": None
        },
        "privacy": {"status": "needs_review", "review_notes": []},
        "disposition": "quarantine"
    }


def test_staging_schema_preserves_original_content_and_unknown_rights():
    record = _record()
    validate_staging_record(record)
    assert record["raw_text"] == "چانت #بغداد 😀"
    assert record["labels"] == "raw-label"
    assert record["disposition"] == "quarantine"


def test_schema_rejects_acceptance_without_explicit_rights_and_privacy_clearance():
    record = _record()
    record["disposition"] = "accepted"
    with pytest.raises(StagingRecordError, match="licensing.status='cleared'"):
        validate_staging_record(record)


def test_schema_rejects_missing_provenance():
    record = _record()
    del record["source"]["revision"]
    with pytest.raises(StagingRecordError, match="source missing fields"):
        validate_staging_record(record)


def test_dry_run_cli_writes_zero_download_report(tmp_path):
    prefix = tmp_path / "report"
    status = main(["--source", "ameer4wisam/iraqi_words_finetuning", "--report-prefix", str(prefix)])
    assert status == 0
    result = json.loads((tmp_path / "report.json").read_text(encoding="utf-8"))
    assert result["mode"] == "dry-run"
    assert result["records_downloaded"] == 0
    assert result["records_accepted"] == 0
    assert result["license_status"] == "unknown"


def test_cli_refuses_download_even_if_requested(tmp_path):
    status = main(["--download", "--approve-downloads", "--report-prefix", str(tmp_path / "report")])
    assert status == 2
    assert not (tmp_path / "report.json").exists()


def test_report_collision_protection_does_not_overwrite(tmp_path):
    prefix = tmp_path / "existing"
    existing = tmp_path / "existing.json"
    existing.write_text("keep me", encoding="utf-8")
    with pytest.raises(ReportOutputError, match="refusing to overwrite"):
        write_reports(ImportReport(source_id="owner/data"), prefix)
    assert existing.read_text(encoding="utf-8") == "keep me"
    assert not (tmp_path / "existing.md").exists()
