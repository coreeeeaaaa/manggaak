"""Context and state holders for budgets and reversibility (thread-safe)."""

import threading
from typing import Any, Dict


class BudgetState:
    def __init__(self, storage_budget: float = 1.0, semantic_budget: float = 1.0):
        self.storage_budget = storage_budget
        self.semantic_budget = semantic_budget
        self.utilization = {"storage": 0.0, "semantic": 0.0}
        self._lock = threading.Lock()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "storage_budget": self.storage_budget,
            "semantic_budget": self.semantic_budget,
            "utilization": self.utilization,
        }

    def record_usage(self, storage_delta: float = 0.0, semantic_delta: float = 0.0) -> None:
        with self._lock:
            self.utilization["storage"] = max(0.0, self.utilization["storage"] + storage_delta)
            self.utilization["semantic"] = max(0.0, self.utilization["semantic"] + semantic_delta)


class ReversibilityState:
    def __init__(self, stage: int = 0):
        self.stage = stage  # 0~9 aligning with v1 stages
        self._lock = threading.Lock()

    def advance(self, new_stage: int) -> None:
        with self._lock:
            if new_stage > self.stage:
                self.stage = new_stage


class ContextManager:
    """Tracks budget and reversibility state across operations."""

    def __init__(self):
        self.budget_state = BudgetState()
        self.reversibility_state = ReversibilityState()

    def snapshot(self) -> Dict[str, Any]:
        return {
            "budget_state": self.budget_state.to_dict(),
            "reversibility_stage": self.reversibility_state.stage,
        }
