"""Online optimizer for weights/thresholds/strategy probabilities."""

from typing import Any, Dict


class LearningOptimizer:
    """Lightweight bandit-style updater with safety caps.

    Tracks feedback events and nudges weights/thresholds within bounded ranges.
    This is deliberately simple and transparent; can be replaced by full BO.
    """

    def __init__(self, decision_engine=None):
        self.metrics: Dict[str, float] = {}
        self.decision_engine = decision_engine

    def update(self, feedback_event: Dict[str, Any]) -> None:
        event_type = feedback_event.get("type")
        if not event_type or not self.decision_engine:
            return

        # Simple rules: if we see false positive deletion, raise thresholds; if
        # unnecessary retention, lower thresholds.
        thr = self.decision_engine.thresholds
        if event_type == "false_positive_delete":
            thr["archive"] = min(0.4, thr.get("archive", 0.2) + 0.05)
            thr["mask"] = min(0.5, thr.get("mask", 0.35) + 0.05)
        elif event_type == "unnecessary_retain":
            thr["archive"] = max(0.1, thr.get("archive", 0.2) - 0.05)
            thr["mask"] = max(0.25, thr.get("mask", 0.35) - 0.05)

        self.metrics["last_event"] = event_type
