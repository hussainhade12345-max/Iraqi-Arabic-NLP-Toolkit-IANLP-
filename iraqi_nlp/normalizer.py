import re

def normalize_iraqi_text(text):
    text = re.sub(r'[إأآا]', 'ا', text)
    text = re.sub(r'پ', 'ب', text)
    text = re.sub(r'چ', 'ك', text)
    text = re.sub(r'گ', 'ك', text)
    return text.strip()
