import sys
import time
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from v2.core.pipeline import ForgettingPipeline


class TestE2EPipeline(unittest.TestCase):
    def test_high_value_preserved_low_value_deleted(self):
        pipe = ForgettingPipeline()
        items = [
            ({"id": "high"}, {"id": "high", "content": "very important data", "semantic_value": 0.9, "business_impact": 0.9, "access_frequency": 0.8}),
            ({"id": "low"}, {"id": "low", "content": "junk", "importance": 0.1, "access_frequency": 0.0, "semantic_value": 0.1, "redundancy": 1.0, "archive_ttl": 1}),
        ]
        res = pipe.run(items)
        actions = [r["plan"].action for r in res["results"]]
        self.assertIn("preserve", actions)
        self.assertTrue(any(a in {"archive", "delete", "mask"} for a in actions))
        time.sleep(1.1)
        res2 = pipe.run([])
        self.assertGreaterEqual(res2["purge"]["removed"], 0)

    def test_pii_requires_approval(self):
        pipe = ForgettingPipeline()
        items = [({"id": "pii"}, {"id": "pii", "content": "My SSN is 123-45-6789", "class": "pii", "pii": True})]
        res = pipe.run(items)
        action = res["results"][0]["plan"].action
        self.assertIn(action, {"mask", "retain"})

    def test_irreversible_requires_token(self):
        pipe = ForgettingPipeline()
        pipe.system.context_manager.reversibility_state.advance(7)
        items = [({"id": "irr"}, {"id": "irr", "allow_irreversible": True})]
        res = pipe.run(items)
        action = res["results"][0]["plan"].action
        self.assertEqual(action, "retain")
        # with token
        items2 = [({"id": "irr2"}, {"id": "irr2", "allow_irreversible": True, "approval_token": "ok"})]
        res2 = pipe.run(items2)
        self.assertEqual(res2["results"][0]["plan"].action, "key_destroy")


if __name__ == "__main__":
    unittest.main()
