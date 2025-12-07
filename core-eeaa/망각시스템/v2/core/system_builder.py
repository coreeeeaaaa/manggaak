"""Convenience builder for the Intelligent Forgetting System v2."""

import json
from pathlib import Path

import yaml

from .intelligent_forgetting import IntelligentForgettingSystem
from .decision_engine import DecisionEngine
from .learning_optimizer import LearningOptimizer
from .multidimensional_analyzer import MultidimensionalAnalyzer
from .strategy_registry import build_default_registry
from .ledger import Ledger
from .storage_adapter import StorageAdapter
from ..algorithms.importance_calculator import ImportanceCalculator
from ..algorithms.usage_analyzer import UsageAnalyzer
from ..algorithms.semantic_analyzer import SemanticAnalyzer
from ..algorithms.temporal_modeler import TemporalModeler
from ..algorithms.context_analyzer import ContextAnalyzer
from ..algorithms.redundancy_analyzer import RedundancyAnalyzer


def load_config(path: Path = None) -> dict:
    default_path = Path(__file__).resolve().parents[1] / "config" / "default_policy.yaml"
    cfg_path = path or default_path
    with cfg_path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def build_system(config_path: Path = None) -> IntelligentForgettingSystem:
    cfg = load_config(config_path)
    analyzer = MultidimensionalAnalyzer(
        importance_calc=ImportanceCalculator(),
        usage_analyzer=UsageAnalyzer(),
        semantic_analyzer=SemanticAnalyzer(),
        temporal_modeler=TemporalModeler(),
        context_analyzer=ContextAnalyzer(),
        redundancy_analyzer=RedundancyAnalyzer(),
    )
    decision = DecisionEngine(
        weights=cfg.get("weights"),
        thresholds=cfg.get("thresholds"),
        class_policies=cfg.get("class_policies"),
    )
    decision.pii_protect = cfg.get("pii_protect", True)
    decision.risk_keep_threshold = cfg.get("risk_keep_threshold", 0.7)

    strategies = build_default_registry()
    optimizer = LearningOptimizer(decision_engine=decision)
    ledger_file = cfg.get("logging", {}).get("ledger_file")
    ledger = Ledger(logfile=Path(ledger_file) if ledger_file else None)
    storage = StorageAdapter()
    return IntelligentForgettingSystem(analyzer, decision, strategies, optimizer, ledger=ledger, storage_adapter=storage)
