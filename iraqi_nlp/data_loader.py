"""
Data loading, splitting, and baseline evaluation utilities for IANLP.
تحميل البيانات وتقسيمها ونماذج التقييم الأساسية
"""

import os
import json
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Any, Union

from .normalizer import normalize_iraqi_text


def load_corpus_splits(corpus_dir: Optional[str] = None) -> Dict[str, pd.DataFrame]:
    """
    Load train, validation, and test CSV splits from the corpus directory.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    corpus_dir = corpus_dir or os.path.join(base_dir, "corpus")

    splits = {}
    for name in ["train", "validation", "test"]:
        path = os.path.join(corpus_dir, f"{name}.csv")
        if os.path.exists(path):
            try:
                splits[name] = pd.read_csv(path, encoding="utf-8")
            except Exception:
                splits[name] = pd.DataFrame()
        else:
            splits[name] = pd.DataFrame()

    return splits


def load_sentiment_dataset(path: Optional[str] = None) -> pd.DataFrame:
    """Load sentiment dataset CSV."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    path = path or os.path.join(base_dir, "data", "sentiment_dataset.csv")

    if os.path.exists(path):
        return pd.read_csv(path, encoding="utf-8")
    return pd.DataFrame()


def split_dataset(
    df: pd.DataFrame,
    train_ratio: float = 0.8,
    val_ratio: float = 0.1,
    test_ratio: float = 0.1,
    random_state: int = 42,
    stratify_col: Optional[str] = None,
    deduplicate_by_text: bool = True,
    text_col: str = "text"
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split a dataset into train, validation, and test sets reproducibly.
    Guarantees no duplicate text leakage across splits.

    Parameters:
    -----------
    df : pd.DataFrame
        Input data
    train_ratio : float
        Proportion for training set (e.g. 0.8)
    val_ratio : float
        Proportion for validation set (e.g. 0.1)
    test_ratio : float
        Proportion for test set (e.g. 0.1)
    random_state : int
        Seed for reproducibility
    stratify_col : Optional[str]
        Column name to stratify splits by
    deduplicate_by_text : bool
        If True, drops duplicate texts before splitting to eliminate split leakage
    text_col : str
        Column name for text

    Returns:
    --------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        (train_df, val_df, test_df)
    """
    if df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    total = train_ratio + val_ratio + test_ratio
    train_ratio /= total
    val_ratio /= total
    test_ratio /= total

    work_df = df.copy()

    # Deduplicate by normalized text to prevent data leakage
    if deduplicate_by_text and text_col in work_df.columns:
        norm_key = work_df[text_col].dropna().astype(str).apply(normalize_iraqi_text)
        work_df = work_df.loc[~norm_key.duplicated()].copy()

    # Reproducible shuffle
    shuffled_df = work_df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    n = len(shuffled_df)
    train_end = int(round(n * train_ratio))
    val_end = train_end + int(round(n * val_ratio))

    train_df = shuffled_df.iloc[:train_end].copy().reset_index(drop=True)
    val_df = shuffled_df.iloc[train_end:val_end].copy().reset_index(drop=True)
    test_df = shuffled_df.iloc[val_end:].copy().reset_index(drop=True)

    return train_df, val_df, test_df


class SentimentBaseline:
    """
    Lexicon and rule-based baseline classifier for Iraqi Arabic sentiment analysis.
    """

    POSITIVE_WORDS = {
        "طيب", "حلو", "يخبل", "روعة", "ممتاز", "مبدع", "راقي", "عاشت",
        "تسلم", "ممنون", "مشكور", "مناسبة", "نظيف", "يوفقكم", "خير"
    }
    NEGATIVE_WORDS = {
        "سيئة", "رديئة", "متأخر", "مكسورة", "تالفة", "يقطع", "يعلق",
        "تأخير", "خراب", "خربان", "ما يسوى", "مو زين", "ظلم", "تقصير"
    }

    def predict_one(self, text: str) -> str:
        """Predict sentiment label ('positive', 'negative', 'neutral') for a single text."""
        if not text or not isinstance(text, str):
            return "neutral"

        norm = normalize_iraqi_text(text)
        words = set(norm.split())

        pos_count = len(words & {normalize_iraqi_text(w) for w in self.POSITIVE_WORDS})
        neg_count = len(words & {normalize_iraqi_text(w) for w in self.NEGATIVE_WORDS})

        # Negation check
        if any(neg_particle in norm for neg_particle in ["ما انصح", "ما يسوى", "مو نفس", "ما دا اسمع"]):
            neg_count += 2

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        return "neutral"

    def predict(self, texts: List[str]) -> List[str]:
        return [self.predict_one(t) for t in texts]

    def evaluate(self, df: pd.DataFrame, text_col: str = "text", label_col: str = "label") -> Dict[str, float]:
        """Evaluate baseline accuracy on a test DataFrame."""
        if df.empty or text_col not in df.columns or label_col not in df.columns:
            return {"accuracy": 0.0, "total": 0}

        preds = self.predict(df[text_col].tolist())
        actuals = df[label_col].tolist()

        correct = sum(1 for p, a in zip(preds, actuals) if str(p).lower() == str(a).lower())
        total = len(actuals)
        acc = round(correct / total, 4) if total > 0 else 0.0

        return {"accuracy": acc, "total": total, "correct": correct}
