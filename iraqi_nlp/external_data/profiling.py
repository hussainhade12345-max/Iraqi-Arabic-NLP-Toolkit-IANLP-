"""Dataset quality profiling with explicit measurement definitions and unknowns."""

from __future__ import annotations

import hashlib
import re
from collections import Counter
from typing import Any, Dict, Mapping

ARABIC_RE = re.compile(r"[\u0600-\u06ff\u0750-\u077f\u08a0-\u08ff\ufb50-\ufdff\ufe70-\ufeff]")
LATIN_RE = re.compile(r"[A-Za-z]")
TEXT_FIELDS = ("text", "raw_text", "sentence", "content", "tweet", "post", "word", "iraqi_term")
DIALECT_FIELDS = ("dialect_region", "dialect", "dialect_label", "region", "governorate")


class DatasetProfiler:
    """Accumulate profiles without retaining record text, only tokens/fingerprints."""

    def __init__(self) -> None:
        self.total_records = 0
        self.nonempty_text_records = 0
        self.canonical_schema_valid_records = 0
        self.malformed_records = 0
        self.missing_text = 0
        self.missing_values: Counter[str] = Counter()
        self.sentiment: Counter[str] = Counter()
        self.intent: Counter[str] = Counter()
        self.dialect_values: Dict[str, Counter[str]] = {field: Counter() for field in DIALECT_FIELDS}
        self.code_switch_mixed = 0
        self.code_switch_records_measured = 0
        self.text_lengths: Counter[str] = Counter()
        self.whitespace_tokens: set[str] = set()
        self.exact_hashes: Counter[str] = Counter()
        self.normalized_hashes: Counter[str] = Counter()

    @staticmethod
    def _bucket(length: int) -> str:
        if length == 0: return "0"
        if length <= 10: return "1-10"
        if length <= 25: return "11-25"
        if length <= 50: return "26-50"
        if length <= 100: return "51-100"
        return "101+"

    def add(self, record: Mapping[str, Any], canonical_valid: bool = False) -> None:
        self.total_records += 1
        if not isinstance(record, Mapping):
            self.malformed_records += 1
            return
        key = next((name for name in TEXT_FIELDS if name in record), None)
        text = record.get(key) if key else None
        if not isinstance(text, str) or not text.strip():
            self.missing_text += 1
            self.missing_values["text"] += 1
            self.malformed_records += 1
        else:
            self.nonempty_text_records += 1
            if canonical_valid:
                self.canonical_schema_valid_records += 1
            tokens = text.split()
            self.text_lengths[self._bucket(len(tokens))] += 1
            self.whitespace_tokens.update(token.casefold() for token in tokens)
            canonical = " ".join(text.split()).casefold()
            self.exact_hashes[hashlib.sha256(text.encode("utf-8")).hexdigest()] += 1
            self.normalized_hashes[hashlib.sha256(canonical.encode("utf-8")).hexdigest()] += 1
            arabic, latin = len(ARABIC_RE.findall(text)), len(LATIN_RE.findall(text))
            if arabic + latin:
                self.code_switch_records_measured += 1
                self.code_switch_mixed += int(bool(arabic and latin))
        for field, value in record.items():
            if value is None or value == "":
                self.missing_values[str(field)] += 1
        if record.get("sentiment") not in (None, ""):
            self.sentiment[str(record["sentiment"])] += 1
        if record.get("intent") not in (None, ""):
            self.intent[str(record["intent"])] += 1
        # Store only source-provided values; never infer speaker attributes.
        for field in DIALECT_FIELDS:
            value = record.get(field)
            if value not in (None, ""):
                self.dialect_values[field][str(value)] += 1

    @staticmethod
    def _duplicates(counter: Counter[str]) -> int:
        return sum(count - 1 for count in counter.values() if count > 1)

    def to_state(self) -> Dict[str, Any]:
        return {
            "total_records": self.total_records, "nonempty_text_records": self.nonempty_text_records,
            "canonical_schema_valid_records": self.canonical_schema_valid_records,
            "malformed_records": self.malformed_records, "missing_text": self.missing_text,
            "missing_values": dict(self.missing_values), "sentiment": dict(self.sentiment),
            "intent": dict(self.intent),
            "dialect_values": {k: dict(v) for k, v in self.dialect_values.items()},
            "code_switch_mixed": self.code_switch_mixed,
            "code_switch_records_measured": self.code_switch_records_measured,
            "text_lengths": dict(self.text_lengths), "whitespace_tokens": sorted(self.whitespace_tokens),
            "exact_hashes": dict(self.exact_hashes), "normalized_hashes": dict(self.normalized_hashes),
        }

    def restore_state(self, state: Mapping[str, Any]) -> None:
        """Restore profiler state from a validated checkpoint payload."""
        for name in ("total_records", "nonempty_text_records", "canonical_schema_valid_records", "malformed_records", "missing_text", "code_switch_mixed", "code_switch_records_measured"):
            setattr(self, name, int(state.get(name, 0)))
        self.missing_values.update(state.get("missing_values", {}))
        self.sentiment.update(state.get("sentiment", {}))
        self.intent.update(state.get("intent", {}))
        self.text_lengths.update(state.get("text_lengths", {}))
        self.whitespace_tokens.update(state.get("whitespace_tokens", []))
        self.exact_hashes.update(state.get("exact_hashes", {}))
        self.normalized_hashes.update(state.get("normalized_hashes", {}))
        for field, values in state.get("dialect_values", {}).items():
            if field in self.dialect_values:
                self.dialect_values[field].update(values)

    def to_dict(self) -> Dict[str, Any]:
        n = self.nonempty_text_records
        exact = self._duplicates(self.exact_hashes)
        normalized = self._duplicates(self.normalized_hashes)
        return {
            "total_records": self.total_records,
            "nonempty_text_records": self.nonempty_text_records,
            "canonical_schema_valid_records": self.canonical_schema_valid_records,
            "canonical_schema_validity_basis": "record passed staging-schema validation; not equivalent to non-empty text",
            "malformed_records": self.malformed_records,
            "missing_text_records": self.missing_text,
            "missing_values_by_field": dict(sorted(self.missing_values.items())),
            "unique_whitespace_token_count_casefolded": len(self.whitespace_tokens),
            "vocabulary_measurement": "whitespace-split tokens, case-folded; not linguistic tokenization",
            "duplicate_rates": {"exact_duplicate_records": exact, "exact_rate": exact / n if n else 0.0,
                                 "normalized_duplicate_records": normalized, "normalized_rate": normalized / n if n else 0.0},
            "text_word_length_distribution": dict(sorted(self.text_lengths.items())),
            "sentiment_label_distribution": dict(sorted(self.sentiment.items())) if self.sentiment else {"status": "unavailable_metadata_not_present"},
            "intent_label_distribution": dict(sorted(self.intent.items())) if self.intent else {"status": "unavailable_metadata_not_present"},
            "code_switching": {"records_with_script_measurement": self.code_switch_records_measured,
                "mixed_arabic_latin_records": self.code_switch_mixed,
                "mixed_rate_among_measured": self.code_switch_mixed / self.code_switch_records_measured if self.code_switch_records_measured else None,
                "method": "Unicode script presence heuristic; not validated language identification"},
            "dialect_metadata": {"status": "source_metadata_only_no_inference",
                "value_distributions": {k: dict(sorted(v.items())) for k, v in self.dialect_values.items() if v}},
        }
