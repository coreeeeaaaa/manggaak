"""Simple in-memory metrics collector."""

from collections import Counter
from typing import Dict


class Metrics:
    def __init__(self) -> None:
        self.actions = Counter()
        self.errors = Counter()

    def record_action(self, action: str) -> None:
        self.actions[action] += 1

    def record_error(self, name: str) -> None:
        self.errors[name] += 1

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        return {
            "actions": dict(self.actions),
            "errors": dict(self.errors),
        }
