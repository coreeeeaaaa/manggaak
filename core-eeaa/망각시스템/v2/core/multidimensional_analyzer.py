"""Axis-wise scoring and aggregation for Intelligent Forgetting System v2.

This module wires individual axis calculators (importance, usage, semantic,
temporal, context, risk, redundancy) into a normalized ScoreVector.
"""

from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class ScoreVector:
    importance: float
    usage: float
    semantic: float
    temporal: float
    context: float
    risk: float
    redundancy: float

    def to_dict(self) -> Dict[str, float]:
        return {
            "importance": self.importance,
            "usage": self.usage,
            "semantic": self.semantic,
            "temporal": self.temporal,
            "context": self.context,
            "risk": self.risk,
            "redundancy": self.redundancy,
        }


def _clip01(value: float) -> float:
    return max(0.0, min(1.0, value))


class MultidimensionalAnalyzer:
    """Composes axis calculators into a normalized ScoreVector."""

    def __init__(self, *, importance_calc, usage_analyzer, semantic_analyzer,
                 temporal_modeler, context_analyzer, redundancy_analyzer):
        self.importance_calc = importance_calc
        self.usage_analyzer = usage_analyzer
        self.semantic_analyzer = semantic_analyzer
        self.temporal_modeler = temporal_modeler
        self.context_analyzer = context_analyzer
        self.redundancy_analyzer = redundancy_analyzer

    def analyze(self, item: Any, meta: Dict[str, Any]) -> ScoreVector:
        """Return a ScoreVector in [0,1]^7 for the given item.

        Each calculator should already apply its own normalization; we clip as a
        safety net to keep scores within bounds.
        """

        return ScoreVector(
            importance=_clip01(self.importance_calc.compute(item, meta)),
            usage=_clip01(self.usage_analyzer.compute(item, meta)),
            semantic=_clip01(self.semantic_analyzer.compute(item, meta)),
            temporal=_clip01(self.temporal_modeler.compute(item, meta)),
            context=_clip01(self.context_analyzer.compute(item, meta)),
            risk=_clip01(meta.get("risk", 0.0)),
            redundancy=_clip01(self.redundancy_analyzer.compute(item, meta)),
        )
