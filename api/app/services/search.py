import re
from app.config import REFERENCE_PATTERNS


def extract_search_term(question: str):
    question = question.lower()
    patterns = [
        r"onde usei (.+)",
        r"onde foi usado (.+)",
        r"onde aparece (.+)",
        r"onde está (.+)",
        r"quem usa (.+)",
        r"quem chama (.+)",
        r"em qual arquivo.*?(.+)"
    ]
    for pattern in patterns:
        match = re.search(pattern, question)
        if match:
            term = match.group(1)
            term = re.sub(r"[^\w\.]", "", term)
            return term
    return question

def is_reference_search(question: str) -> bool:
    question = question.lower()
    return any(
        pattern in question
        for pattern in REFERENCE_PATTERNS
    )