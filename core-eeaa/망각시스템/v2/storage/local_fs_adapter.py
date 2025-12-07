"""Local filesystem storage backend (demo only)."""

import time
import threading
from pathlib import Path
from typing import Any, Dict, Optional

from .base import StorageBackend


class LocalFSAdapter(StorageBackend):
    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.ttl_map: Dict[Any, float] = {}
        self._lock = threading.Lock()

    def move_to_tier(self, item_id: Any, content: Any, tier: str, ttl: Optional[float] = None) -> Dict[str, Any]:
        tier_dir = self.root / tier
        tier_dir.mkdir(parents=True, exist_ok=True)
        path = tier_dir / f"{item_id}.bin"
        data = content
        if isinstance(content, str):
            data = content.encode("utf-8")
        if isinstance(data, bytes):
            with self._lock:
                path.write_bytes(data)
        else:
            with self._lock:
                path.write_text(str(data), encoding="utf-8")
        if ttl:
            with self._lock:
                self.ttl_map[item_id] = time.time() + ttl
        size = path.stat().st_size if path.exists() else 0
        return {"tier": tier, "size": size, "ttl": ttl, "path": str(path)}

    def purge_expired(self) -> Dict[str, int]:
        with self._lock:
            now = time.time()
            removed = 0
            for item_id, expire_at in list(self.ttl_map.items()):
                if now >= expire_at:
                    for tier_dir in self.root.iterdir():
                        if tier_dir.is_dir():
                            path = tier_dir / f"{item_id}.bin"
                            if path.exists():
                                path.unlink()
                    self.ttl_map.pop(item_id, None)
                    removed += 1
            return {"removed": removed}
