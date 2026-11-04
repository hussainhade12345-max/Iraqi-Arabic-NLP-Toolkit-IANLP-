import pytest
import iraqi_nlp


def test_remove_diacritics():
    text = "شُلُونِك حَبِيبِي؟"
    assert iraqi_nlp.remove_diacritics(text) == "شلونك حبيبي؟"


def test_remove_tatweel():
    text = "هسّـــــــــة"
    cleaned = iraqi_nlp.remove_tatweel(text)
    assert "ـ" not in cleaned
    assert cleaned == "هسّة"


def test_preserve_iraqi_dialect_characters_by_default():
    # Dialect characters چ گ پ ڤ must NOT be converted to ك or ب or ف by default
    text = "چانت الگاع متروسة ماي وپلاستيك"
    norm = iraqi_nlp.normalize(text)
    assert "چ" in norm
    assert "گ" in norm
    assert "پ" in norm


def test_optional_flattening_of_dialect_characters():
    text = "چانت الگاع متروسة ماي وپلاستيك"
    norm = iraqi_nlp.normalize(text, preserve_dialect_chars=False)
    assert "چ" not in norm
    assert "گ" not in norm
    assert "پ" not in norm
    assert "كانت" in norm


def test_alef_and_teh_marbuta_normalization():
    text = "أمس إجت آمال إلى المدرسة"
    norm = iraqi_nlp.normalize_arabic_chars(text)
    # Both alef variants (أ إ آ -> ا), alef maksura (ى -> ي) and teh marbuta (ة -> ه) are normalized
    assert "امس اجت امال الي المدرسه" in norm


def test_clean_repeated_chars():
    text = "هههههههه شلونكككككك !!!!"
    res = iraqi_nlp.clean_repeated_chars(text, max_repeat=2)
    assert res == "هه شلونكك !!"


def test_convert_arabic_numbers():
    text = "رقم ١٢٣٤٥"
    assert iraqi_nlp.convert_arabic_numbers(text) == "رقم 12345"


def test_is_arabic():
    assert iraqi_nlp.is_arabic("شلونك اليوم؟") is True
    assert iraqi_nlp.is_arabic("Hello world from Baghdad") is False
    assert iraqi_nlp.is_arabic("") is False


def test_clean_social_media():
    raw = "وااااي 😭 @user الكهرباء #بغداد راحت http://t.co/xyz ١٢٣"
    cleaned = iraqi_nlp.clean_social_media(raw)
    assert "@user" not in cleaned
    assert "http" not in cleaned
    assert "123" in cleaned
    assert "😭" not in cleaned


def test_tokenize():
    tokens = iraqi_nlp.tokenize("خوش سالفة هسه چانت")
    assert "خوش" in tokens
    assert "چانت" in tokens
