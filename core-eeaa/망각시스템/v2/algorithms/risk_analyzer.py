"""Risk analyzer based on multiple factors."""

from typing import Any, Dict


def _norm(v: float) -> float:
    return max(0.0, min(1.0, v))


class RiskAnalyzer:
    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        recovery_cost = _norm(float(meta.get("data_recovery_cost", 0.5)))
        compliance = _norm(float(meta.get("compliance_violation_risk", 0.5)))
        bc_impact = _norm(float(meta.get("business_continuity_impact", 0.5)))
        reputation = _norm(float(meta.get("reputation_damage", 0.5)))
        legal = _norm(float(meta.get("legal_liability", 0.5)))
        irreversible_penalty = _norm(float(meta.get("irreversibility_penalty", 0.0)))

        # weights from spec: 0.25,0.25,0.20,0.15,0.10,0.05
        score = (
            0.25 * recovery_cost
            + 0.25 * compliance
            + 0.20 * bc_impact
            + 0.15 * reputation
            + 0.10 * legal
            + 0.05 * irreversible_penalty
        )
        return _norm(score)
