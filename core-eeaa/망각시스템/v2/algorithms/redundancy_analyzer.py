"""Redundancy analyzer with hash/semantic/entropy cues."""

import re
import hashlib
import math
from typing import Any, Dict

from v2.utils.summarizer import _tokens, lsh_signature


def _entropy(text: str) -> float:
    tokens = _tokens(text)
    if not tokens:
        return 0.0
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    total = len(tokens)
    ent = 0.0
    for c in freq.values():
        p = c / total
        ent -= p * math.log2(p)
    # Normalize by log2(V)
    norm = ent / math.log2(len(freq) + 1)
    return min(1.0, max(0.0, norm))


class RedundancyAnalyzer:
    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        hint = meta.get("redundancy")
        content = meta.get("content") or item.get("content") if isinstance(item, dict) else None
        if isinstance(content, str):
            tokens = _tokens(content)
            if not tokens:
                return float(hint or 0.0)
            uniq_ratio = min(1.0, len(set(tokens)) / len(tokens))
            token_redundancy = 1.0 - uniq_ratio
            ent = _entropy(content)
            # Use LSH signature hash length as semantic cue (shorter overlap => higher redundancy)
            sig = lsh_signature(tokens)
            sig_hash = hashlib.sha256("".join(sig).encode()).hexdigest()
            semantic_redundancy = 0.5 if sig_hash else 0.0
            score = 0.4 * token_redundancy + 0.2 * (1 - ent) + 0.4 * semantic_redundancy
            return max(0.0, min(1.0, score))
        return float(hint or 0.0)
