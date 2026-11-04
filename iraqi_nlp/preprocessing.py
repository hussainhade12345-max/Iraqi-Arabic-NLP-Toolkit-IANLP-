"""
Text preprocessing utilities for Iraqi Arabic dialect.
Handles diacritics removal, character normalization, social media cleanup, and tokenization.
"""

import re
from typing import List, Optional

try:
    import regex
except ImportError:
    regex = None

from .normalizer import normalize_iraqi_text


def remove_diacritics(text: str) -> str:
    """
    Remove Arabic diacritical marks (tashkeel) and dagger alif from text.
    
    Args:
        text: Input text with diacritics
        
    Returns:
        Text without diacritics
    """
    if not isinstance(text, str):
        return ""
    return re.sub(r'[\u064B-\u065F\u0670]', '', text)


def remove_tatweel(text: str) -> str:
    """
    Remove Arabic elongation character (tatweel / kashida \u0640).

    Args:
        text: Input text

    Returns:
        Text without tatweel
    """
    if not isinstance(text, str):
        return ""
    return re.sub(r'\u0640+', '', text)


def normalize_arabic_chars(text: str, preserve_dialect_chars: bool = True) -> str:
    """
    Normalize Arabic characters for consistency while preserving dialect features.
    
    Normalizations:
    - أ إ آ ٱ → ا (alef variants to bare alef)
    - ة → ه (teh marbuta to heh)
    - ى → ي (alef maksura to yeh)
    
    Preserves Iraqi-specific letters by default:
    - چ گ پ ڤ (Kurdish/Persian origin letters common in Iraqi Arabic)
    
    Args:
        text: Input text
        preserve_dialect_chars: If True, keep Iraqi letters intact.
        
    Returns:
        Normalized text
    """
    if not isinstance(text, str):
        return ""
    return normalize_iraqi_text(
        text,
        remove_diacritics=False,
        remove_tatweel=False,
        normalize_alef=True,
        normalize_teh_marbuta=True,
        normalize_alef_maksura=True,
        preserve_dialect_chars=preserve_dialect_chars
    )


def remove_urls(text: str) -> str:
    """Remove URLs from text."""
    if not isinstance(text, str):
        return ""
    url_pattern = r'https?://\S+|www\.\S+'
    return re.sub(url_pattern, '', text)


def remove_emails(text: str) -> str:
    """Remove email addresses from text."""
    if not isinstance(text, str):
        return ""
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.sub(email_pattern, '', text)


def remove_emojis(text: str) -> str:
    """Remove emoji characters from text."""
    if not isinstance(text, str):
        return ""
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F700-\U0001F77F"  # alchemical symbols
        "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
        "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "\U0001FA00-\U0001FA6F"  # Chess Symbols
        "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "]+",
        flags=re.UNICODE
    )
    return emoji_pattern.sub(r'', text)


def remove_emoji(text: str) -> str:
    """Alias for remove_emojis."""
    return remove_emojis(text)


def remove_mentions(text: str) -> str:
    """Remove social media mentions (@username)."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'@[\w]+', '', text)


def remove_hashtags(text: str) -> str:
    """Remove hashtags symbols or hashtag tokens."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'#[\w]+', '', text)


def remove_numbers(text: str) -> str:
    """Remove Latin and Arabic digits from text."""
    if not isinstance(text, str):
        return ""
    return re.sub(r'[\d٠١٢٣٤٥٦٧٨٩]+', '', text)


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace by collapsing multiple spaces and stripping ends."""
    if not isinstance(text, str):
        return ""
    return ' '.join(text.split())


def clean_repeated_chars(text: str, max_repeat: int = 2) -> str:
    """
    Reduce repeated characters common in Iraqi social media discourse.
    هههههههه → هه | يييييي → يي | !!!!! → !!

    Args:
        text: Input text
        max_repeat: Maximum allowed consecutive repetitions (default: 2)

    Returns:
        Text with reduced repetitions
    """
    if not isinstance(text, str):
        return ""
    pattern = re.compile(r'(.)\1{' + str(max_repeat) + r',}')
    replacement = r'\1' * max_repeat
    return pattern.sub(replacement, text)


def convert_arabic_numbers(text: str) -> str:
    """
    Convert Arabic-Indic numerals to Western numerals.
    ١٢٣٤٥٦٧٨٩٠ → 1234567890
    """
    if not isinstance(text, str):
        return ""
    table = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    return text.translate(table)


def is_arabic(text: str, threshold: float = 0.5) -> bool:
    """
    Check if a string contains primarily Arabic script characters.
    
    Args:
        text: Input string
        threshold: Minimum fraction of non-whitespace letters that are Arabic script (default: 0.5)
        
    Returns:
        True if text has at least threshold proportion of Arabic characters
    """
    if not isinstance(text, str) or not text.strip():
        return False

    letters = re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z]', text)
    if not letters:
        return False

    arabic_count = sum(1 for c in letters if re.match(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]', c))
    return (arabic_count / len(letters)) >= threshold


def normalize(text: str, remove_numbers_flag: bool = False, preserve_dialect_chars: bool = True) -> str:
    """
    Comprehensive text normalization for Iraqi Arabic.
    
    Steps:
    1. Remove diacritics (tashkeel)
    2. Remove tatweel (kashida)
    3. Normalize Arabic characters (Alef, Teh Marbuta, Alef Maksura)
    4. Remove URLs and emails
    5. Remove emojis
    6. Remove mentions and hashtags
    7. Optionally remove numbers
    8. Normalize whitespace
    
    Args:
        text: Input text
        remove_numbers_flag: Whether to remove numbers
        preserve_dialect_chars: Preserve Iraqi-specific letters (چ, گ, پ, ڤ)
        
    Returns:
        Normalized text
    """
    if not isinstance(text, str):
        return ""

    text = remove_diacritics(text)
    text = remove_tatweel(text)
    text = normalize_arabic_chars(text, preserve_dialect_chars=preserve_dialect_chars)
    text = remove_urls(text)
    text = remove_emails(text)
    text = remove_emojis(text)
    text = remove_mentions(text)
    text = remove_hashtags(text)
    if remove_numbers_flag:
        text = remove_numbers(text)
    text = normalize_whitespace(text)
    return text


def clean_text(text: str, preserve_dialect_chars: bool = True) -> str:
    """Alias for normalize()."""
    return normalize(text, preserve_dialect_chars=preserve_dialect_chars)


def tokenize(text: str) -> List[str]:
    """
    Word tokenizer for Iraqi Arabic text.
    Handles Arabic letters (including Iraqi specific glyphs) and Latin words.
    """
    if not isinstance(text, str):
        return []
    text = normalize(text)
    if regex:
        return regex.findall(r'[\p{L}\p{M}]+', text)
    return re.findall(r'[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFFa-zA-Z]+', text)


def clean_social_media(text: str, preserve_dialect_chars: bool = True) -> str:
    """
    Full cleaning pipeline optimized for Iraqi social media text.
    Reduces repetitions, removes URLs/emojis/mentions, converts numerals, and normalizes.
    """
    if not isinstance(text, str):
        return ""
    text = clean_repeated_chars(text)
    text = normalize(text, preserve_dialect_chars=preserve_dialect_chars)
    text = convert_arabic_numbers(text)
    return text.strip()


def segment_sentences(text: str) -> List[str]:
    """
    Split Iraqi Arabic text into sentences on punctuation boundaries.
    """
    if not isinstance(text, str):
        return []
    sentences = re.split(r'[.؟!،؛\n]+', text)
    return [s.strip() for s in sentences if s.strip()]
