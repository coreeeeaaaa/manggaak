"""Deletion strategy stub."""

from typing import Any, Dict


class Delete:
    def apply(self, item: Any, meta: Dict[str, Any], plan: Any, scores: Any, context: Any) -> Dict[str, Any]:
        context.reversibility_state.advance(7)
        size = float(meta.get("size_bytes", 1.0))
        context.budget_state.record_usage(storage_delta=-size)
        return {
            "status": "deleted",
            "feedback": {"type": "deleted"},
        }
