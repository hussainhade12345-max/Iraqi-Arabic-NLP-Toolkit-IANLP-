"""
Dataset quality, integrity, schema validation, and leakage detection for IANLP.
أدوات فحص جودة البيانات والتحقق من صحتها وتفادي تسريب البيانات
"""

import os
import json
import pandas as pd
from typing import Dict, List, Set, Any, Optional, Tuple
from dataclasses import dataclass, field

from .normalizer import normalize_iraqi_text

# Authoritative documented complaint domains (IANLP taxonomy)
VALID_DOMAINS = {
    "infrastructure",
    "healthcare",
    "education",
    "employment",
    "security",
    "housing",
    "administrative",
    "mixed",
}

# Aliases and uppercase variations mapped to canonical domain
DOMAIN_MAP = {
    "infra": "infrastructure",
    "infrastructure": "infrastructure",
    "infrastructure & services": "infrastructure",
    "health": "healthcare",
    "healthcare": "healthcare",
    "educ": "education",
    "education": "education",
    "employ": "employment",
    "employment": "employment",
    "security": "security",
    "housing": "housing",
    "admin": "administrative",
    "administrative": "administrative",
    "administrative services": "administrative",
    "mixed": "mixed",
    "other": "mixed",
}

# Documented valid CSV column sets
CORPUS_COLUMNS = [
    "post_id", "text", "governorate", "source", "date_collected", "labels", "confidence", "notes"
]
TECHNICAL_SPEC_COLUMNS = [
    "text_id", "text", "label_primary", "label_secondary", "text_normalized",
    "dialect_region", "is_codeswitched", "english_tokens", "register",
    "source", "collection_date", "annotator_id", "annotation_confidence"
]


@dataclass
class ValidationReport:
    """Report detailing dataset integrity, schema checks, duplicates, and leakage."""
    dataset_name: str
    total_records: int = 0
    missing_fields: List[str] = field(default_factory=list)
    null_text_count: int = 0
    empty_text_count: int = 0
    duplicate_exact_count: int = 0
    duplicate_normalized_count: int = 0
    invalid_labels: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset_name": self.dataset_name,
            "total_records": self.total_records,
            "is_valid": self.is_valid,
            "missing_fields": self.missing_fields,
            "null_text_count": self.null_text_count,
            "empty_text_count": self.empty_text_count,
            "duplicate_exact_count": self.duplicate_exact_count,
            "duplicate_normalized_count": self.duplicate_normalized_count,
            "invalid_labels": self.invalid_labels,
            "warnings": self.warnings,
            "errors": self.errors,
        }


def validate_dataframe_schema(
    df: pd.DataFrame,
    required_columns: Optional[List[str]] = None,
    dataset_name: str = "dataset"
) -> ValidationReport:
    """
    Validate schema and content of a DataFrame containing Iraqi Arabic records.

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame to inspect
    required_columns : Optional[List[str]]
        Expected column names
    dataset_name : str
        Label for the dataset in report

    Returns:
    --------
    ValidationReport
    """
    report = ValidationReport(dataset_name=dataset_name, total_records=len(df))

    if df.empty:
        report.warnings.append("DataFrame is empty (0 records).")
        return report

    # 1. Schema check
    if required_columns:
        missing = [col for col in required_columns if col not in df.columns]
        if missing:
            report.missing_fields = missing
            report.errors.append(f"Missing required columns: {missing}")
            report.is_valid = False

    # 2. Text column inspection
    text_col = next(
        (c for c in df.columns if c.lower() in ["text", "post", "content", "tweet", "نص"]),
        None
    )
    if not text_col:
        report.errors.append("No text column identified.")
        report.is_valid = False
        return report

    null_count = df[text_col].isnull().sum()
    report.null_text_count = int(null_count)
    if null_count > 0:
        report.errors.append(f"Found {null_count} null text values in '{text_col}'.")
        report.is_valid = False

    clean_series = df[text_col].dropna().astype(str).str.strip()
    empty_count = (clean_series == "").sum()
    report.empty_text_count = int(empty_count)
    if empty_count > 0:
        report.errors.append(f"Found {empty_count} blank/whitespace-only text records.")
        report.is_valid = False

    # 3. Duplicate detection
    exact_dups = int(clean_series.duplicated().sum())
    report.duplicate_exact_count = exact_dups
    if exact_dups > 0:
        report.warnings.append(f"Detected {exact_dups} duplicate exact text records.")

    normalized_series = clean_series.apply(normalize_iraqi_text)
    norm_dups = int(normalized_series.duplicated().sum())
    report.duplicate_normalized_count = norm_dups
    if norm_dups > exact_dups:
        report.warnings.append(
            f"Detected {norm_dups - exact_dups} additional duplicates after normalization."
        )

    # 4. Label validation (if label column exists)
    label_col = next(
        (c for c in df.columns if c.lower() in ["label", "labels", "label_primary", "domain", "category", "sentiment"]),
        None
    )
    if label_col:
        unique_labels = df[label_col].dropna().astype(str).unique()
        # If sentiment column or dataset
        if label_col == "sentiment" or "sentiment" in dataset_name.lower():
            valid_sentiments = {"positive", "negative", "neutral"}
            for lab in unique_labels:
                if lab.strip().lower() not in valid_sentiments:
                    report.invalid_labels.append(lab)
            if report.invalid_labels:
                report.warnings.append(f"Unknown sentiment labels: {set(report.invalid_labels)}")
        else:
            for lab in unique_labels:
                lab_clean = lab.strip().lower()
                if lab_clean not in VALID_DOMAINS and lab_clean not in DOMAIN_MAP:
                    report.invalid_labels.append(lab)
            if report.invalid_labels:
                report.warnings.append(f"Unknown domain labels: {set(report.invalid_labels)}")

    return report


def validate_json_dataset(filepath: str) -> ValidationReport:
    """
    Validate sample dataset JSON files against documented schema.
    """
    report = ValidationReport(dataset_name=os.path.basename(filepath))
    if not os.path.exists(filepath):
        report.errors.append(f"File not found: {filepath}")
        report.is_valid = False
        return report

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Handle file preamble comments (e.g. triple quotes) if present
        clean_content = content
        if clean_content.strip().startswith('"""'):
            clean_content = clean_content.strip()
            end_idx = clean_content.find('"""', 3)
            if end_idx != -1:
                clean_content = clean_content[end_idx + 3:].strip()

        data = json.loads(clean_content)
    except Exception as e:
        report.errors.append(f"JSON parse error: {e}")
        report.is_valid = False
        return report

    samples = data.get("corpus_samples") or data.get("samples") or []
    report.total_records = len(samples)

    if not samples:
        report.warnings.append("JSON dataset contains no sample records.")
        return report

    df = pd.DataFrame(samples)
    return validate_dataframe_schema(
        df,
        required_columns=["text_id", "text", "label_primary"],
        dataset_name=os.path.basename(filepath)
    )


def detect_data_leakage(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    text_column: str = "text"
) -> Dict[str, Any]:
    """
    Check for train/validation/test data leakage (shared samples).

    Returns:
    --------
    Dict containing overlap counts and intersecting samples.
    """
    def get_texts(df: pd.DataFrame) -> Set[str]:
        if df is None or df.empty or text_column not in df.columns:
            return set()
        return set(df[text_column].dropna().astype(str).str.strip().apply(normalize_iraqi_text))

    train_set = get_texts(train_df)
    val_set = get_texts(val_df)
    test_set = get_texts(test_df)

    train_val_overlap = list(train_set & val_set)
    train_test_overlap = list(train_set & test_set)
    val_test_overlap = list(val_set & test_set)

    has_leakage = bool(train_val_overlap or train_test_overlap or val_test_overlap)

    return {
        "has_leakage": has_leakage,
        "train_val_overlap_count": len(train_val_overlap),
        "train_test_overlap_count": len(train_test_overlap),
        "val_test_overlap_count": len(val_test_overlap),
        "train_val_overlap_samples": train_val_overlap[:5],
        "train_test_overlap_samples": train_test_overlap[:5],
        "val_test_overlap_samples": val_test_overlap[:5],
    }
