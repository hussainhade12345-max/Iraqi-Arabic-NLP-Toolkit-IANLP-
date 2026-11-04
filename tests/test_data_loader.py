import pytest
import pandas as pd
import iraqi_nlp


def test_split_dataset_no_leakage():
    df = pd.DataFrame({
        "text": [f"نص رقم {i}" for i in range(50)],
        "label": ["neutral"] * 50
    })
    train_df, val_df, test_df = iraqi_nlp.split_dataset(
        df, train_ratio=0.8, val_ratio=0.1, test_ratio=0.1, random_state=42
    )

    assert len(train_df) + len(val_df) + len(test_df) == 50
    leakage = iraqi_nlp.detect_data_leakage(train_df, val_df, test_df)
    assert leakage["has_leakage"] is False


def test_sentiment_baseline():
    baseline = iraqi_nlp.SentimentBaseline()
    pos_res = baseline.predict_one("الأكل جان كلش طيب وروعة وعاشت ايدكم")
    neg_res = baseline.predict_one("الخدمة سيئة والتوصيل متأخر وما انصح احد")
    assert pos_res == "positive"
    assert neg_res == "negative"


def test_sentiment_baseline_evaluate():
    baseline = iraqi_nlp.SentimentBaseline()
    df = pd.DataFrame({
        "text": ["الأكل طيب وروعة", "الخدمة رديئة جداً"],
        "label": ["positive", "negative"]
    })
    eval_res = baseline.evaluate(df)
    assert eval_res["accuracy"] == 1.0
    assert eval_res["total"] == 2
