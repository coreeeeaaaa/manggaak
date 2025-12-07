"""Context analyzer stub.

Considers domain relevance, user role importance, project dependency, network
centrality, urgency, resource availability.
"""

from typing import Any, Dict


def _norm(value: float) -> float:
    return max(0.0, min(1.0, value))


class ContextAnalyzer:
    def compute(self, item: Any, meta: Dict[str, Any]) -> float:
        role = float(meta.get("user_role_importance", 0.5))
        dependency = float(meta.get("project_dependency", 0.5))
        centrality = float(meta.get("network_centrality", 0.5))
        urgency = float(meta.get("urgency_factor", 0.5))
        availability = float(meta.get("resource_availability", 0.5))
        vals = [role, dependency, centrality, urgency, availability]
        avg = sum(vals) / len(vals)
        return _norm(avg)
