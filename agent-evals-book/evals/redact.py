"""Redaction step for production traces before they become eval cases (Chapter 19)."""
import re

PATTERNS = {                                # order matters: cards first
    "CARD": r"\b\d(?:[ -]?\d){12,15}\b",
    "EMAIL": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "PHONE": r"\+?\d[\d ().-]{7,}\d",
    "CUSTOMER": r"\bC-\d{4}\b",
}


def redact(text):
    """Swap personal data for typed placeholders, numbered per value,
    so graders can still tell two different customers apart."""
    seen = {}
    for label, pattern in PATTERNS.items():
        def tag(m, label=label):
            key = (label, m.group(0))
            if key not in seen:
                n = 1 + sum(k[0] == label for k in seen)
                seen[key] = f"<{label}_{n}>"
            return seen[key]
        text = re.sub(pattern, tag, text)
    return text

