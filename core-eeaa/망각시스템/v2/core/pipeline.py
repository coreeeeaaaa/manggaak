"""Forgetting pipeline that orchestrates tier transitions and TTL enforcement."""

from typing import Any, Dict, Iterable, Tuple

from .storage_adapter import StorageAdapter
from .batch_processor import process_batch
from .system_builder import build_system
from ..storage.local_fs_adapter import LocalFSAdapter
from pathlib import Path


class ForgettingPipeline:
    def __init__(self, storage: StorageAdapter = None, use_local_fs: bool = False):
        self.system = build_system()
        if storage:
            self.storage = storage
        elif use_local_fs:
            default_root = Path(__file__).resolve().parents[1] / ".data"
            self.storage = LocalFSAdapter(root=default_root)
        else:
            self.storage = StorageAdapter()

    def run(self, items: Iterable[Tuple[Any, Dict[str, Any]]]) -> Dict[str, Any]:
        results = process_batch(self.system, items)
        for res, (_, meta) in zip(results, items):
            action = res["plan"].action
            item_id = meta.get("id") or res["result"].get("id") if isinstance(res["result"], dict) else None
            content = meta.get("content")
            if action == "archive":
                ttl = meta.get("archive_ttl", 30 * 24 * 3600)
                self._move_with_retry(item_id, content or "", "cold", ttl=ttl)
            elif action == "preserve":
                self._move_with_retry(item_id, content or "", "hot")
            elif action == "mask":
                self._move_with_retry(item_id, res["result"].get("redacted_preview", ""), "warm")
            elif action == "compress":
                self._move_with_retry(item_id, content or "", "warm")
            elif action == "delete" or action == "key_destroy":
                if item_id is not None:
                    self.storage.delete_item(item_id)
        purge_info = self.storage.purge_expired()
        return {"results": results, "purge": purge_info}

    def _move_with_retry(self, item_id, content, tier, ttl=None, retries: int = 2):
        last_exc = None
        for attempt in range(retries + 1):
            try:
                return self.storage.move_to_tier(item_id, content, tier, ttl=ttl)
            except Exception as exc:
                last_exc = exc
                time.sleep(0.05 * (2 ** attempt))
        # log failure
        self.system.ledger.log_error("storage_move_failed", {"item_id": item_id, "tier": tier, "error": str(last_exc)})
        return {"error": str(last_exc)}
