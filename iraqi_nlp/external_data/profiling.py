"""Dataset quality profiling with streaming accumulation and explicit unknowns."""

from __future__ import annotations

import re
from collections import Counter
from typing import Any, Dict, Mapping, Optional

ARABIC_RE = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]")
LATIN_RE = re.compile(r"[A-Za-z]")


class DatasetProfiler:
    """Accumulate descriptive statistics without retaining record text."""

    def __init__(self) -> None:
        self.total_records = 0
        self.valid_records = 0
        self.malformed_records = 0
        self.missing_text = 0
        self.missing_values: Counter[str] = Counter()
        self.sentiment: Counter[str] = Counter()
        self.intent: Counter[str] = Counter()
        self.dialect_metadata: Counter[str] = Counter()
        self.code_switch_mixed = 0
        self.code_switch_records_measured = 0
        self.text_lengths: Counter[str] = Counter()
        self.vocabulary: set[str] = set()
        self.exact_hashes: Counter[str] = Counter()
        self.normalized_hashes: Counter[str] = Counter()

    @staticmethod
    def _bucket(length: int) -> str:
        if length == 0:
            return "0"
        if length <= 10:
            return "1-10"
        if length <= 25:
            return "11-25"
        if length <= 50:
            return "26-50"
        if length <= 100:
            return "51-100"
        return "101+"

    def add(self, record: Mapping[str, Any]) -> None:
        self.total_records += 1
        if not isinstance(record, Mapping):
            self.malformed_records += 1
            return
        text_key = next((key for key in ("text", "raw_text", "sentence", "content", "tweet", "post", "word", "iraqi_term") if key in record), None)
        text = record.get(text_key) if text_key is not None else None
        if not isinstance(text, str) or not text.strip():
            self.missing_text += 1
            self.missing_values["text"] += 1
        else:
            self.valid_records += 1
            words = text.split()
            self.text_lengths[self._bucket(len(words))] += 1
            self.vocabulary.update(word.casefold() for word in words)
            import hashlib
            self.exact_hashes[hashlib.sha256(text.encode("utf-8")).hexdigest()] += 1
            canonical = " ".join(text.split()).casefold()
            self.normalized_hashes[hashlib.sha256(canonical.encode("utf-8")).hexdigest()] += 1
            arabic, latin = len(ARABIC_RE.findall(text)), len(LATIN_RE.findall(text))
            if arabic + latin:
                self.code_switch_records_measured += 1
                if arabic and latin:
                    self.code_switch_mixed += 1
        for key, value in record.items():
            if value is None or value == "":
                self.missing_values[str(key)] += 1
        for key in ("sentiment",):
            if record.get(key) not in (None, ""):
                self.sentiment[str(record[key])] += 1
        if record.get("intent") not in (None, ""):
            self.intent[str(record["intent"])] += 1
        # Only count source-provided metadata; never infer a region or dialect.
        for key in ("dialect_region", "dialect", "dialect_label", "region", "governorate"):
            if record.get(key) not in (None, ""):
                self.dialect_metadata[key] += 1
        if not isinstance(text, str):
            self.malformed_records += 1

    @staticmethod
    def _duplicate_count(counter: Counter[str]) -> int:
        return sum(count - 1 for count in counter.values() if count > 1)

    def to_dict(self) -> Dict[str, Any]:
        n = self.valid_records
        return {
            "total_records": self.total_records,
            "valid_records": self.valid_records,
            "malformed_records": self.malformed_records,
            "missing_text_records": self.missing_text,
            "missing_values_by_field": dict(sorted(self.missing_values.items())),
            "unique_vocabulary_size": len(self.vocabulary),
            "duplicate_rates": {
                "exact_duplicate_records": self._duplicate_count(self.exact_hashes),
                "exact_rate": self._duplicate_count(self.exact_hashes) / n if n else 0.0,
                "normalized_duplicate_records": self._duplicate_count(self.normalized_hashes),
                "normalized_rate": self._duplicate_count(self.normalized_hashes) / n if n else 0.0,
            },
            "text_word_length_distribution": dict(sorted(self.text_lengths.items())),
            "sentiment_label_distribution": dict(sorted(self.sentiment.items()),) if self.sentiment else {"status": "unavailable_metadata_not_present"},
            "intent_label_distribution": dict(sorted(self.intent.items())) if self.intent else {"status": "unavailable_metadata_not_present"},
            "code_switching": {
                "records_with_script_measurement": self.code_switch_records_measured,
                "mixed_arabic_latin_records": self.code_switch_mixed,
                "mixed_rate_among_measured": self.code_switch_mixed / self.code_switch_records_measured if self.code_switch_records_measured else None,
                "method": "Unicode script presence heuristic; not token-level language identification",
            },
            "dialect_metadata": {
                "status": "source_metadata_only_no_inference",
                "field_counts": dict(sorted(self.dialect_metadata.items())) if self.dialect_metadata else {},
                "available": bool(self.dialect_metadata),
            },
        }
