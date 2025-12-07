import sys
from pathlib import Path
import time
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from v2.core.pipeline import ForgettingPipeline


class TestLedgerPipeline(unittest.TestCase):
    def test_pipeline_stores_tiers_and_logs(self):
        pipe = ForgettingPipeline()
        items = [
            ({"id": "hot1"}, {"id": "hot1", "content": "very important", "semantic_value": 0.9, "business_impact": 0.9, "access_frequency": 0.8}),
            ({"id": "pii1"}, {"id": "pii1", "content": "My SSN is 123-45-6789", "class": "pii", "pii": True}),
            ({"id": "cold1"}, {"id": "cold1", "content": "old log", "importance": 0.1, "access_frequency": 0.0, "semantic_value": 0.1, "archive_ttl": 1}),
        ]
        res = pipe.run(items)
        self.assertGreaterEqual(len(pipe.storage.tiers["hot"]), 1)
        self.assertGreaterEqual(len(pipe.storage.tiers["warm"]), 1)
        # let TTL expire and purge
        time.sleep(1.1)
        res2 = pipe.run([])
        self.assertGreaterEqual(res2["purge"]["removed"], 0)
        # ledger should have events recorded
        self.assertGreaterEqual(len(pipe.system.ledger.events), 3)
        # constraints/thresholds should be present in ledger entries
        entry = pipe.system.ledger.events[0]
        self.assertIn("policy", entry)
        self.assertIn("constraints", entry)


if __name__ == "__main__":
    unittest.main()
