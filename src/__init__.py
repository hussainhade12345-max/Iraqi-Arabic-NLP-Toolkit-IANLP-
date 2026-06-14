"""
src/__init__.py - Iraqi Arabic NLP Toolkit Package Initialization

This module initializes the IANLP package and exposes key utilities for easy import.
"""

from .preprocessing import (
    normalize_iraqi_text,
    clean_text,
    tokenize_iraqi,
    detect_codeswitch,
    CodeSwitchResult,
    IraqiLexicon,
    IraqiCorpus
)

__version__ = "0.9.0"
__author__ = "Hussein Hadeh"
__email__ = "hussainhade12345@gmail.com"
__license__ = "MIT (code) / CC BY 4.0 (data)"

__all__ = [
    "normalize_iraqi_text",
    "clean_text",
    "tokenize_iraqi",
    "detect_codeswitch",
    "CodeSwitchResult",
    "IraqiLexicon",
    "IraqiCorpus"
]

def get_version():
    """Return IANLP version."""
    return __version__

def info():
    """Print IANLP package information."""
    print(f"""
    Iraqi Arabic NLP Toolkit (IANLP)
    Version: {__version__}
    Author: {__author__}
    Email: {__email__}
    License: {__license__}
    
    Repository: https://github.com/hussainhade12345-max/Iraqi-Arabic-NLP-Toolkit-IANLP-
    """)
