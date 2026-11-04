import pytest
import iraqi_nlp


def test_detect_complaint():
    text = "الكهرباء مقطوعة من أمس والمولدة خربانة وتعبنا من هذا الوضع"
    res = iraqi_nlp.detect_intent(text)
    assert res["intent"] == "complaint"
    assert res["confidence"] > 0.0


def test_detect_urgent():
    text = "عاجل جدا مريض بالمستشفى بحاجة مساعدة طارئة"
    res = iraqi_nlp.detect_intent(text)
    assert res["intent"] == "urgent"


def test_detect_question():
    text = "شنو السالفة ليش المي ماكو؟"
    label = iraqi_nlp.get_intent_label(text)
    assert label in ["question", "complaint"]


def test_detect_praise():
    text = "شكرا جزيلا وعاشت ايدك ممنون منك"
    label = iraqi_nlp.get_intent_label(text)
    assert label == "praise"
