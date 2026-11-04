# External data ingestion (Stage 2 adapters)

Stage 2 adds local CSV, JSON, JSONL readers, pinned-file Hugging Face and GitHub adapters, optional Parquet parsing, record mapping/policy checks, duplicate reporting, and bounded network acquisition. These modules are tested with local fixtures and injected mock fetchers. **No registered real dataset was downloaded or imported as part of this implementation.**

## Local readers

`iraqi_nlp.external_data.adapters.read_local_file(path)` reads CSV, JSON arrays/objects (`records`, `data`, or `samples` arrays), JSONL, and Parquet if a compatible optional engine (`pyarrow` or `fastparquet`) is installed. CSV/JSON/JSONL use the Python standard library. Original fields are returned as dictionaries.

## Pinned remote file adapters

- `HuggingFaceAdapter(dataset_id="owner/name")` fetches explicitly listed files via Hub resolve URLs. Requires a 7–64 character hexadecimal commit SHA.
- `GitHubAdapter(owner="owner", repo="name")` fetches explicitly listed files via `raw.githubusercontent.com` at a 7–64 character commit SHA.
- Branch aliases (`main`, `master`, `latest`, `HEAD`) and unsafe paths are rejected. Adapters do not enumerate repositories; callers must provide file paths and pinned revisions.
- `RetryPolicy` bounds attempts (max 5), request timeout (max 120 seconds), backoff, and per-file maximum bytes (default 50 MiB).
- An optional cache stores complete file responses keyed by immutable URL for rerun/resume at file granularity. It is not a partial HTTP range/resume downloader.

No tokens are needed for public files. Private authenticated repositories are not supported in this stage. No upload or publish adapter exists.

## Mapping and safety policy

`map_to_staging_record()` preserves source data in `original_fields`, maps recognized text without normalization, retains original labels, and records the explicit file, revision, and record reference. Missing text is preserved as an empty string and reported; it is not fabricated. Email- and phone-like patterns trigger `privacy.status=needs_review`; this is a conservative signal, not a complete PII detector.

All mapped records default to `disposition=quarantine`. Dataset-level licenses are not treated as record-level clearance. A reported CC0 source does not automatically clear rights in underlying third-party social content. A non-commercial flag segregates records as `restricted`; unknown or unreviewed rights remain quarantined. No record is accepted by automated heuristics. Acceptance requires a separate reviewer decision with explicit redistribution and privacy clearance.

`detect_duplicates()` reports exact text hashes and whitespace/case-folded duplicate groups with all record IDs; it never removes records. It does not claim semantic or fuzzy/near-duplicate detection.

`process_records()` operates only on provided in-memory/local or mocked rows; it makes no network requests and writes no data files. The Stage 1 CLI continues to refuse downloads while the registry says downloads are disabled. The four registry entries still have unpinned revisions, so they cannot be fetched until a human verifies metadata and pins immutable commits. Real imports remain unauthorized and must not be run without separate approval.

## Tests

Run local/mock tests:

```bash
pytest -v tests/test_external_data_stage1.py tests/test_external_data_adapters.py
```

Tests do not access the network. Parquet behavior is optional; the test confirms a clear missing-engine/invalid-file error path when Parquet cannot be read.
