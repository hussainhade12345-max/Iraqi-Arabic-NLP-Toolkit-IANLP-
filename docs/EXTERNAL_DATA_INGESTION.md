# External data ingestion (Stage 3 integration and profiling)

Stage 3 connects local readers, the registry, canonical staging mapping, quarantine policy, and reports. The CLI remains **dry-run only**. It accepts a local fixture file for profiling and makes no network requests. There is still no authorization to import any of the four registered external datasets.

## Exact CLI examples

List registered sources without reading data:

```bash
python -m iraqi_nlp.external_data
```

Profile a locally supplied JSONL fixture using a registered source's metadata; this does not contact the source URL:

```bash
python -m iraqi_nlp.external_data \
  --source ameer4wisam/iraqi_words_finetuning \
  --input /tmp/local-fixture.jsonl \
  --revision abcdef123456 \
  --chunk-size 500 \
  --checkpoint /tmp/ianlp-import-progress.json \
  --report-prefix /tmp/ianlp-profile
```

Resume from a matching checkpoint after interruption:

```bash
python -m iraqi_nlp.external_data \
  --source ameer4wisam/iraqi_words_finetuning \
  --input /tmp/local-fixture.jsonl \
  --revision abcdef123456 \
  --chunk-size 500 \
  --checkpoint /tmp/ianlp-import-progress.json \
  --resume \
  --report-prefix /tmp/ianlp-profile-resumed
```

Reports are created exclusively; existing JSON or Markdown report paths cause a refusal. Checkpoints contain only source fingerprint, dataset identifier, processing configuration, and completed record count. They do not contain raw text. Do not use a checkpoint path that aliases an input file. A file SHA-256 and configuration must match to resume.

## Streaming and dataset profiles

CSV and JSONL are read row-wise; optional Parquet uses `pyarrow` batch iteration. JSON arrays are parsed by the standard library and therefore are **not bounded-memory streaming**. Duplicate profiling retains text fingerprints and counters, not source text; this still grows with the number of unique texts. Profile fields include total/valid/malformed rows, missing values, vocabulary size, exact/normalized duplicate rates, word-length buckets, sentiment/intent distributions, source-provided dialect metadata availability, and a script-presence code-switch heuristic.

Profile values are measurements from supplied input. Missing sentiment/intent metadata is labeled `unavailable_metadata_not_present`. Dialect/region statistics count only supplied fields; the profiler never infers a speaker's identity, region, or dialect. Code-switch statistics are heuristic script detection, not validated language ID.

Reports include the requested revision, input URL/type/file hash, license status, and processing configuration. In dry-run, records are never accepted; mapped records remain quarantined. No staging record file is emitted by this CLI.

## Tests

Run local fixtures and mocked sources only:

```bash
pytest -v tests/test_external_data_stage1.py tests/test_external_data_adapters.py tests/test_external_data_stage3.py
```

No real external dataset download or Hugging Face upload is part of Stage 3. Remote adapters remain available as library building blocks but the CLI refuses `--download` pending separate explicit authorization and pinned source metadata.
