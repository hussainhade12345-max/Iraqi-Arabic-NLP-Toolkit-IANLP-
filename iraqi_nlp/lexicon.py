"""
Iraqi Dialect Lexicon and Vocabulary Manager.
إدارة القاموس والمفردات واللهجات العراقية
"""

import os
import json
import pandas as pd
from typing import Dict, List, Optional, Any, Set

from .normalizer import normalize_iraqi_text


class IraqiLexicon:
    """
    Manager for Iraqi Arabic dialect vocabulary, MSA equivalents, stopwords, and regional variations.
    """

    def __init__(self, lexicon_path: Optional[str] = None, stopwords_path: Optional[str] = None, dialect_words_path: Optional[str] = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self.lexicon_path = lexicon_path or os.path.join(base_dir, "lexicon", "iraqi_lexicon.csv")
        self.stopwords_path = stopwords_path or os.path.join(base_dir, "lexicon", "iraqi_stopwords.txt")
        self.dialect_words_path = dialect_words_path or os.path.join(base_dir, "lexicon", "dialect_words.json")

        self.df: Optional[pd.DataFrame] = None
        self.stopwords: Set[str] = set()
        self.dialect_words: List[Dict[str, Any]] = []

        self.load_all()

    def load_all(self):
        """Load lexicon CSV, stopwords TXT, and dialect words JSON if available."""
        # 1. Lexicon CSV
        if os.path.exists(self.lexicon_path):
            try:
                self.df = pd.read_csv(self.lexicon_path, encoding="utf-8")
            except Exception:
                self.df = pd.DataFrame()
        else:
            self.df = pd.DataFrame()

        # 2. Stopwords TXT
        if os.path.exists(self.stopwords_path):
            try:
                with open(self.stopwords_path, "r", encoding="utf-8") as f:
                    lines = [line.strip() for line in f if line.strip() and not line.startswith("#")]
                    self.stopwords = set(lines)
            except Exception:
                self.stopwords = set()

        # 3. Dialect words JSON
        if os.path.exists(self.dialect_words_path):
            try:
                with open(self.dialect_words_path, "r", encoding="utf-8") as f:
                    self.dialect_words = json.load(f)
            except Exception:
                self.dialect_words = []

    def lookup(self, word: str) -> Optional[Dict[str, Any]]:
        """
        Lookup an Iraqi term in the lexicon.
        Returns dictionary with details or None if not found.
        """
        if not word or self.df is None or self.df.empty:
            return None

        norm_word = normalize_iraqi_text(word)
        word_col = next((c for c in self.df.columns if c.lower() in ["word", "iraqi_term", "iraqi"]), self.df.columns[0])

        matches = self.df[self.df[word_col].astype(str).apply(normalize_iraqi_text) == norm_word]
        if not matches.empty:
            return matches.iloc[0].to_dict()

        # Check dialect_words json
        for entry in self.dialect_words:
            if normalize_iraqi_text(entry.get("word", "")) == norm_word:
                return {
                    "word": entry.get("word"),
                    "msa_equivalent": entry.get("fusha"),
                    "pos": entry.get("pos"),
                    "source": "dialect_words.json"
                }

        return None

    def is_stopword(self, word: str) -> bool:
        """Check if an Iraqi Arabic word is an identified stopword."""
        if not word:
            return False
        norm = normalize_iraqi_text(word)
        norm_stopwords = {normalize_iraqi_text(w) for w in self.stopwords}
        return norm in norm_stopwords

    def filter_by_region(self, region: str) -> List[Dict[str, Any]]:
        """Filter entries by Iraqi governorate / region."""
        if self.df is None or self.df.empty:
            return []

        gov_col = next((c for c in self.df.columns if c.lower() in ["governorate", "gov", "region"]), None)
        if not gov_col:
            return []

        matches = self.df[self.df[gov_col].astype(str).str.lower().str.contains(region.lower())]
        return matches.to_dict(orient="records")

    def get_msa_equivalent(self, word: str) -> Optional[str]:
        """Return the MSA (Fusha) translation for an Iraqi colloquial word."""
        entry = self.lookup(word)
        if entry:
            return entry.get("msa_equivalent") or entry.get("fusha")
        return None
