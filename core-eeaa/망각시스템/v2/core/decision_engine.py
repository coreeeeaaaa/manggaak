"""Decision engine for mapping scores and constraints to strategies."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .multidimensional_analyzer import ScoreVector


@dataclass
class StrategyPlan:
    action: str
    params: Dict[str, Any] = field(default_factory=dict)
    rationale: Optional[str] = None
    target_stage: Optional[int] = None  # v1 9-stage compatibility


class DecisionEngine:
    """Maps score vectors + meta/constraints to a StrategyPlan.

    This uses a transparent rule-based policy with safety gates. It is designed
    to be swapped out for learned or table-driven policies later.
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None,
                 thresholds: Optional[Dict[str, float]] = None,
                 class_policies: Optional[Dict[str, Dict[str, Any]]] = None):
        self.weights = weights or {
            "importance": 0.3,
            "usage": 0.25,
            "semantic": 0.2,
            "temporal": 0.15,
            "context": 0.1,
            "risk": 0.0,  # risk handled separately as keep-bias
            "redundancy": 0.0,
        }
        self.thresholds = thresholds or {
            "preserve": 0.6,
            "compress": 0.5,
            "mask": 0.35,
            "archive": 0.2,
        }
        self.risk_keep_threshold = 0.7
        self.pii_protect = True
        # Optional per-class policies: e.g., {"pii": {"action": "mask", "profile": "X+Y+T"}}
        self.class_policies = class_policies or {}

    def _aggregate(self, scores: ScoreVector, meta: Dict[str, Any]) -> float:
        score_dict = scores.to_dict()
        base = sum(self.weights[k] * score_dict.get(k, 0.0) for k in self.weights)
        redundancy = score_dict.get("redundancy", 0.0)
        risk = score_dict.get("risk", 0.0)
        # Favor keeping high risk; penalize redundancy
        adjusted = base - 0.25 * redundancy + 0.2 * risk
        return max(0.0, min(1.0, adjusted))

    def _budget_pressure(self, budget_state: Optional[Dict[str, Any]]) -> bool:
        if not budget_state:
            return False
        util = budget_state.get("utilization", {})
        storage_used = util.get("storage", 0.0)
        return storage_used >= budget_state.get("storage_budget", 1.0)

    def select(self, scores: ScoreVector, meta: Dict[str, Any],
               budget_state: Optional[Dict[str, Any]] = None,
               reversibility_state: Optional[int] = None) -> StrategyPlan:
        agg = self._aggregate(scores, meta)
        budget_pressure = self._budget_pressure(budget_state)

        # Hard stops / mandatory retention
        if meta.get("regulatory_hold"):
            return StrategyPlan(action="retain", rationale="Regulatory hold")

        if meta.get("protected_class"):
            return StrategyPlan(action="preserve", rationale="Protected class")

        # Class-based overrides
        data_class = meta.get("class")
        if data_class and data_class in self.class_policies:
            pol = self.class_policies[data_class]
            action = pol.get("action", "retain")
            params = pol.get("params", {})
            return StrategyPlan(action=action, params=params,
                                rationale=f"Class policy: {data_class}")

        # PII or high-risk data: default to preservation/masking unless approved
        if self.pii_protect and meta.get("pii"):
            if not meta.get("allow_processing"):
                return StrategyPlan(action="mask", params={"profile": meta.get("mask_profile", "X+Y")},
                                    rationale="PII protection")
            if not meta.get("approval_token"):
                return StrategyPlan(action="retain", rationale="PII processing requires approval token")

        if scores.risk >= self.risk_keep_threshold and not meta.get("allow_processing"):
            return StrategyPlan(action="preserve", rationale="High risk -> preserve")

        # Irreversible gate when already encrypted/distributed (stage >=7)
        if reversibility_state is not None and reversibility_state >= 7:
            if meta.get("allow_irreversible"):
                if not meta.get("approval_token"):
                    return StrategyPlan(action="retain", rationale="Irreversible requires approval token")
                return StrategyPlan(action="key_destroy", target_stage=9,
                                    rationale="Irreversible gate approved")
            return StrategyPlan(action="retain", rationale="Irreversible gate blocked")

        # High value → preserve or predictive cache
        if agg >= self.thresholds["preserve"]:
            return StrategyPlan(action="preserve", rationale="High composite score")

        # Mid-high → lossless compression (retain reversibility)
        if agg >= self.thresholds["compress"]:
            return StrategyPlan(action="compress", params={"lossy": False},
                                rationale="Mid score -> lossless compression")

        # Mid-low → masking/semantic preservation
        if agg >= self.thresholds["mask"]:
            # If semantic value is relatively high, preserve semantics instead of raw masking
            if scores.semantic >= 0.55 and scores.importance >= 0.45:
                return StrategyPlan(action="semantic_preserve",
                                    rationale="Semantic value high -> preserve summary")
            profile = meta.get("mask_profile", "X+Y")
            return StrategyPlan(action="mask", params={"profile": profile},
                                rationale="Low-mid score -> masking")

        # Low score: archive by default; if under budget pressure, delete
        if agg >= self.thresholds["archive"]:
            return StrategyPlan(action="archive", rationale="Very low score -> archive")

        if budget_pressure:
            return StrategyPlan(action="delete", rationale="Budget pressure -> delete")

        return StrategyPlan(action="archive", rationale="Low score but no pressure -> archive")
