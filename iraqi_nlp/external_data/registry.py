"""Versioned external source registry loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List


class RegistryError(ValueError):
    """Raised when a source registry is malformed or unsafe."""


REGISTRY_PATH = Path(__file__).with_name("source_registry.v1.json")
ALLOWED_SOURCE_TYPES = {"huggingface", "github"}
ALLOWED_IMPORT_STATUSES = {"not_imported", "planned", "imported", "failed"}


def validate_registry(registry: Dict[str, Any]) -> None:
    """Validate registry structure and safety invariants; raise on first issue."""
    if not isinstance(registry, dict):
        raise RegistryError("registry must be a JSON object")
    for key in ("registry_version", "schema_version", "policy", "sources"):
        if key not in registry:
            raise RegistryError("missing registry key: {}".format(key))
    policy = registry["policy"]
    if not isinstance(policy, dict) or policy.get("default_mode") != "dry-run":
        raise RegistryError("policy.default_mode must be dry-run")
    if policy.get("downloads_enabled") is not False:
        raise RegistryError("downloads must remain disabled in the source registry")
    if policy.get("never_modify_existing_dataset_files") is not True:
        raise RegistryError("registry must prohibit modifying existing dataset files")
    sources = registry["sources"]
    if not isinstance(sources, list) or not sources:
        raise RegistryError("sources must be a non-empty list")
    seen = set()
    for index, source in enumerate(sources):
        prefix = "sources[{}]".format(index)
        if not isinstance(source, dict):
            raise RegistryError(prefix + " must be an object")
        required = ("dataset_id", "url", "source_type", "dataset_license", "record_license",
                    "revision", "import_status", "last_successful_import_date", "default_disposition")
        missing = [key for key in required if key not in source]
        if missing:
            raise RegistryError(prefix + " missing keys: " + ", ".join(missing))
        dataset_id = source["dataset_id"]
        if not isinstance(dataset_id, str) or not dataset_id.strip() or dataset_id in seen:
            raise RegistryError(prefix + " has empty or duplicate dataset_id")
        seen.add(dataset_id)
        if source["source_type"] not in ALLOWED_SOURCE_TYPES:
            raise RegistryError(prefix + " has unsupported source_type")
        if not isinstance(source["url"], str) or not source["url"].startswith("https://"):
            raise RegistryError(prefix + " URL must use HTTPS")
        if source["import_status"] not in ALLOWED_IMPORT_STATUSES:
            raise RegistryError(prefix + " has invalid import_status")
        if source["import_status"] == "not_imported" and source["last_successful_import_date"] is not None:
            raise RegistryError(prefix + " unimported source cannot have a successful import date")
        license_info = source["dataset_license"]
        if not isinstance(license_info, dict) or "status" not in license_info or "spdx_id" not in license_info:
            raise RegistryError(prefix + " dataset_license must include status and spdx_id")
        if license_info["status"] == "unknown" and license_info["spdx_id"] is not None:
            raise RegistryError(prefix + " unknown license must not assert an SPDX identifier")
        if not isinstance(source["record_license"], dict):
            raise RegistryError(prefix + " record_license must be an object")
        if not isinstance(source["revision"], dict) or "value" not in source["revision"]:
            raise RegistryError(prefix + " revision must explicitly state value (null if unpinned)")


def load_registry(path: Path | str | None = None) -> Dict[str, Any]:
    """Load and validate a JSON registry from path or the packaged versioned file."""
    registry_path = Path(path) if path is not None else REGISTRY_PATH
    try:
        with registry_path.open("r", encoding="utf-8") as handle:
            registry = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise RegistryError("cannot load registry {}: {}".format(registry_path, exc)) from exc
    validate_registry(registry)
    return registry
