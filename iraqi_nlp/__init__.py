"""
Iraqi Arabic NLP Toolkit (IANLP)
القاموس العراقي ومنظومة معالجة اللغة الطبيعية

Author  : Hussein Hadeh | Al-Iraqia University, Baghdad
License : MIT (Code) | CC BY 4.0 (Data)
Version : 0.1.0
GitHub  : https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-
"""

from .preprocessing import (
    normalize,
    tokenize,
    clean_text,
    clean_social_media,
    clean_repeated_chars,
    convert_arabic_numbers,
    segment_sentences,
    remove_diacritics,
    remove_urls,
    remove_mentions,
    remove_hashtags,
    remove_emoji,
    is_arabic,
)

from .codeswitch import (
    detect_codeswitch,
    get_switch_density,
)

__version__ = "0.1.0"
__author__  = "Hussein Hadeh"
__email__   = ""
__license__ = "MIT"

__all__ = [
    # Preprocessing
    "normalize",
    "tokenize",
    "clean_text",
    "clean_social_media",
    "clean_repeated_chars",
    "convert_arabic_numbers",
    "segment_sentences",
    "remove_diacritics",
    "remove_urls",
    "remove_mentions",
    "remove_hashtags",
    "remove_emoji",
    "is_arabic",
    # Code-switching
    "detect_codeswitch",
    "get_switch_density",
]
