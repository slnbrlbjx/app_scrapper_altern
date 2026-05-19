from services.keywords import CYBER_KEYWORDS


def is_cyber_job(text: str) -> bool:
    """Return True if the text contains any cybersecurity keyword."""
    if not text:
        return False
    text_lower = text.lower()
    return any(keyword in text_lower for keyword in CYBER_KEYWORDS)
