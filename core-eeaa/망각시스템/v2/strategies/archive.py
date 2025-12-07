"""Archive strategy stub: move to cold storage with TTL."""

from typing import Any, Dict


class Archive:
    def apply(self, item: Any, meta: Dict[str, Any], plan: Any, scores: Any, context: Any) -> Dict[str, Any]:
        size = float(meta.get("size_bytes", 1.0))
        saved = size * 0.5  # cold storage reduction
        context.budget_state.record_usage(storage_delta=-saved)
        ttl = meta.get("archive_ttl", 30 * 24 * 3600)
        return {
            "status": "archived",
            "ttl": ttl,
            "feedback": {"type": "archived"},
        }
