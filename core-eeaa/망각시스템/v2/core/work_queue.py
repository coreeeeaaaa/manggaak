"""Work queue with worker threads for stable parallel processing."""

import queue
import threading
from typing import Any, Dict, Tuple, Callable

from .intelligent_forgetting import IntelligentForgettingSystem


class WorkQueue:
    def __init__(self, system: IntelligentForgettingSystem, workers: int = 4):
        self.system = system
        self.workers = workers
        self.q: queue.Queue[Tuple[Any, Dict[str, Any], Callable[[Dict[str, Any]], None]]] = queue.Queue()
        self._threads = []
        self._stop = threading.Event()

    def start(self):
        for _ in range(self.workers):
            t = threading.Thread(target=self._worker, daemon=True)
            t.start()
            self._threads.append(t)

    def stop(self):
        self._stop.set()
        for _ in self._threads:
            self.q.put(None)  # type: ignore
        for t in self._threads:
            t.join(timeout=1)

    def submit(self, item: Any, meta: Dict[str, Any], callback: Callable[[Dict[str, Any]], None] = None):
        self.q.put((item, meta, callback or (lambda _: None)))

    def _worker(self):
        while not self._stop.is_set():
            task = self.q.get()
            if task is None:
                break
            item, meta, cb = task
            try:
                res = self.system.process_item(item, meta)
                cb(res)
            except Exception as exc:
                self.system.ledger.log_error("worker_failure", {"error": str(exc), "meta": meta})
            finally:
                self.q.task_done()
