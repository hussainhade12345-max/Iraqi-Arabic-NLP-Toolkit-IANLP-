import pytest
import iraqi_nlp


def test_detect_codeswitch_mixed():
    text = "شنو اخبارك today يا طيب؟"
    res = iraqi_nlp.detect_codeswitch(text)
    assert res.is_mixed is True
    assert "today" in res.english_tokens
    assert "شنو" in res.arabic_tokens
    assert res.english_ratio > 0.0


def test_detect_codeswitch_pure_arabic():
    text = "هسه راح نطلع للمول"
    res = iraqi_nlp.detect_codeswitch(text)
    assert res.is_mixed is False
    assert len(res.english_tokens) == 0


def test_switch_density():
    # ar -> en -> ar -> en (high density)
    text = "شلونك bro كلش fine"
    density = iraqi_nlp.get_switch_density(text)
    assert density > 0.5


def test_empty_codeswitch():
    res = iraqi_nlp.detect_codeswitch("")
    assert res.is_mixed is False
    assert res.arabic_ratio == 0.0
    assert iraqi_nlp.get_switch_density("") == 0.0
