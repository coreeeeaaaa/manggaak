"""Simple tiered storage adapter stub with TTL support and basic locking."""

import time
import threading
from typing import Any, Dict, Optional


class StorageAdapter:
    def __init__(self):
        self.tiers = {"hot": {}, "warm": {}, "cold": {}}
        self.ttl_map: Dict[Any, float] = {}
        self._lock = threading.Lock()

    def move_to_tier(self, item_id: Any, content: Any, tier: str, ttl: Optional[float] = None) -> Dict[str, Any]:
        with self._lock:
            if tier not in self.tiers:
                tier = "cold"
            self.tiers[tier][item_id] = content
            if ttl:
                self.ttl_map[item_id] = time.time() + ttl
            size = len(content) if isinstance(content, (bytes, str)) else 0
            return {"tier": tier, "size": size, "ttl": ttl}

    def purge_expired(self) -> Dict[str, int]:
        with self._lock:
            now = time.time()
            removed = 0
            for item_id, expire_at in list(self.ttl_map.items()):
                if now >= expire_at:
                    for tier in self.tiers.values():
                        tier.pop(item_id, None)
                    self.ttl_map.pop(item_id, None)
                    removed += 1
            return {"removed": removed}
