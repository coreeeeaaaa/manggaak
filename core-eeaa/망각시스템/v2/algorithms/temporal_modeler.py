"""Temporal modeler with half-life and future access adjustment."""

import math
from typing import Any, Dict


class TemporalModeler:
    def __init__(self, half_life_days: float = 30.0):
        self.half_life_days = half_life_days

    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        age_days = float(meta.get("age_days", 0.0))
        if age_days <= 0:
            return 1.0
        decay = 0.5 ** (age_days / self.half_life_days)
        future_access = float(meta.get("future_access_prob", 0.0))
        hazard = math.exp(-age_days / max(1.0, self.half_life_days))
        mixed = 0.6 * decay + 0.2 * future_access + 0.2 * hazard
        return max(0.0, min(1.0, mixed))
