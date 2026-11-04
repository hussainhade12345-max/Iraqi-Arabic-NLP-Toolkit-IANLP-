"""Conservative record-level rights and privacy policy.

No dataset-level license declaration is treated as per-record clearance.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Optional

PERMISSION_FIELDS = (
    "retain_allowed",
    "process_allowed",
    "train_allowed",
    "redistribute_allowed",
    "commercial_use_allowed",
)


def _explicit_bool(value: Any) -> Optional[bool]:
    return value if isinstance(value, bool) else None


def apply_record_policy(record: Dict[str, Any], reviewer_decision: Optional[Mapping[str, Any]] = None, **legacy: Any) -> Dict[str, Any]:
    """Set disposition without allowing review to override explicit restrictions.

    Legacy ``reviewer_cleared=True`` is intentionally not accepted as a clearance:
    approval must name each permission explicitly in ``reviewer_decision``.
    """
    licensing = record.setdefault("licensing", {})
    privacy = record.setdefault("privacy", {})
    for key in PERMISSION_FIELDS:
        licensing[key] = _explicit_bool(licensing.get(key))

    if licensing["commercial_use_allowed"] is False:
        record["disposition"] = "restricted"
        return record
    if any(licensing[key] is False for key in PERMISSION_FIELDS if key != "commercial_use_allowed"):
        record["disposition"] = "restricted"
        return record

    if reviewer_decision is not None:
        # Review can establish missing evidence only; it cannot override an explicit
        # false permission stored in the source/license record.
        for key in PERMISSION_FIELDS:
            decision_value = reviewer_decision.get(key)
            if licensing[key] is False and decision_value is True:
                record["disposition"] = "restricted"
                return record
            if licensing[key] is None:
                licensing[key] = _explicit_bool(decision_value)
        if reviewer_decision.get("license_status") == "cleared":
            licensing["status"] = "cleared"
        if reviewer_decision.get("privacy_status") == "cleared":
            privacy["status"] = "cleared"

    allowed = all(licensing[key] is True for key in PERMISSION_FIELDS if key != "commercial_use_allowed")
    commercial_not_prohibited = licensing["commercial_use_allowed"] is not False
    cleared = licensing.get("status") == "cleared" and privacy.get("status") == "cleared"
    record["disposition"] = "accepted" if allowed and commercial_not_prohibited and cleared else "quarantine"
    return record
