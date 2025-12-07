"""Ledger for decision/strategy events with optional file logging."""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional


class Ledger:
    def __init__(self, logfile: Optional[Path] = None) -> None:
        self.events: List[Dict[str, Any]] = []
        self.logfile = logfile

    def log(self, event: Dict[str, Any]) -> None:
        # ensure event is JSON-serializable
        serializable = {}
        for k, v in event.items():
            if hasattr(v, "__dict__"):
                serializable[k] = v.__dict__
            else:
                serializable[k] = v

        self.events.append(serializable)
        if self.logfile:
            line = json.dumps(serializable, ensure_ascii=False)
            self.logfile.parent.mkdir(parents=True, exist_ok=True)
            with self.logfile.open("a", encoding="utf-8") as f:
                f.write(line + "\n")

    def tail(self, n: int = 10) -> List[Dict[str, Any]]:
        return self.events[-n:]

    def log_error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        event = {"type": "error", "message": message, "context": context or {}}
        self.log(event)

    def log_constraint(self, name: str, passed: bool, detail: Optional[Dict[str, Any]] = None) -> None:
        event = {"type": "constraint", "name": name, "passed": passed, "detail": detail or {}}
        self.log(event)
