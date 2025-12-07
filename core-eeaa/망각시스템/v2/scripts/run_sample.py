"""Sample runner for Intelligent Forgetting System v2.

Usage:
  python -m v2.scripts.run_sample
"""

from v2.core.system_builder import build_system


def main():
    sys = build_system()

    samples = [
        {"id": 1, "meta": {"semantic_value": 0.9, "business_impact": 0.9, "access_frequency": 0.8}},
        {"id": 2, "meta": {"importance": 0.2, "access_frequency": 0.0, "semantic_value": 0.2}},
        {"id": 3, "meta": {"importance": 0.4, "semantic_value": 0.6, "mask_profile": "X+Y+T"}},
        {"id": 4, "meta": {"importance": 0.1, "allow_irreversible": True}},
    ]

    for sample in samples:
        result = sys.process_item(item={"id": sample["id"]}, meta=sample["meta"])
        print(f"item={sample['id']} plan={result['plan'].action} result={result['result']}")


if __name__ == "__main__":
    main()
