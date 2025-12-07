"""Batch processor for prioritised forgetting decisions.

Processes items with priority ordering so that low-value items are handled
first under budget pressure, while high-value items are preserved or deferred.
"""

from typing import Any, Dict, Iterable, List, Tuple

from .intelligent_forgetting import IntelligentForgettingSystem


def process_batch(
    system: IntelligentForgettingSystem,
    items: Iterable[Tuple[Any, Dict[str, Any]]],
) -> List[Dict[str, Any]]:
    """Process a batch of (item, meta) pairs with priority ordering.

    Priority is determined by the system's aggregate score; lower scores are
    processed first so that budget pressure can be alleviated early.
    """

    # Pre-score to decide order
    scored: List[Tuple[float, Any, Dict[str, Any]]] = []
    for item, meta in items:
        scores = system.analyzer.analyze(item, meta)
        agg = system.decision_engine._aggregate(scores, meta)  # type: ignore
        scored.append((agg, item, meta))

    # Process low-score first
    scored.sort(key=lambda t: t[0])
    results: List[Dict[str, Any]] = []
    for _, item, meta in scored:
        results.append(system.process_item(item, meta))
    return results
