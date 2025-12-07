"""Default strategy registry and simple ledger hook."""

from typing import Dict, Any

from .context_manager import ContextManager
from ..strategies.gradual_compression import GradualCompression
from ..strategies.semantic_preservation import SemanticPreservation
from ..strategies.predictive_caching import PredictiveCaching
from ..strategies.adaptive_threshold import AdaptiveThreshold
from ..strategies.masking import Masking
from ..strategies.key_destroy import KeyDestroy
from ..strategies.archive import Archive
from ..strategies.delete import Delete


def build_default_registry() -> Dict[str, Any]:
    return {
        "compress": GradualCompression(),
        "semantic_preserve": SemanticPreservation(),
        "preserve": PredictiveCaching(),  # reuse caching as preservation placeholder
        "mask": Masking(),
        "archive": Archive(),
        "delete": Delete(),
        "key_destroy": KeyDestroy(),
        "retain": PredictiveCaching(),
    }
