"""Storage adapter interface for pluggable backends."""

from typing import Any, Dict, Optional


class StorageBackend:
    def move_to_tier(self, item_id: Any, content: Any, tier: str, ttl: Optional[float] = None) -> Dict[str, Any]:
        raise NotImplementedError

    def purge_expired(self) -> Dict[str, int]:
        raise NotImplementedError

    def delete_item(self, item_id: Any) -> Dict[str, Any]:
        raise NotImplementedError
