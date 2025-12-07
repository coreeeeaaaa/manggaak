"""Parallel batch processing using ThreadPoolExecutor."""

from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, Iterable, List, Tuple

from .intelligent_forgetting import IntelligentForgettingSystem


def process_batch_parallel(
    system: IntelligentForgettingSystem,
    items: Iterable[Tuple[Any, Dict[str, Any]]],
    max_workers: int = 4,
) -> List[Dict[str, Any]]:
    items_list = list(items)
    # Snapshot max_workers from config if exists
    cfg_workers = max_workers
    try:
        cfg_workers = system.decision_engine.thresholds.get("parallel_workers", max_workers)
    except Exception:
        pass

    def worker(pair):
        item, meta = pair
        return system.process_item(item, meta)

    with ThreadPoolExecutor(max_workers=cfg_workers) as ex:
        results = list(ex.map(worker, items_list))
    return results
