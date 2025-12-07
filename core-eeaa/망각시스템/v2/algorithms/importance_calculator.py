"""Importance calculator with weighted aggregation."""

from typing import Any, Dict, Optional


def _norm(value: float) -> float:
    return max(0.0, min(1.0, value))


class ImportanceCalculator:
    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            "semantic_value": 0.25,
            "business_impact": 0.25,
            "legal_retention_requirement": 0.15,
            "user_rating": 0.15,
            "collab_value": 0.1,
            "creative_potential": 0.1,
        }

    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        score = 0.0
        total_w = 0.0
        for k, w in self.weights.items():
            score += w * float(meta.get(k, 0.5))
            total_w += w
        if total_w == 0:
            return 0.5
        return _norm(score / total_w)
