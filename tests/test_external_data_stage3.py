"""Stage 3 integration, profiling, interruption, and resume tests; no network."""

import json

import pytest

from iraqi_nlp.external_data.cli import main
from iraqi_nlp.external_data.integration import ResumeError, profile_local_file
from iraqi_nlp.external_data.reports import ReportOutputError, write_reports, ImportReport


def _registered_source():
    return {
        "dataset_id": "ameer4wisam/iraqi_words_finetuning",
        "url": "https://huggingface.co/datasets/ameer4wisam/iraqi_words_finetuning",
        "source_type": "huggingface",
        "dataset_license": {"spdx_id": None, "status": "unknown"},
    }


def test_streamed_jsonl_profile_has_provenance_and_unavailable_label_metadata(tmp_path):
    input_path = tmp_path / "fixture.jsonl"
    input_path.write_text(
        '{"id":"1","text":"چانت electricity","sentiment":"negative","intent":"complaint"}\n'
        '{"id":"2","text":"هسه الكهرباء","dialect_region":"Baghdad"}\n', encoding="utf-8")
    report, profile = profile_local_file(
        input_path, dataset_id="owner/test", source_url="https://example.test/data",
        source_type="github", revision="abcdef123456", dataset_license={"status": "unknown"}, chunk_size=1)
    assert profile["total_records"] == 2
    assert profile["valid_records"] == 2
    assert profile["unique_vocabulary_size"] == 4
    assert profile["sentiment_label_distribution"] == {"negative": 1}
    assert profile["intent_label_distribution"] == {"complaint": 1}
    assert profile["dialect_metadata"]["status"] == "source_metadata_only_no_inference"
    assert report.source_revision == "abcdef123456"
    assert report.provenance["input_sha256"]
    assert report.records_accepted == 0
    assert report.quarantined_records == 2


def test_cli_profiles_local_only_and_emits_report(tmp_path):
    source = _registered_source()
    input_path = tmp_path / "posts.csv"
    input_path.write_text("id,text\n1,هسه چانت\n", encoding="utf-8")
    prefix = tmp_path / "profile"
    assert main(["--source", source["dataset_id"], "--input", str(input_path), "--revision", "abcdef123456", "--report-prefix", str(prefix)]) == 0
    data = json.loads((tmp_path / "profile.json").read_text(encoding="utf-8"))
    assert data["profiling"]["total_records"] == 1
    assert data["provenance"]["input_file"] == str(input_path)
    assert data["licensing_status"] == "unknown"


def test_interruption_checkpoint_and_resume_are_deterministic(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text("\n".join(json.dumps({"id": i, "text": "نص {}".format(i)}) for i in range(5)) + "\n", encoding="utf-8")
    checkpoint = tmp_path / "resume.json"
    args = dict(dataset_id="owner/data", source_url="https://example.test/data", source_type="github", revision="abcdef123456", dataset_license={"status": "unknown"}, chunk_size=2, checkpoint_path=checkpoint)
    first, first_profile = profile_local_file(path, interrupted_after=3, **args)
    assert first.status == "interrupted_checkpointed"
    second, second_profile = profile_local_file(path, resume=True, **args)
    assert second_profile["total_records"] == 2
    assert second.source_records_discovered == 2
    assert second.records_accepted == 0


def test_resume_refuses_changed_input_or_configuration(tmp_path):
    path = tmp_path / "data.jsonl"
    path.write_text('{"text":"one"}\n', encoding="utf-8")
    checkpoint = tmp_path / "resume.json"
    kwargs = dict(dataset_id="owner/data", source_url="https://example.test/data", source_type="github", revision="abcdef123456", dataset_license={"status": "unknown"}, checkpoint_path=checkpoint)
    profile_local_file(path, chunk_size=1, **kwargs)
    path.write_text('{"text":"changed"}\n', encoding="utf-8")
    with pytest.raises(ResumeError, match="does not match"):
        profile_local_file(path, chunk_size=1, resume=True, **kwargs)


def test_report_collision_and_existing_project_data_are_untouched(tmp_path):
    corpus = tmp_path / "corpus.csv"
    lexicon = tmp_path / "lexicon.csv"
    corpus.write_text("untouched corpus", encoding="utf-8")
    lexicon.write_text("untouched lexicon", encoding="utf-8")
    prefix = tmp_path / "existing"
    (tmp_path / "existing.json").write_text("original report", encoding="utf-8")
    with pytest.raises(ReportOutputError):
        write_reports(ImportReport(source_id="owner/data"), prefix)
    assert corpus.read_text(encoding="utf-8") == "untouched corpus"
    assert lexicon.read_text(encoding="utf-8") == "untouched lexicon"
    assert (tmp_path / "existing.json").read_text(encoding="utf-8") == "original report"


def test_large_jsonl_stream_does_not_accumulate_staged_rows(tmp_path):
    path = tmp_path / "many.jsonl"
    path.write_text("".join(json.dumps({"id": i, "text": "text {}".format(i)}) + "\n" for i in range(2500)), encoding="utf-8")
    report, profile = profile_local_file(
        path, dataset_id="owner/data", source_url="https://example.test/data", source_type="github",
        revision="abcdef123456", dataset_license={"status": "unknown"}, chunk_size=128)
    assert profile["total_records"] == 2500
    assert report.quarantined_records == 2500
    assert report.records_accepted == 0
