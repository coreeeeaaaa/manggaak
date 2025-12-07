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
from .metrics import Metrics
from ..algorithms.importance_calculator import ImportanceCalculator
from ..algorithms.usage_analyzer import UsageAnalyzer
from ..algorithms.semantic_analyzer import SemanticAnalyzer
from ..algorithms.temporal_modeler import TemporalModeler
from ..algorithms.context_analyzer import ContextAnalyzer
from ..algorithms.redundancy_analyzer import RedundancyAnalyzer
from ..storage.local_fs_adapter import LocalFSAdapter


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
    storage_backend = cfg.get("storage", {}).get("backend", "memory")
    if storage_backend == "local_fs":
        root = Path(cfg.get("storage", {}).get("root", ".data"))
        storage = LocalFSAdapter(root=root)
    else:
        storage = StorageAdapter()
    metrics = Metrics()
    return IntelligentForgettingSystem(analyzer, decision, strategies, optimizer, ledger=ledger, storage_adapter=storage, metrics=metrics)


def reload_config(system, config_path: Path = None) -> None:
    cfg = load_config(config_path)
    system.decision_engine.thresholds = cfg.get("thresholds", system.decision_engine.thresholds)
    system.decision_engine.weights = cfg.get("weights", system.decision_engine.weights)
    system.decision_engine.class_policies = cfg.get("class_policies", getattr(system.decision_engine, "class_policies", {}))
