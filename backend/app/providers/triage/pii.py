from __future__ import annotations

import re

PHONE = re.compile(r'(?<!\d)(?:\+?92[- ]?|0)?3\d{2}[- ]?\d{7}(?!\d)')
EMAIL = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b')
CNIC = re.compile(r'(?<!\d)\d{5}-?\d{7}-?\d(?!\d)')
HOUSE_NUMBER = re.compile(r'\b(?:house|h|flat|unit)\s*#?\s*\d+[A-Za-z-]*\b', re.I)


def redact_for_hosted_llm(text: str, location: str) -> tuple[str, str]:
    def redact(value: str) -> str:
        value = PHONE.sub('[REDACTED_PHONE]', value)
        value = EMAIL.sub('[REDACTED_EMAIL]', value)
        value = CNIC.sub('[REDACTED_CNIC]', value)
        return value

    safe_text = redact(text)
    safe_location = HOUSE_NUMBER.sub('[REDACTED_HOUSE]', redact(location))
    return safe_text, safe_location
