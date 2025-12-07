"""Usage analyzer with weighted activity features."""

from typing import Any, Dict


def _norm(value: float) -> float:
    return max(0.0, min(1.0, value))


class UsageAnalyzer:
    def __init__(self):
        self.weights = {
            "access_frequency": 0.5,
            "query_success_rate": 0.2,
            "recent_access_weight": 0.2,
            "cross_reference_count": 0.1,
        }

    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        freq = _norm(float(meta.get("access_frequency", 0.0)))
        success = _norm(float(meta.get("query_success_rate", 0.5)))
        recent = _norm(float(meta.get("recent_access_weight", 0.5)))
        cross = _norm(float(meta.get("cross_reference_count", 0.0)))
        score = (
            self.weights["access_frequency"] * freq
            + self.weights["query_success_rate"] * success
            + self.weights["recent_access_weight"] * recent
            + self.weights["cross_reference_count"] * cross
        )
        return _norm(score)
