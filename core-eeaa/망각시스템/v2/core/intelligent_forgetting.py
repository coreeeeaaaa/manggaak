"""Orchestrator wiring analyzer, decision engine, strategies, and learning."""

from typing import Any, Dict, Optional

from .context_manager import ContextManager
from .decision_engine import DecisionEngine, StrategyPlan
from .learning_optimizer import LearningOptimizer
from .multidimensional_analyzer import MultidimensionalAnalyzer
from .multidimensional_analyzer import ScoreVector
from .ledger import Ledger
from .storage_adapter import StorageAdapter


class IntelligentForgettingSystem:
    def __init__(self, analyzer: MultidimensionalAnalyzer,
                 decision_engine: DecisionEngine,
                 strategy_registry: Dict[str, Any],
                 learning_optimizer: LearningOptimizer,
                 context_manager: Optional[ContextManager] = None,
                 ledger: Optional[Ledger] = None,
                 storage_adapter: Optional[StorageAdapter] = None):
        self.analyzer = analyzer
        self.decision_engine = decision_engine
        self.strategy_registry = strategy_registry
        self.learning_optimizer = learning_optimizer
        self.context_manager = context_manager or ContextManager()
        self.ledger = ledger or Ledger()
        self.storage = storage_adapter or StorageAdapter()

    def process_item(self, item: Any, meta: Dict[str, Any]) -> Dict[str, Any]:
        scores: ScoreVector = self.analyzer.analyze(item, meta)
        ctx_snapshot = self.context_manager.snapshot()
        plan: StrategyPlan = self.decision_engine.select(
            scores,
            meta,
            budget_state=ctx_snapshot.get("budget_state"),
            reversibility_state=ctx_snapshot.get("reversibility_stage"),
        )

        strategy = self.strategy_registry.get(plan.action)
        if strategy is None:
            raise ValueError(f"Unknown strategy: {plan.action}")

        result = strategy.apply(item=item, meta=meta, plan=plan, scores=scores,
                                context=self.context_manager)
        self.learning_optimizer.update(result.get("feedback", {}))

        # Track budget deltas heuristically based on meta size hint
        size = float(meta.get("size_bytes", 1.0))
        if plan.action in {"delete", "key_destroy"}:
            self.context_manager.budget_state.record_usage(storage_delta=-size)
        elif plan.action in {"compress", "mask", "archive", "semantic_preserve"}:
            self.context_manager.budget_state.record_usage(storage_delta=-0.5 * size)
        else:
            self.context_manager.budget_state.record_usage(storage_delta=0.0)

        record = {
            "scores": scores.to_dict(),
            "plan": plan,
            "result": result,
            "context": ctx_snapshot,
            "meta": {k: meta.get(k) for k in meta if k not in {"content", "payload"}},
            "policy": {
                "thresholds": self.decision_engine.thresholds,
                "class_policies": getattr(self.decision_engine, "class_policies", {}),
            },
            "constraints": {
                "regulatory_hold": meta.get("regulatory_hold", False),
                "protected_class": meta.get("protected_class", False),
                "pii": meta.get("pii", False),
                "allow_irreversible": meta.get("allow_irreversible", False),
                "approval_token": bool(meta.get("approval_token")),
            },
        }
        self.ledger.log(record)
        return record
