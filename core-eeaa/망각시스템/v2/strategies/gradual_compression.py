"""Gradual compression strategy with gzip as a default backend."""

import gzip
import io
from typing import Any, Dict


class GradualCompression:
    def apply(self, item: Any, meta: Dict[str, Any], plan: Any, scores: Any, context: Any) -> Dict[str, Any]:
        # Lossless stage first, optionally lossy if requested.
        context.reversibility_state.advance(1)
        lossy = plan.params.get("lossy") if hasattr(plan, "params") else False
        if lossy:
            context.reversibility_state.advance(5)
        # Heuristic compressed size fraction
        content = meta.get("content") or item.get("content") if isinstance(item, dict) else None
        size = float(meta.get("size_bytes", len(content) if isinstance(content, (str, bytes)) else 1.0))
        compressed_size = size
        if isinstance(content, str):
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as f:
                f.write(content.encode("utf-8"))
            compressed_size = len(buf.getvalue())
        elif isinstance(content, bytes):
            buf = io.BytesIO()
            with gzip.GzipFile(fileobj=buf, mode="wb") as f:
                f.write(content)
            compressed_size = len(buf.getvalue())

        saved = max(0.0, size - compressed_size)
        if lossy:
            saved = max(saved, size * 0.3)
        context.budget_state.record_usage(storage_delta=-saved)
        return {
            "status": "compressed_lossy" if lossy else "compressed_lossless",
            "stage": context.reversibility_state.stage,
            "compressed_size": compressed_size,
            "feedback": {"type": "compress_success"},
        }
