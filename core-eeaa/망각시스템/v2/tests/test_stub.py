import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from v2.algorithms.context_analyzer import ContextAnalyzer
from v2.algorithms.importance_calculator import ImportanceCalculator
from v2.algorithms.redundancy_analyzer import RedundancyAnalyzer
from v2.algorithms.semantic_analyzer import SemanticAnalyzer
from v2.algorithms.temporal_modeler import TemporalModeler
from v2.algorithms.usage_analyzer import UsageAnalyzer
from v2.algorithms.risk_analyzer import RiskAnalyzer
from v2.core.decision_engine import DecisionEngine
from v2.core.intelligent_forgetting import IntelligentForgettingSystem
from v2.core.learning_optimizer import LearningOptimizer
from v2.core.multidimensional_analyzer import MultidimensionalAnalyzer
from v2.core.strategy_registry import build_default_registry
from v2.core.batch_processor import process_batch
from v2.core.parallel_batch import process_batch_parallel
from v2.core.ledger import Ledger
from v2.core.system_builder import load_config
from v2.core.work_queue import WorkQueue


def _build_system():
    analyzer = MultidimensionalAnalyzer(
        importance_calc=ImportanceCalculator(),
        usage_analyzer=UsageAnalyzer(),
        semantic_analyzer=SemanticAnalyzer(),
        temporal_modeler=TemporalModeler(),
        context_analyzer=ContextAnalyzer(),
        redundancy_analyzer=RedundancyAnalyzer(),
        risk_analyzer=RiskAnalyzer(),
    )
    cfg = load_config()
    decision = DecisionEngine(
        weights=cfg.get("weights"), thresholds=cfg.get("thresholds"), class_policies=cfg.get("class_policies")
    )
    strategies = build_default_registry()
    optimizer = LearningOptimizer(decision_engine=decision)
    ledger = Ledger()
    return IntelligentForgettingSystem(analyzer, decision, strategies, optimizer, ledger=ledger)


class TestDecisionFlow(unittest.TestCase):
    def test_high_value_preserved(self):
        sys = _build_system()
        meta = {
            "semantic_value": 0.9,
            "business_impact": 0.9,
            "importance": 0.9,
            "access_frequency": 0.9,
        }
        result = sys.process_item(item={"id": 1}, meta=meta)
        self.assertEqual(result["plan"].action, "preserve")

    def test_low_value_archived_or_deleted_under_budget_pressure(self):
        sys = _build_system()
        sys.context_manager.budget_state.record_usage(storage_delta=2.0)
        meta = {
            "semantic_value": 0.0,
            "business_impact": 0.0,
            "legal_retention_requirement": 0.0,
            "user_rating": 0.0,
            "collab_value": 0.0,
            "creative_potential": 0.0,
            "access_frequency": 0.0,
            "query_success_rate": 0.0,
            "recent_access_weight": 0.0,
            "cross_reference_count": 0.0,
            "age_days": 999,
            "context": 0.0,
            "redundancy": 1.0,
        }
        result = sys.process_item(item={"id": 2}, meta=meta)
        self.assertIn(result["plan"].action, {"archive", "delete"})

    def test_irreversible_gate_blocks_without_approval(self):
        sys = _build_system()
        sys.context_manager.reversibility_state.advance(7)
        meta = {"importance": 0.1}
        result = sys.process_item(item={"id": 3}, meta=meta)
        self.assertEqual(result["plan"].action, "retain")

    def test_batch_low_score_first(self):
        sys = _build_system()
        items = [
            ({"id": 1}, {"semantic_value": 0.9, "business_impact": 0.9, "access_frequency": 0.8}),
            ({"id": 2}, {"semantic_value": 0.1, "business_impact": 0.0, "access_frequency": 0.0, "redundancy": 1.0}),
        ]
        results = process_batch(sys, items)
        # Expect low-score item processed first -> budget utilization reduced
        actions = [r["plan"].action for r in results]
        self.assertIn(actions[0], {"archive", "delete", "mask"})

    def test_pii_class_policy_masks(self):
        sys = _build_system()
        meta = {
            "class": "pii",
            "pii": True,
            "content": "My SSN is 123-45-6789",
        }
        result = sys.process_item(item={"id": 5}, meta=meta)
        self.assertEqual(result["plan"].action, "mask")

    def test_parallel_batch(self):
        sys = _build_system()
        items = [
            ({"id": i}, {"id": i, "semantic_value": 0.5, "business_impact": 0.4}) for i in range(5)
        ]
        results = process_batch_parallel(sys, items, max_workers=2)
        self.assertEqual(len(results), len(items))

    def test_reversibility_progress(self):
        sys = _build_system()
        meta = {"content": "data", "semantic_value": 0.4, "business_impact": 0.3}
        res = sys.process_item(item={"id": 10}, meta=meta)
        self.assertGreaterEqual(sys.context_manager.reversibility_state.stage, 0)
        # simulate irreversible with approval
        sys.context_manager.reversibility_state.advance(7)
        meta2 = {"allow_irreversible": True, "size_bytes": 100, "approval_token": "ok"}
        res2 = sys.process_item(item={"id": 11}, meta=meta2)
        self.assertEqual(sys.context_manager.reversibility_state.stage, 9)

    def test_work_queue_processes(self):
        sys = _build_system()
        wq = WorkQueue(sys, workers=2)
        wq.start()
        results = []
        wq.submit({"id": 20}, {"content": "pii", "class": "pii", "pii": True}, callback=lambda r: results.append(r))
        wq.q.join()
        wq.stop()
        self.assertTrue(results)


if __name__ == "__main__":
    unittest.main()
