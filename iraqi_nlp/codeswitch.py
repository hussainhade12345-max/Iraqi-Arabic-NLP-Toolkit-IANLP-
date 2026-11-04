"""
Code-switching detection utilities for Iraqi Arabic and English mixed text.
كشف خلط اللغات بين العربية والإنجليزية في النصوص العراقية
"""

import re
from typing import Dict, List, Any
from dataclasses import dataclass


@dataclass
class CodeSwitchResult:
    """Result of code-switching detection."""
    is_mixed: bool
    arabic_tokens: List[str]
    english_tokens: List[str]
    arabic_ratio: float
    english_ratio: float

    def to_dict(self) -> Dict[str, Any]:
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
        Input text to inspect
    threshold : float
        Minimum ratio of English tokens to consider text code-switched (default: 0.05)

    Returns:
    --------
    CodeSwitchResult
        Object containing tokens, ratios, and mixed-language flag
    """
    if not text or not isinstance(text, str):
        return CodeSwitchResult(
            is_mixed=False,
            arabic_tokens=[],
            english_tokens=[],
            arabic_ratio=0.0,
            english_ratio=0.0
        )

    # Tokenize words (Arabic script and Latin script tokens)
    tokens = re.findall(r'\b[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+\b|\b[a-zA-Z]+\b', text)

    arabic_tokens = []
    english_tokens = []

    for token in tokens:
        if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', token):
            arabic_tokens.append(token)
        elif re.search(r'[a-zA-Z]', token):
            english_tokens.append(token)

    total = len(arabic_tokens) + len(english_tokens)
    arabic_ratio = len(arabic_tokens) / total if total > 0 else 0.0
    english_ratio = len(english_tokens) / total if total > 0 else 0.0

    is_mixed = (english_ratio >= threshold) and (len(arabic_tokens) > 0)

    return CodeSwitchResult(
        is_mixed=is_mixed,
        arabic_tokens=arabic_tokens,
        english_tokens=english_tokens,
        arabic_ratio=arabic_ratio,
        english_ratio=english_ratio
    )


def get_switch_density(text: str) -> float:
    """
    Calculate transition density (number of language switches between adjacent tokens).

    Parameters:
    -----------
    text : str
        Input text

    Returns:
    --------
    float
        Ratio of language switches to total transitions (0.0 to 1.0)
    """
    if not text or not isinstance(text, str):
        return 0.0

    tokens = re.findall(r'\b[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]+\b|\b[a-zA-Z]+\b', text)
    if len(tokens) <= 1:
        return 0.0

    tags = []
    for token in tokens:
        if re.search(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', token):
            tags.append('ar')
        elif re.search(r'[a-zA-Z]', token):
            tags.append('en')

    if len(tags) <= 1:
        return 0.0

    switches = sum(1 for i in range(len(tags) - 1) if tags[i] != tags[i+1])
    return round(switches / (len(tags) - 1), 3)
