"""Canonical staging record contract and dependency-free validation."""

from __future__ import annotations

from typing import Any, Dict, List

# JSON-Schema-like contract kept as a plain mapping so runtime validation has no
# jsonschema dependency. Versioned with source_registry.v1.json.
STAGING_RECORD_SCHEMA: Dict[str, Any] = {
    "$schema_version": "1.0.0",
    "type": "object",
    "required": ["schema_version", "record_id", "raw_text", "source", "original_fields", "labels", "licensing", "privacy", "disposition"],
    "properties": {
        "schema_version": "string",
        "record_id": "string",
        "raw_text": "string (unaltered source text)",
        "source": ["dataset_id", "source_url", "source_type", "revision", "split_or_file", "source_record_id", "retrieved_at_utc"],
        "original_fields": "object (preserve unrecognized source columns without dropping them)",
        "labels": "any (source labels as provided; do not infer or rewrite)",
        "licensing": ["dataset_license", "record_license", "license_evidence", "status", "commercial_use_allowed", "redistribution_allowed", "attribution_required"],
        "privacy": ["status", "review_notes"],
        "disposition": "accepted | quarantine | restricted",
    },
    "notes": [
        "Raw text must remain unchanged; normalized text, if later added, is a separate field.",
        "Unknown licensing or privacy must be represented explicitly and quarantined.",
        "A dataset-level license does not override record-level restrictions or third-party rights.",
        "Original source fields and labels are preserved in original_fields and labels.",
    ],
}

REQUIRED_TOP_LEVEL = set(STAGING_RECORD_SCHEMA["required"])
REQUIRED_SOURCE = {"dataset_id", "source_url", "source_type", "revision", "split_or_file", "source_record_id", "retrieved_at_utc"}
REQUIRED_LICENSE = {"dataset_license", "record_license", "license_evidence", "status", "commercial_use_allowed", "redistribution_allowed", "attribution_required"}


class StagingRecordError(ValueError):
    """Raised when a canonical staging record fails validation."""


def validate_staging_record(record: Dict[str, Any]) -> None:
    """Validate required staging fields while allowing extra source metadata."""
    if not isinstance(record, dict):
        raise StagingRecordError("record must be an object")
    missing = sorted(REQUIRED_TOP_LEVEL - set(record))
    if missing:
        raise StagingRecordError("missing required fields: " + ", ".join(missing))
    if record.get("schema_version") != STAGING_RECORD_SCHEMA["$schema_version"]:
        raise StagingRecordError("unsupported or missing schema_version")
    if not isinstance(record.get("record_id"), str) or not record["record_id"].strip():
        raise StagingRecordError("record_id must be a non-empty string")
    if not isinstance(record.get("raw_text"), str):
        raise StagingRecordError("raw_text must be a string and must not be normalized here")
    for key in ("source", "original_fields", "licensing", "privacy"):
        if not isinstance(record.get(key), dict):
            raise StagingRecordError(key + " must be an object")
    missing_source = sorted(REQUIRED_SOURCE - set(record["source"]))
    if missing_source:
        raise StagingRecordError("source missing fields: " + ", ".join(missing_source))
    missing_license = sorted(REQUIRED_LICENSE - set(record["licensing"]))
    if missing_license:
        raise StagingRecordError("licensing missing fields: " + ", ".join(missing_license))
    if record["disposition"] not in {"accepted", "quarantine", "restricted"}:
        raise StagingRecordError("disposition must be accepted, quarantine, or restricted")
    for flag in ("commercial_use_allowed", "redistribution_allowed", "attribution_required"):
        if record["licensing"][flag] not in (True, False, None):
            raise StagingRecordError("licensing.{} must be true, false, or null".format(flag))
    # Conservative default: unresolved licensing/privacy can never be accepted.
    if record["disposition"] == "accepted":
        if record["licensing"]["status"] != "cleared":
            raise StagingRecordError("accepted record requires licensing.status='cleared'")
        if record["licensing"]["redistribution_allowed"] is not True:
            raise StagingRecordError("accepted record requires explicit redistribution permission")
        if record["privacy"].get("status") != "cleared":
            raise StagingRecordError("accepted record requires privacy.status='cleared'")
