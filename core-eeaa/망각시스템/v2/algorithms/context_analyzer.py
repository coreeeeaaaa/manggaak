"""Context analyzer with weighted factors."""

from typing import Any, Dict


def _norm(value: float) -> float:
    return max(0.0, min(1.0, value))


class ContextAnalyzer:
    def __init__(self):
        self.weights = {
            "user_role_importance": 0.25,
            "project_dependency": 0.25,
            "network_centrality": 0.2,
            "urgency_factor": 0.2,
            "resource_availability": 0.1,
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
