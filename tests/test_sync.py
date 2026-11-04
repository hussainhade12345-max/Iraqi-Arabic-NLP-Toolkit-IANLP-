import pytest
from pathlib import Path
import sys

# Add scripts directory to path for testing
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_to_huggingface import (
    is_excluded,
    collect_local_files_to_sync,
    sync_to_huggingface,
    ROOT,
    DEFAULT_REPO_ID,
)


def test_is_excluded_sensitive_patterns():
    # Sensitive and environment files must be excluded
    assert is_excluded(".env")[0] is True
    assert is_excluded(".env.production")[0] is True
    assert is_excluded("secret_token.txt")[0] is True
    assert is_excluded("api_credentials.json")[0] is True
    assert is_excluded("id_rsa.key")[0] is True
    assert is_excluded("cert.pem")[0] is True


def test_is_excluded_git_and_bytecode():
    assert is_excluded(".git/config")[0] is True
    assert is_excluded(".github/workflows/test.yml")[0] is True
    assert is_excluded("iraqi_nlp/__pycache__/utils.cpython-312.pyc")[0] is True
    assert is_excluded("tests/.pytest_cache/v/cache/stepwise")[0] is True
    assert is_excluded("module.pyc")[0] is True


def test_is_excluded_valid_nlp_modules():
    assert is_excluded("iraqi_nlp/__init__.py")[0] is False
    assert is_excluded("iraqi_nlp/preprocessing.py")[0] is False
    assert is_excluded("corpus/train.csv")[0] is False
    assert is_excluded("lexicon/iraqi_lexicon.csv")[0] is False
    assert is_excluded("tests/test_preprocessing.py")[0] is False
    assert is_excluded("README.md")[0] is False


def test_collect_local_files():
    files = collect_local_files_to_sync(ROOT)
    assert len(files) > 0
    rel_files = [str(f.relative_to(ROOT)) for f in files]
    # Check that core components are included
    assert "iraqi_nlp/__init__.py" in rel_files
    assert "tests/test_preprocessing.py" in rel_files
    assert "README.md" in rel_files
    # Ensure no bytecode or git files
    assert not any(f.endswith(".pyc") for f in rel_files)
    assert not any(f.startswith(".git") for f in rel_files)


def test_sync_dry_run():
    report = sync_to_huggingface(repo_id=DEFAULT_REPO_ID, dry_run=True, skip_validation=True)
    assert report["dry_run"] is True
    assert report["validation_passed"] is True
    assert len(report["added_files"]) > 0
    assert report["error"] is None
