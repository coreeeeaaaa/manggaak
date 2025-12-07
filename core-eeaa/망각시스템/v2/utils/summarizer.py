"""Lightweight summarizer and deduplicator (TF-IDF + LSH-like hashing)."""

import re
import math
import hashlib
from collections import Counter
from typing import List, Tuple


def _tokens(text: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9가-힣]+", text.lower())


def summarize(text: str, k: int = 20) -> str:
    tokens = _tokens(text)
    if not tokens:
        return text[:200]
    freq = Counter(tokens)
    top = [w for w, _ in freq.most_common(k)]
    return " ".join(top)[:500]


def tfidf_score(doc_tokens: List[str], corpus_df: Counter, corpus_size: int) -> Counter:
    tf = Counter(doc_tokens)
    scores = Counter()
    for term, f in tf.items():
        df = corpus_df.get(term, 1)
        idf = math.log((1 + corpus_size) / (1 + df)) + 1
        scores[term] = f * idf
    return scores


def lsh_signature(tokens: List[str], bands: int = 4, rows: int = 4) -> Tuple[str, ...]:
    # Simple hash buckets from token sets; not a full MinHash but lightweight.
    sig = []
    chunk = max(1, len(tokens) // (bands * rows))
    for b in range(bands):
        slice_tokens = tokens[b * chunk : (b + 1) * chunk] or tokens
        h = hashlib.sha256(" ".join(sorted(set(slice_tokens))).encode()).hexdigest()
        sig.append(h[:8])
    return tuple(sig)
