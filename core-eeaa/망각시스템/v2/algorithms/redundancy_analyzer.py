"""Redundancy analyzer.

Uses content token uniqueness as a cheap proxy if available; otherwise falls
back to meta hint.
"""

import re
from typing import Any, Dict


class RedundancyAnalyzer:
    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        hint = meta.get("redundancy")
        content = meta.get("content") or item.get("content") if isinstance(item, dict) else None
        if isinstance(content, str):
            tokens = re.findall(r"[A-Za-z0-9가-힣]+", content.lower())
            if not tokens:
                return float(hint or 0.0)
            uniq = len(set(tokens))
            redundancy = 1.0 - min(1.0, uniq / len(tokens))
            return redundancy
        return float(hint or 0.0)
