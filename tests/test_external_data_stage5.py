"""External ingestion license and profiling regression tests; local-only."""

import json

import pytest

from iraqi_nlp.external_data.adapters import apply_record_policy as legacy_policy, detect_duplicates
from iraqi_nlp.external_data.integration import ResumeError, profile_local_file
from iraqi_nlp.external_data.licensing import apply_record_policy
from iraqi_nlp.external_data.profiling import DatasetProfiler


def _record(permissions=None):
    return {"licensing": {"status": "needs_review", "redistribution_allowed": None,
        "retain_allowed": None, "process_allowed": None, "train_allowed": None,
        "commercial_use_allowed": None, **(permissions or {})}, "privacy": {"status": "needs_review"}, "disposition": "quarantine"}


def test_commercial_prohibition_cannot_be_overridden_by_review():
    record = _record({"commercial_use_allowed": False})
    result = apply_record_policy(record, {"retain_allowed": True, "process_allowed": True, "train_allowed": True,
        "redistribute_allowed": True, "commercial_use_allowed": True, "license_status": "cleared", "privacy_status": "cleared"})
    assert result["disposition"] == "restricted"
    assert result["licensing"]["commercial_use_allowed"] is False


def test_unknown_permissions_remain_quarantined():
    record = _record()
    result = apply_record_policy(record, {"license_status": "cleared", "privacy_status": "cleared"})
    assert result["disposition"] == "quarantine"


def test_explicit_restriction_on_training_or_redistribution_is_not_overridden():
    for field in ("train_allowed", "redistribute_allowed", "retain_allowed", "process_allowed"):
        record = _record({field: False})
        result = apply_record_policy(record, {field: True, "license_status": "cleared", "privacy_status": "cleared"})
        assert result["disposition"] == "restricted"


def test_all_permissions_and_clearance_required_for_acceptance():
    record = _record({"retain_allowed": True, "process_allowed": True, "train_allowed": True,
                      "redistribute_allowed": True, "commercial_use_allowed": True})
    result = apply_record_policy(record, {"license_status": "cleared", "privacy_status": "cleared"})
    assert result["disposition"] == "accepted"


def test_generator_duplicate_detection_is_one_pass_and_preserves_groups():
    source = ({"record_id": rid, "raw_text": text} for rid, text in [("a", "سلام"), ("b", "سلام"), ("c", "سلام  ")])
    result = detect_duplicates(source)
    assert result["record_count"] == 3
    assert result["records_preserved"] is True
    assert {item["kind"] for item in result["duplicate_groups"]} == {"exact", "normalized"}
    normalized = next(item for item in result["duplicate_groups"] if item["kind"] == "normalized")
    assert normalized["record_ids"] == ["a", "b", "c"]


def test_profiler_distinguishes_nonempty_from_canonical_valid_and_reports_values():
    profiler = DatasetProfiler()
    profiler.add({"text": "نص"}, canonical_valid=False)
    profiler.add({"text": "نص آخر", "dialect_region": "Baghdad", "governorate": "Wasit"}, canonical_valid=True)
    profile = profiler.to_dict()
    assert profile["nonempty_text_records"] == 2
    assert profile["canonical_schema_valid_records"] == 1
    assert profile["unique_whitespace_token_count_casefolded"] == 3
    assert profile["dialect_metadata"]["value_distributions"]["dialect_region"] == {"Baghdad": 1}


def test_checkpoint_resume_restores_full_profile_and_rejects_input_alias(tmp_path):
    source = tmp_path / "rows.jsonl"
    source.write_text("".join(json.dumps({"id": i, "text": "كلمة {}".format(i)}) + "\n" for i in range(8)), encoding="utf-8")
    checkpoint = tmp_path / "checkpoint.json"
    kwargs = dict(dataset_id="owner/test", source_url="https://example.test/data", source_type="github",
        revision="abcdef123456", dataset_license={"status": "unknown"}, checkpoint_path=checkpoint, chunk_size=2)
    partial, _ = profile_local_file(source, interrupted_after=3, **kwargs)
    assert partial.status == "interrupted_checkpointed"
    resumed, profile = profile_local_file(source, resume=True, **kwargs)
    complete, full_profile = profile_local_file(source, dataset_id="owner/test", source_url="https://example.test/data",
        source_type="github", revision="abcdef123456", dataset_license={"status": "unknown"})
    assert profile["total_records"] == full_profile["total_records"] == 8
    assert profile["unique_whitespace_token_count_casefolded"] == full_profile["unique_whitespace_token_count_casefolded"]
    with pytest.raises(ResumeError, match="must not resolve"):
        profile_local_file(source, dataset_id="owner/test", source_url="https://example.test/data", source_type="github",
            revision="abcdef123456", dataset_license={}, checkpoint_path=source)


def test_legacy_adapter_policy_alias_is_also_safe():
    record = _record({"commercial_use_allowed": False})
    assert legacy_policy(record, reviewer_cleared=True)["disposition"] == "restricted"
