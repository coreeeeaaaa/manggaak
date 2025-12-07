"""Lightweight summarizer: top-K frequent tokens (bag-of-words)."""

import re
from collections import Counter
from typing import List


def summarize(text: str, k: int = 20) -> str:
    tokens: List[str] = re.findall(r"[A-Za-z0-9가-힣]+", text.lower())
    if not tokens:
        return text[:200]
    freq = Counter(tokens)
    top = [w for w, _ in freq.most_common(k)]
    return " ".join(top)[:500]
