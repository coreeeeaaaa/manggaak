"""4D masking strategy stub with v1 profile compatibility."""

from typing import Any, Dict


MASKING_PROFILES = {
    "X": {"mask_rate": 0.50, "score": 3},
    "Y": {"mask_rate": 0.25, "score": 2},
    "Z": {"mask_rate": 0.33, "score": 2.5},
    "T": {"mask_rate": 0.66, "score": 4},
    "X+Y": {"mask_rate": 0.625, "score": 5},
    "X+Z": {"mask_rate": 0.665, "score": 5.5},
    "X+T": {"mask_rate": 0.83, "score": 7},
    "Y+Z": {"mask_rate": 0.4925, "score": 4.5},
    "Y+T": {"mask_rate": 0.745, "score": 6},
    "Z+T": {"mask_rate": 0.7778, "score": 6.5},
    "X+Y+Z": {"mask_rate": 0.74125, "score": 7.5},
    "X+Y+T": {"mask_rate": 0.89125, "score": 8.5},
    "X+Z+T": {"mask_rate": 0.94445, "score": 9},
    "Y+Z+T": {"mask_rate": 0.86335, "score": 8},
    "X+Y+Z+T": {"mask_rate": 0.96667, "score": 10},
}


class Masking:
    def apply(self, item: Any, meta: Dict[str, Any], plan: Any, scores: Any, context: Any) -> Dict[str, Any]:
        profile = plan.params.get("profile") if hasattr(plan, "params") else None
        profile = profile or "X+Y"
        profile_data = MASKING_PROFILES.get(profile, MASKING_PROFILES["X+Y"])
        context.reversibility_state.advance(4)
        size = float(meta.get("size_bytes", 1.0))
        saved = size * profile_data["mask_rate"] * 0.5  # heuristic saved fraction
        context.budget_state.record_usage(storage_delta=-saved)
        redacted = None
        content = meta.get("content") or item.get("content") if isinstance(item, dict) else None
        if isinstance(content, str):
            redacted = content[: max(1, int(len(content) * (1 - profile_data["mask_rate"])))].ljust(len(content), "*")
        return {
            "status": "masked",
            "profile": profile,
            "mask_rate": profile_data["mask_rate"],
            "redacted_preview": redacted,
            "feedback": {"type": "mask_applied"},
        }
