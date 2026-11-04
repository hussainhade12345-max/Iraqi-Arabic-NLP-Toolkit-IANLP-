# External data ingestion (Stage 1)

This document describes the safe foundation for importing third-party datasets. The current implementation is a **registry, schema, report writer, and dry-run CLI only**. It does not retrieve records, modify `corpus/` or `lexicon/`, or publish to Hugging Face.

## Safety defaults

- Dry-run is the default. `python -m iraqi_nlp.external_data --source OWNER/DATASET --report-prefix staging/external_import_reports/NAME` validates the registered source and writes a JSON and Markdown planning report.
- The CLI makes no network requests. `--download` is deliberately refused in Stage 1, even if `--approve-downloads` is also supplied. A later adapter implementation must have explicit approval gates.
- Reports are created with exclusive file creation. If either report already exists, the command refuses to overwrite it.
- Existing corpus, lexicon, and sample dataset files are not import destinations. Imported records must later be isolated in a dedicated staging/quarantine area.
- No records are considered accepted by the current CLI. Unknown or unresolved record rights/privacy are quarantined by schema policy.

## Source registry

The versioned registry is `iraqi_nlp/external_data/source_registry.v1.json`. It records the four approved dataset IDs, source URLs/types, preliminary format/license findings, revision pin state, import state, and default disposition. Preliminary facts from the audit are marked as reported and require direct verification at a pinned revision before use. `not_imported` and a null last-import date are intentional.

Registry license status is not a legal determination. In particular:

- The reported `CC-BY-NC-4.0` for `factlogic/iraqi-arabic-dialect-corpus-v2` requires non-commercial separation; record-level license and platform terms must be inspected individually.
- The reported `CC0-1.0` for `ebady/Iraqi-Arabic-Dialect-Dataset` does not automatically clear rights in underlying third-party social-media or other content. Provenance/privacy review remains required.
- License details for `ameer4wisam/iraqi_words_finetuning` and `ArSyra/arsyra-iraqi` were unknown in the initial audit. They remain quarantined pending verification.
- A record-level license field being present does not itself authorize redistribution.

Do not treat these preliminary registry values as verified current metadata; refresh and pin source revisions before any actual download.

## Canonical staging record

`iraqi_nlp.external_data.schema.STAGING_RECORD_SCHEMA` defines a versioned, dependency-free contract. Records preserve raw text exactly, original fields, source record IDs, revisions/files, original labels, and licensing/privacy evidence. Normalized text, if added by a later processing phase, must be separate. Unknown permissions are represented as `null`/unknown and must not be accepted. Accepted records require explicit redistribution clearance and privacy clearance.

## Reports and CLI

Example dry run:

```bash
python -m iraqi_nlp.external_data \
  --source factlogic/iraqi-arabic-dialect-corpus-v2 \
  --report-prefix staging/external_import_reports/factlogic-plan
```

This writes `factlogic-plan.json` and `factlogic-plan.md`. It reports zero discovered, downloaded, and accepted records because no adapter/network operation exists yet. The default report prefix is `staging/external_import_reports/import-report`; specify one source to avoid collisions between separate reports.

## Implemented versus planned

**Implemented:** versioned registry validation, staging-record validation, dry-run planning, JSON/Markdown report generation, and overwrite collision protection.

**Not implemented yet:** Hugging Face/GitHub readers, CSV/JSON/JSONL/Parquet adapters, retries/pagination/resume, license/privacy record assessment, duplicate scans, staging data writes, scheduled/manual Actions workflow, and any upload/publishing support. No successful imports are claimed.

Run the local tests with `pytest -v tests/test_external_data_stage1.py`. These tests use no external datasets or network calls.
