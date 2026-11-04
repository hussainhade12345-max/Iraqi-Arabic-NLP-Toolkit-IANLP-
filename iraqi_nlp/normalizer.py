"""
Dialect-aware text normalization for Iraqi Arabic.
توحيد النصوص مع الحفاظ على الهوية اللهجية العراقية
"""

import re
from typing import Optional


def normalize_iraqi_text(
    text: str,
    remove_diacritics: bool = True,
    remove_tatweel: bool = True,
    normalize_alef: bool = True,
    normalize_teh_marbuta: bool = True,
    normalize_alef_maksura: bool = True,
    preserve_dialect_chars: bool = True
) -> str:
    """
    Standardize Iraqi Arabic text while protecting dialectal identity.

    Important: Dialect-distinctive characters (چ, گ, پ, ڤ) are preserved by default!
    Aggressive flattening to (ك, ب, ف) damages Iraqi dialect identification and
    must only happen if preserve_dialect_chars is explicitly set to False.

    Parameters:
    -----------
    text : str
        Input Iraqi Arabic text.
    remove_diacritics : bool
        Whether to strip tashkeel (fatha, damma, kasra, sukun, shadda, tanween).
    remove_tatweel : bool
        Whether to strip kashida/tatweel (\u0640).
    normalize_alef : bool
        Whether to map [إأآٱ] -> ا.
    normalize_teh_marbuta : bool
        Whether to map ة -> ه.
    normalize_alef_maksura : bool
        Whether to map ى -> ي.
    preserve_dialect_chars : bool
        If True, preserves Iraqi letters (چ, گ, پ, ڤ). If False, flattens them to MSA equivalents.

    Returns:
    --------
    str
        Normalized text.
    """
    if not isinstance(text, str):
        return ""

    # Remove tashkeel/diacritics (\u064B-\u065F, \u0670 dagger alif)
    if remove_diacritics:
        text = re.sub(r'[\u064B-\u065F\u0670]', '', text)

    # Remove tatweel / kashida (\u0640)
    if remove_tatweel:
        text = re.sub(r'\u0640', '', text)

    # Normalize Alef variants
    if normalize_alef:
        text = re.sub(r'[إأآٱ]', 'ا', text)

    # Normalize Teh Marbuta
    if normalize_teh_marbuta:
        text = re.sub(r'ة\b', 'ه', text)
        text = text.replace('ة', 'ه')

    # Normalize Alef Maksura
    if normalize_alef_maksura:
        text = text.replace('ى', 'ي')

    # Optional flattening of Iraqi dialect characters (default: keep them intact!)
    if not preserve_dialect_chars:
        text = text.replace('پ', 'ب')
        text = text.replace('چ', 'ك')
        text = text.replace('گ', 'ك')
        text = text.replace('ڤ', 'ف')

    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
