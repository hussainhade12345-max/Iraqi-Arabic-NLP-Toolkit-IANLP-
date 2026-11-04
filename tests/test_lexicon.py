import pytest
import iraqi_nlp


def test_lexicon_lookup():
    lex = iraqi_nlp.IraqiLexicon()
    entry = lex.lookup("لعد")
    assert entry is not None
    assert "then" in entry.get("english_translation", "").lower() or "إذن" in entry.get("msa_equivalent", "")


def test_lexicon_msa_equivalent():
    lex = iraqi_nlp.IraqiLexicon()
    msa = lex.get_msa_equivalent("باوع")
    assert msa is not None
    assert "انظر" in msa


def test_stopwords():
    lex = iraqi_nlp.IraqiLexicon()
    assert lex.is_stopword("ليش") is True
    assert lex.is_stopword("هسه") is True
    assert lex.is_stopword("كلمة_غير_موجودة") is False


def test_filter_by_region():
    lex = iraqi_nlp.IraqiLexicon()
    southern = lex.filter_by_region("Southern")
    assert isinstance(southern, list)
    assert len(southern) > 0
