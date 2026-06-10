"""
Text preprocessing utilities for Iraqi Arabic dialect.
Handles diacritics removal, character normalization, and cleanup.
"""

import re
import regex
from typing import List


def remove_diacritics(text: str) -> str:
    """
    Remove Arabic diacritical marks from text.
    
    Args:
        text: Input text with diacritics
        
    Returns:
        Text without diacritics
    """
    diacritics = re.compile(r'[\u064B-\u0652]')
    return diacritics.sub('', text)


def normalize_arabic_chars(text: str) -> str:
    """
    Normalize Arabic characters for consistency.
    
    Normalizations:
    - أ إ آ → ا (alef variants to alef)
    - ة → ه (teh marbuta to heh)
    - ى → ي (alef maksura to yeh)
    
    Also handles Iraqi-specific characters:
    - چ گ پ ڤ (Kurdish/Persian origin letters)
    
    Args:
        text: Input text
        
    Returns:
        Normalized text
    """
    # Alef variants
    text = text.replace('أ', 'ا')
    text = text.replace('إ', 'ا')
    text = text.replace('آ', 'ا')
    
    # Teh marbuta to heh
    text = text.replace('ة', 'ه')
    
    # Alef maksura to yeh
    text = text.replace('ى', 'ي')
    
    return text


def remove_urls(text: str) -> str:
    """
    Remove URLs from text.
    
    Args:
        text: Input text
        
    Returns:
        Text without URLs
    """
    url_pattern = r'https?://[^\s]+'
    return re.sub(url_pattern, '', text)


def remove_emails(text: str) -> str:
    """
    Remove email addresses from text.
    
    Args:
        text: Input text
        
    Returns:
        Text without emails
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return re.sub(email_pattern, '', text)


def remove_emojis(text: str) -> str:
    """
    Remove emoji characters from text.
    
    Args:
        text: Input text
        
    Returns:
        Text without emojis
    """
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


def remove_mentions(text: str) -> str:
    """
    Remove social media mentions (@username).
    
    Args:
        text: Input text
        
    Returns:
        Text without mentions
    """
    mention_pattern = r'@[\w]+'
    return re.sub(mention_pattern, '', text)


def remove_hashtags(text: str) -> str:
    """
    Remove hashtags from text.
    
    Args:
        text: Input text
        
    Returns:
        Text without hashtags
    """
    hashtag_pattern = r'#[\w]+'
    return re.sub(hashtag_pattern, '', text)


def remove_numbers(text: str) -> str:
    """
    Remove digits from text (optional).
    
    Args:
        text: Input text
        
    Returns:
        Text without numbers
    """
    return re.sub(r'\d+', '', text)


def normalize_whitespace(text: str) -> str:
    """
    Normalize whitespace by removing extra spaces.
    
    Args:
        text: Input text
        
    Returns:
        Text with normalized whitespace
    """
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Strip leading and trailing whitespace
    text = text.strip()
    return text


def normalize(text: str, remove_numbers_flag: bool = False) -> str:
    """
    Comprehensive text normalization for Iraqi Arabic.
    
    Performs the following steps:
    1. Remove diacritics
    2. Normalize Arabic characters
    3. Remove URLs and emails
    4. Remove emojis
    5. Remove mentions and hashtags
    6. Normalize whitespace
    7. Optionally remove numbers
    
    Args:
        text: Input text to normalize
        remove_numbers_flag: Whether to remove numbers (default: False)
        
    Returns:
        Normalized text
        
    Example:
        >>> text = "هسّه شنو أخبارك؟ #سالفة @user"
        >>> normalize(text)
        'هسه شنو اخبارك'
    """
    # Remove diacritics
    text = remove_diacritics(text)
    
    # Normalize characters
    text = normalize_arabic_chars(text)
    
    # Remove URLs and emails
    text = remove_urls(text)
    text = remove_emails(text)
    
    # Remove emojis
    text = remove_emojis(text)
    
    # Remove social media markers
    text = remove_mentions(text)
    text = remove_hashtags(text)
    
    # Remove numbers if requested
    if remove_numbers_flag:
        text = remove_numbers(text)
    
    # Normalize whitespace
    text = normalize_whitespace(text)
    
    return text


def tokenize(text: str) -> List[str]:
    """
    Basic tokenizer for Iraqi Arabic text.
    Splits on whitespace and common punctuation.
    
    Args:
        text: Input text to tokenize
        
    Returns:
        List of tokens
        
    Example:
        >>> text = "خوش سالفة هسه"
        >>> tokenize(text)
        ['خوش', 'سالفة', 'هسه']
    """
    # Normalize the text first
    text = normalize(text)
    
    # Split on whitespace and punctuation
    tokens = regex.findall(r'\p{L}+', text)
    
    return tokens


def clean_text(text: str) -> str:
    """
    Alias for normalize() for backwards compatibility.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    return normalize(text)
def clean_repeated_chars(text: str, max_repeat: int = 2) -> str:
    """
    Reduce repeated characters common in Iraqi social media.
    هههههههه → هه | يييييي → يي | !!!!! → !!

    Args:
        text: Input text
        max_repeat: Maximum allowed repetitions (default: 2)

    Returns:
        Text with reduced repetitions

    Example:
        >>> clean_repeated_chars("هههههه شلونكككك")
        'هه شلونكك'
    """
    import re
    return re.sub(r'(.)\1{' + str(max_repeat) + r',}', r'\1\1', text)


def convert_arabic_numbers(text: str) -> str:
    """
    Convert Arabic-Indic numerals to Western numerals.
    ١٢٣٤٥٦٧٨٩٠ → 1234567890

    Note: Different from remove_numbers() — this converts instead of removing.

    Args:
        text: Input text

    Returns:
        Text with Western numerals

    Example:
        >>> convert_arabic_numbers("عندي ٣ أيام بس")
        'عندي 3 أيام بس'
    """
    table = str.maketrans('٠١٢٣٤٥٦٧٨٩', '0123456789')
    return text.translate(table)


def clean_social_media(text: str) -> str:
    """
    Full cleaning pipeline optimized for Iraqi social media text.
    Higher-level function that combines all preprocessing steps.

    Args:
        text: Raw social media text

    Returns:
        Cleaned text ready for NLP processing

    Example:
        >>> clean_social_media("وااااي 😭 @user الكهرباء #بغداد راحت http://t.co/x")
        'وي الكهربا راحت'
    """
    text = normalize(text)
    text = clean_repeated_chars(text)
    text = convert_arabic_numbers(text)
    return text.strip()


def segment_sentences(text: str) -> List[str]:
    """
    Split Iraqi Arabic text into sentences.
    Handles Arabic and Latin punctuation.

    Args:
        text: Input text

    Returns:
        List of sentence strings

    Example:
        >>> segment_sentences("الكهرباء راحت. ماي ما جاي. شنو السالفة؟")
        ['الكهرباء راحت', 'ماي ما جاي', 'شنو السالفة']
    """
    import re
    sentences = re.split(r'[.؟!،؛\n]+', text)
    return [s.strip() for s in sentences if s.strip()]
