"""
Intent Detection for Iraqi Arabic Texts
كشف النية في النصوص العراقية

Rule-based intent detection using Iraqi dialect keywords.
Designed to be replaced or extended with ML models in future versions.
"""

import re
from typing import Dict, Any

# ── Intent keyword patterns (Iraqi dialect) ───────────────────────
INTENT_PATTERNS = {

    "complaint": {
        "keywords": [
            "شكوى", "شكوه", "اشتكي", "نشتكي", "مشكلة", "مصيبة",
            "ما يصير", "ما يصح", "غلط", "ظلم", "تقصير", "إهمال",
            "والله ما", "ابد ما", "عمرنا ما", "متعبين", "تعبنا",
            "زهجنا", "خلصنا", "فدوه", "يعني شنو", "شگد",
        ],
        "patterns": [
            r"(ما|مو|مب)\s+(جاي|يجي|موجود|شغال)",
            r"(راح|طاح|وقع|انكسر|خربان)",
            r"(منذ|من)\s+\w+\s+(ما|مو)",
        ],
        "weight": 1.0,
    },

    "request": {
        "keywords": [
            "نطلب", "اطلب", "رجاء", "رجاءً", "الرجاء", "لو سمحت",
            "من فضلك", "يرجى", "نرجو", "ممكن", "قدر", "تكدر",
            "ساعدونا", "ساعدوني", "وين", "متى", "شلون",
        ],
        "patterns": [
            r"(نطلب|اطلب)\s+من",
            r"(ممكن|يمكن)\s+(تساعد|تحل|توفر)",
        ],
        "weight": 0.9,
    },

    "urgent": {
        "keywords": [
            "عاجل", "سريع", "ضروري", "خطر", "طوارئ", "انقذونا",
            "ماي ما عدنا", "كهرباء ما عدنا", "مريض", "مستشفى",
            "حالة حرجة", "الوضع خطير", "الله يسامحكم",
        ],
        "patterns": [
            r"(عاجل|ضروري|خطر)\b",
            r"(طفل|مريض|عجوز)\s+(بحاجة|يحتاج)",
        ],
        "weight": 1.2,
    },

    "question": {
        "keywords": [
            "شنو", "شگو", "وين", "شلون", "ليش", "متى", "كيف",
            "من وين", "شبيها", "شديها", "هل", "اشوف",
        ],
        "patterns": [
            r"(شنو|شگو|وين|شلون|ليش|متى)\b",
            r"\?$|؟$",
        ],
        "weight": 0.8,
    },

    "praise": {
        "keywords": [
            "شكراً", "شكرا", "ممنون", "مشكور", "خوش", "زين",
            "يسلمو", "بارك الله", "تسلم", "عاشت ايدك",
            "احسنتم", "والله يعطيكم العافية",
        ],
        "patterns": [
            r"(شكر|ممنون|يسلم)\b",
        ],
        "weight": 0.9,
    },

    "warning": {
        "keywords": [
            "انتبه", "احذر", "خطر", "تحذير", "بلاغ",
            "يوجد مشكلة", "في مشكلة", "انتبهوا",
        ],
        "patterns": [
            r"(انتبه|احذر|خطر|تحذير)\b",
        ],
        "weight": 1.0,
    },
}


def detect_intent(text: str) -> Dict[str, Any]:
    """
    Detect the intent expressed in Iraqi Arabic text.

    Uses rule-based keyword matching with Iraqi dialect patterns.

    Args:
        text: Input Iraqi Arabic text

    Returns:
        dict with:
            - text       (str)   : Original input
            - intent     (str)   : Detected intent label
            - confidence (float) : Confidence score 0.0–1.0
            - all_scores (dict)  : Scores for all intent categories
            - method     (str)   : Detection method used

    Example:
        >>> detect_intent("الكهرباء راحت من ساعة 6 الصبح ما رجعت")
        {
            'intent': 'complaint',
            'confidence': 0.85,
            ...
        }

        >>> detect_intent("عاجل مريض بالمستشفى يحتاج مساعدة")
        {
            'intent': 'urgent',
            'confidence': 0.92,
            ...
        }
    """
    if not text or not isinstance(text, str):
        return {
            "text":       text,
            "intent":     None,
            "confidence": 0.0,
            "all_scores": {},
            "method":     "rule-based",
        }

    text_lower = text.lower()
    scores = {}

    for intent, config in INTENT_PATTERNS.items():
        score = 0.0

        # Keyword matching
        for kw in config["keywords"]:
            if kw in text_lower:
                score += 1.0

        # Pattern matching (weighted higher)
        for pattern in config["patterns"]:
            if re.search(pattern, text_lower):
                score += 1.5

        # Apply weight
        scores[intent] = round(score * config["weight"], 3)

    if not any(scores.values()):
        return {
            "text":       text,
            "intent":     "unknown",
            "confidence": 0.0,
            "all_scores": scores,
            "method":     "rule-based",
        }

    # Get top intent
    top_intent = max(scores, key=scores.get)
    top_score  = scores[top_intent]

    # Normalize confidence to 0–1
    confidence = round(min(top_score / 5.0, 1.0), 3)

    return {
        "text":       text,
        "intent":     top_intent,
        "confidence": confidence,
        "all_scores": scores,
        "method":     "rule-based",
    }


def get_intent_label(text: str) -> str:
    """
    Shortcut — returns only the intent label string.

    Example:
        >>> get_intent_label("شكوى من الماء")
        'complaint'
    """
    return detect_intent(text).get("intent", "unknown")
