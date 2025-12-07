"""Adaptive threshold tuning stub."""

from typing import Any, Dict


class AdaptiveThreshold:
    def apply(self, item: Any, meta: Dict[str, Any], plan: Any, scores: Any, context: Any) -> Dict[str, Any]:
        return {
            "status": "noop",
            "feedback": {"type": "threshold_adjust"},
        }
