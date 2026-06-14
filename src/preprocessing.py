"""
Iraqi Arabic NLP Preprocessing and Utilities Module
مجموعة أدوات معالجة اللغة الطبيعية للعربية العراقية

This module provides comprehensive text processing utilities specifically designed
for Iraqi Arabic dialect with support for normalization, code-switching detection,
and lexicon operations.
"""

import os
import re
import json
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


# ==========================================
# 1. Text Preprocessing (تنظيف وتوحيد النصوص)
# ==========================================

def normalize_iraqi_text(text: str, remove_diacritics: bool = True, 
                        normalize_alef: bool = True, 
                        normalize_ta_marbuta: bool = True) -> str:
    """
    Standardize Iraqi Arabic text by removing diacritics and unifying characters.
    
    Parameters:
    -----------
    text : str
        Input Iraqi Arabic text
    remove_diacritics : bool
        Whether to remove tashkeel (vowel marks)
    normalize_alef : bool
        Whether to normalize Alef variants (أ, إ, آ -> ا)
    normalize_ta_marbuta : bool
        Whether to normalize ta marbuta (ة -> ه)
    
    Returns:
    --------
    str
        Normalized text
        
    Example:
    --------
    >>> normalize_iraqi_text("شُلُونِك حبيبي؟")
    'شلونك حبيبي'
    """
    if not isinstance(text, str):
        return ""
    
    # Remove diacritics/tashkeel
    if remove_diacritics:
        diacritics = re.compile(r'[\u064B-\u0652]')
        text = re.sub(diacritics, '', text)
    
    # Normalize Alef variants (أ, إ, آ -> ا)
    if normalize_alef:
        text = re.sub(r'[أإآ]', 'ا', text)
    
    # Normalize ta marbuta and ha (ة -> ه)
    if normalize_ta_marbuta:
        text = re.sub(r'ة\b', 'ه', text)
    
    # Normalize alef maksura (ى -> ي)
    text = re.sub(r'ى', 'ي', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    return text.strip()


def clean_text(text: str, remove_urls: bool = True, 
               remove_mentions: bool = True, 
               remove_hashtags: bool = True,
               remove_emojis: bool = True,
               normalize: bool = True) -> str:
    """
    Comprehensive text cleaning for Iraqi Arabic social media and civic discourse.
    
    Parameters:
    -----------
    text : str
        Raw input text
    remove_urls : bool
        Remove URLs (http, https, www)
    remove_mentions : bool
        Remove @mentions
    remove_hashtags : bool
        Remove #hashtags
    remove_emojis : bool
        Remove emoji characters
    normalize : bool
        Apply normalization after cleaning
    
    Returns:
    --------
    str
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    # Remove URLs
    if remove_urls:
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)
    
    # Remove mentions (@username)
    if remove_mentions:
        text = re.sub(r'@\w+', '', text)
    
    # Remove hashtags but keep content
    if remove_hashtags:
        text = re.sub(r'#(\w+)', r'\1', text)
    
    # Remove emoji characters
    if remove_emojis:
        emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "]+", 
            flags=re.UNICODE
        )
        text = emoji_pattern.sub('', text)
    
    # Remove extra punctuation
    text = re.sub(r'([!؟.،])\1{2,}', r'\1', text)
    
    # Normalize whitespace
    text = ' '.join(text.split())
    
    if normalize:
        text = normalize_iraqi_text(text)
    
    return text.strip()


def tokenize_iraqi(text: str) -> List[str]:
    """
    Simple word tokenizer for Iraqi Arabic.
    Handles Arabic script and English words.
    
    Parameters:
    -----------
    text : str
        Input text
    
    Returns:
    --------
    List[str]
        List of tokens
        
    Example:
    --------
    >>> tokenize_iraqi("شنو أخبارك اليوم")
    ['شنو', 'أخبارك', 'اليوم']
    """
    # Split on whitespace and punctuation
    tokens = re.findall(r'\b[\u0600-\u06FF]+\b|\b[a-zA-Z]+\b|\d+', text)
    return [t for t in tokens if t]


# ==========================================
# 2. Code-Switching Detection (كشف خلط اللغات)
# ==========================================

@dataclass
class CodeSwitchResult:
    """Result of code-switching detection"""
    is_mixed: bool
    arabic_tokens: List[str]
    english_tokens: List[str]
    arabic_ratio: float
    english_ratio: float
    
    def to_dict(self) -> Dict:
        return {
            'is_mixed': self.is_mixed,
            'arabic_tokens': self.arabic_tokens,
            'english_tokens': self.english_tokens,
            'arabic_ratio': round(self.arabic_ratio, 2),
            'english_ratio': round(self.english_ratio, 2)
        }


def detect_codeswitch(text: str, threshold: float = 0.05) -> CodeSwitchResult:
    """
    Detect Arabic-English code-switching in text.
    
    Parameters:
    -----------
    text : str
        Input text
    threshold : float
        Minimum ratio to consider as code-switched (default 5%)
    
    Returns:
    --------
    CodeSwitchResult
        Code-switching analysis result
        
    Example:
    --------
    >>> detect_codeswitch("شنو أخبارك today؟")
    CodeSwitchResult(is_mixed=True, arabic_ratio=0.67, english_ratio=0.33, ...)
    """
    # Tokenize
    tokens = tokenize_iraqi(text)
    
    arabic_tokens = []
    english_tokens = []
    
    for token in tokens:
        # Check if token is Arabic
        if re.search(r'[\u0600-\u06FF]', token):
            arabic_tokens.append(token)
        # Check if token is English
        elif re.search(r'[a-zA-Z]', token):
            english_tokens.append(token)
    
    total = len(tokens)
    arabic_ratio = len(arabic_tokens) / total if total > 0 else 0
    english_ratio = len(english_tokens) / total if total > 0 else 0
    
    is_mixed = english_ratio >= threshold
    
    return CodeSwitchResult(
        is_mixed=is_mixed,
        arabic_tokens=arabic_tokens,
        english_tokens=english_tokens,
        arabic_ratio=arabic_ratio,
        english_ratio=english_ratio
    )


# ==========================================
# 3. Lexicon Management (إدارة والبحث في القاموس)
# ==========================================

class IraqiLexicon:
    """
    Iraqi Arabic Lexicon management and lookup utility.
    
    Supports:
    - Loading lexicon from CSV
    - Searching for Iraqi words
    - Looking up MSA equivalents
    - Filtering by register or region
    """
    
    def __init__(self, file_path: Optional[str] = None):
        """
        Initialize lexicon.
        
        Parameters:
        -----------
        file_path : str, optional
            Path to lexicon CSV file. If None, uses default location.
        """
        if file_path is None:
            # Default path: lexicon/iraqi_lexicon.csv
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.file_path = os.path.join(base_dir, '..', 'lexicon', 'iraqi_lexicon.csv')
        else:
            self.file_path = file_path
        
        self.lexicon_df = None
        self.load_lexicon()
    
    def load_lexicon(self) -> bool:
        """
        Load lexicon from CSV file.
        
        Returns:
        --------
        bool
            True if loaded successfully, False otherwise
        """
        try:
            if os.path.exists(self.file_path):
                self.lexicon_df = pd.read_csv(self.file_path, encoding='utf-8')
                return True
            else:
                # Create empty DataFrame with expected columns
                self.lexicon_df = pd.DataFrame(
                    columns=['iraqi_term', 'msa_equivalent', 'pos_tag', 
                            'register', 'region', 'usage_frequency',
                            'example_sentence', 'example_translation']
                )
                return False
        except Exception as e:
            print(f"Error loading lexicon: {e}")
            self.lexicon_df = pd.DataFrame()
            return False
    
    def lookup(self, word: str) -> Optional[Dict]:
        """
        Look up an Iraqi word in the lexicon.
        
        Parameters:
        -----------
        word : str
            Iraqi word to search
        
        Returns:
        --------
        Dict or None
            Dictionary with lexicon entry if found, None otherwise
            
        Example:
        --------
        >>> lexicon.lookup("شنو")
        {'iraqi_term': 'شنو', 'msa_equivalent': 'ماذا', ...}
        """
        if self.lexicon_df is None or self.lexicon_df.empty:
            return None
        
        # Normalize the search term
        normalized_word = normalize_iraqi_text(word)
        
        # Search
        result = self.lexicon_df[
            self.lexicon_df['iraqi_term'].apply(normalize_iraqi_text) == normalized_word
        ]
        
        if not result.empty:
            return result.to_dict(orient='records')[0]
        return None
    
    def search_by_msa(self, msa_word: str) -> List[Dict]:
        """
        Find Iraqi terms by MSA equivalent.
        
        Parameters:
        -----------
        msa_word : str
            MSA word to search for
        
        Returns:
        --------
        List[Dict]
            List of matching lexicon entries
        """
        if self.lexicon_df is None or self.lexicon_df.empty:
            return []
        
        normalized_msa = normalize_iraqi_text(msa_word)
        
        results = self.lexicon_df[
            self.lexicon_df['msa_equivalent'].apply(normalize_iraqi_text) == normalized_msa
        ]
        
        return results.to_dict(orient='records')
    
    def filter_by_register(self, register: str) -> List[Dict]:
        """
        Filter lexicon entries by register (colloquial, formal, slang).
        
        Parameters:
        -----------
        register : str
            Register type (colloquial, formal, slang)
        
        Returns:
        --------
        List[Dict]
            Filtered entries
        """
        if self.lexicon_df is None or self.lexicon_df.empty:
            return []
        
        results = self.lexicon_df[self.lexicon_df['register'].str.lower() == register.lower()]
        return results.to_dict(orient='records')
    
    def filter_by_region(self, region: str) -> List[Dict]:
        """
        Filter lexicon entries by geographic region.
        
        Parameters:
        -----------
        region : str
            Region (baghdad, south, north, all_regions)
        
        Returns:
        --------
        List[Dict]
            Filtered entries
        """
        if self.lexicon_df is None or self.lexicon_df.empty:
            return []
        
        results = self.lexicon_df[self.lexicon_df['region'].str.lower().str.contains(region.lower())]
        return results.to_dict(orient='records')
    
    def get_statistics(self) -> Dict:
        """
        Get lexicon statistics.
        
        Returns:
        --------
        Dict
            Statistics about the lexicon
        """
        if self.lexicon_df is None or self.lexicon_df.empty:
            return {'total_entries': 0}
        
        return {
            'total_entries': len(self.lexicon_df),
            'unique_registers': self.lexicon_df['register'].nunique(),
            'unique_regions': self.lexicon_df['region'].nunique(),
            'registers': self.lexicon_df['register'].unique().tolist() if 'register' in self.lexicon_df else [],
            'regions': self.lexicon_df['region'].unique().tolist() if 'region' in self.lexicon_df else []
        }


# ==========================================
# 4. Corpus Processing (معالجة مجموعة النصوص)
# ==========================================

class IraqiCorpus:
    """
    Iraqi Arabic Corpus loader and processor.
    """
    
    def __init__(self, corpus_dir: Optional[str] = None):
        """
        Initialize corpus.
        
        Parameters:
        -----------
        corpus_dir : str, optional
            Path to corpus directory. Defaults to ./corpus
        """
        if corpus_dir is None:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            self.corpus_dir = os.path.join(base_dir, '..', 'corpus')
        else:
            self.corpus_dir = corpus_dir
        
        self.train_df = None
        self.validation_df = None
        self.test_df = None
    
    def load_corpus(self) -> bool:
        """
        Load all corpus splits.
        
        Returns:
        --------
        bool
            True if at least one split was loaded
        """
        loaded = False
        
        # Load train set
        train_path = os.path.join(self.corpus_dir, 'train.csv')
        if os.path.exists(train_path):
            try:
                self.train_df = pd.read_csv(train_path, encoding='utf-8')
                loaded = True
            except Exception as e:
                print(f"Error loading train set: {e}")
        
        # Load validation set
        val_path = os.path.join(self.corpus_dir, 'validation.csv')
        if os.path.exists(val_path):
            try:
                self.validation_df = pd.read_csv(val_path, encoding='utf-8')
                loaded = True
            except Exception as e:
                print(f"Error loading validation set: {e}")
        
        # Load test set
        test_path = os.path.join(self.corpus_dir, 'test.csv')
        if os.path.exists(test_path):
            try:
                self.test_df = pd.read_csv(test_path, encoding='utf-8')
                loaded = True
            except Exception as e:
                print(f"Error loading test set: {e}")
        
        return loaded
    
    def get_statistics(self) -> Dict:
        """
        Get corpus statistics.
        
        Returns:
        --------
        Dict
            Corpus statistics
        """
        stats = {}
        
        if self.train_df is not None:
            stats['train'] = {
                'samples': len(self.train_df),
                'domains': self.train_df['label_primary'].nunique() if 'label_primary' in self.train_df else 0
            }
        
        if self.validation_df is not None:
            stats['validation'] = {
                'samples': len(self.validation_df),
                'domains': self.validation_df['label_primary'].nunique() if 'label_primary' in self.validation_df else 0
            }
        
        if self.test_df is not None:
            stats['test'] = {
                'samples': len(self.test_df),
                'domains': self.test_df['label_primary'].nunique() if 'label_primary' in self.test_df else 0
            }
        
        return stats


# ==========================================
# 5. Quick Testing (اختبار سريع)
# ==========================================

if __name__ == "__main__":
    print("=" * 60)
    print("Iraqi Arabic NLP Preprocessing Module")
    print("=" * 60)
    
    # Test text normalization
    print("\n1. Text Normalization:")
    sample_text = "شُلُونِك حبيبي؟ هسّة الكهربا قطعت"
    print(f"   Original:   {sample_text}")
    print(f"   Normalized: {normalize_iraqi_text(sample_text)}")
    
    # Test text cleaning
    print("\n2. Text Cleaning:")
    messy_text = "شنو أخبارك؟؟؟ Check @user #خبر https://example.com 😊"
    print(f"   Original: {messy_text}")
    print(f"   Cleaned:  {clean_text(messy_text)}")
    
    # Test tokenization
    print("\n3. Tokenization:")
    tokens = tokenize_iraqi("شنو أخبارك اليوم today؟")
    print(f"   Tokens: {tokens}")
    
    # Test code-switching detection
    print("\n4. Code-Switching Detection:")
    cs_text = "شنو أخبارك today؟"
    result = detect_codeswitch(cs_text)
    print(f"   Text: {cs_text}")
    print(f"   Result: {result.to_dict()}")
    
    # Test lexicon (if file exists)
    print("\n5. Lexicon Lookup:")
    lexicon = IraqiLexicon()
    print(f"   Lexicon loaded: {lexicon.lexicon_df is not None and not lexicon.lexicon_df.empty}")
    if lexicon.lexicon_df is not None and not lexicon.lexicon_df.empty:
        print(f"   Lexicon stats: {lexicon.get_statistics()}")
    
    print("\n" + "=" * 60)
