"""Semantic analyzer with weighted factors."""

from typing import Any, Dict


def _norm(value: float) -> float:
    return max(0.0, min(1.0, value))


class SemanticAnalyzer:
    def __init__(self):
        self.weights = {
            "concept_hierarchy_depth": 0.2,
            "domain_criticality": 0.25,
            "reasoning_chain_value": 0.2,
            "innovation_potential": 0.2,
            "educational_value": 0.15,
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
