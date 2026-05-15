from services.keywords import CYBER_KEYWORDS


def is_cyber_job(text: str):
    text = text.lower()

    return any(keyword in text for keyword in CYBER_KEYWORDS)