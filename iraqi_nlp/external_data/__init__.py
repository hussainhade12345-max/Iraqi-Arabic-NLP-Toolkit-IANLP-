"""Safe external-data ingestion foundations for IANLP.

This package currently provides registry/schema/reporting and dry-run planning only.
It does not download data or publish datasets.
"""

from .registry import RegistryError, load_registry, validate_registry
from .schema import STAGING_RECORD_SCHEMA, StagingRecordError, validate_staging_record
from .reports import ImportReport, ReportOutputError, write_reports

__all__ = [
    "ImportReport",
    "RegistryError",
    "ReportOutputError",
    "STAGING_RECORD_SCHEMA",
    "StagingRecordError",
    "load_registry",
    "validate_registry",
    "validate_staging_record",
    "write_reports",
]
