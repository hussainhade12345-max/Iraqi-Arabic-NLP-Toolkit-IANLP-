import pytest
import pandas as pd
import iraqi_nlp


def test_validate_valid_dataframe():
    df = pd.DataFrame({
        "text": ["المي مقطوع", "الكهرباء انطفت"],
        "label": ["infrastructure", "infrastructure"]
    })
    rep = iraqi_nlp.validate_dataframe_schema(df, required_columns=["text", "label"])
    assert rep.is_valid is True
    assert rep.null_text_count == 0
    assert rep.duplicate_exact_count == 0


def test_validate_missing_columns():
    df = pd.DataFrame({"some_col": [1, 2]})
    rep = iraqi_nlp.validate_dataframe_schema(df, required_columns=["text", "label"])
    assert rep.is_valid is False
    assert "text" in rep.missing_fields


def test_validate_duplicates_and_nulls():
    df = pd.DataFrame({
        "text": ["هسه الكهرباء راحت", "هسه الكهرباء راحت", None, "   "],
        "label": ["infrastructure", "infrastructure", "infrastructure", "infrastructure"]
    })
    rep = iraqi_nlp.validate_dataframe_schema(df)
    assert rep.null_text_count == 1
    assert rep.empty_text_count == 1
    assert rep.duplicate_exact_count >= 1


def test_data_leakage_detection():
    train_df = pd.DataFrame({"text": ["الكهرباء راحت", "المي مقطوع"]})
    val_df = pd.DataFrame({"text": ["الكهرباء راحت", "الطريق مسدود"]})
    test_df = pd.DataFrame({"text": ["المستشفى بعيدة"]})

    res = iraqi_nlp.detect_data_leakage(train_df, val_df, test_df)
    assert res["has_leakage"] is True
    assert res["train_val_overlap_count"] == 1
    assert res["train_test_overlap_count"] == 0
