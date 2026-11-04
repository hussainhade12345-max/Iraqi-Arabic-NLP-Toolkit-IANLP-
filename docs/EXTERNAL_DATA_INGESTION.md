# External data ingestion (Stage 5 safety fixes)

Stage 5 adds permission-specific rights checks, aggregate-state checkpoints, and one-pass duplicate detection. This remains a **readiness/testing stage**. It does not authorize or perform any real external dataset access.

## Rights model

Staging records distinguish permission to retain, process, train on, and redistribute. `commercial_use_allowed` is separately recorded. Each permission is `true`, `false`, or unknown (`null`). Explicit `false` always results in `restricted`; unknown stays quarantined. Review can supply missing explicit evidence but cannot override a source/license prohibition. Dataset-level licenses do not establish permission for every underlying record. Acceptance requires all non-commercial-use permissions explicit and true, a cleared license status, and cleared privacy status. A false commercial-use flag prevents automatic acceptance into a general-purpose output; non-commercial-only material must remain segregated for a separate, properly scoped workflow.

## Checkpoints and profiles

A resume validates the input SHA-256, dataset ID, and processing configuration. It restores accumulated counters, hashes, and vocabulary state so final profiling represents the full input, not just remaining rows. Checkpoints may contain vocabulary and metadata values; protect them as sensitive artifacts. Checkpoint paths resolving to the input file are rejected. The checkpoint format is internal and versioned indirectly by the processing configuration; do not hand-edit it.

Profiling distinguishes `nonempty_text_records` from `canonical_schema_valid_records`. Vocabulary is explicitly `unique_whitespace_token_count_casefolded`; it is not a linguistic tokenizer output. Dialect/region output provides distributions only for source-present values. Code-switch statistics remain a simple Unicode script-presence heuristic and are not validated language labels.

## Remote streaming scope

An opt-in library method streams pinned remote CSV and JSONL rows with a byte cap and bounded open retries. JSON remains bounded-buffered because the standard library parser is not incremental. Parquet streaming is available only for local files with optional `pyarrow`. The CLI does not call remote adapters and continues to reject `--download`.

## Local regression checks

```bash
pytest -v tests/test_external_data_stage1.py tests/test_external_data_adapters.py tests/test_external_data_stage3.py tests/test_external_data_stage5.py
```

Stage 5 tests use local fixtures or mocks only. No real external dataset was downloaded and no Hugging Face write operation exists in this pipeline.
