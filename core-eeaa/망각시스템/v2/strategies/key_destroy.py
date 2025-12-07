"""Irreversible key destruction stub (Crypto Shredding hook)."""

from typing import Any, Dict


class KeyDestroy:
    def apply(self, item: Any, meta: Dict[str, Any], plan: Any, scores: Any, context: Any) -> Dict[str, Any]:
        if not meta.get("allow_irreversible"):
            return {
                "status": "blocked",
                "reason": "approval_required",
                "feedback": {"type": "irreversible_blocked"},
            }
        context.reversibility_state.advance(9)
        size = float(meta.get("size_bytes", 1.0))
        context.budget_state.record_usage(storage_delta=-size)
        return {
            "status": "key_destroyed",
            "feedback": {"type": "irreversible_success"},
        }
