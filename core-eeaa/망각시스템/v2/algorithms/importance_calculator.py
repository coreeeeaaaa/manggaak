"""Importance calculator stub.

Intended to combine semantic value, business impact, legal retention, user
rating, collaborative value, creative potential into a normalized score.
"""

from typing import Any, Dict


def _norm(value: float) -> float:
    return max(0.0, min(1.0, value))


class ImportanceCalculator:
    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        # Combine weighted hints; default mid value.
        factors = [
            meta.get("semantic_value", 0.5),
            meta.get("business_impact", 0.5),
            meta.get("legal_retention_requirement", 0.5),
            meta.get("user_rating", 0.5),
            meta.get("collab_value", 0.5),
            meta.get("creative_potential", 0.5),
        ]
        if not factors:
            return 0.5
        avg = sum(float(f) for f in factors) / len(factors)
        return _norm(avg)
