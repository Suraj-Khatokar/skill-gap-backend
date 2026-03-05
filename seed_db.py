"""
Run once to seed MongoDB with roles from data/roles.json.
Usage: python seed_db.py
"""
import json
import os
from mongo_client import get_collection


def seed():
    path = os.path.join(os.path.dirname(__file__), "data", "roles.json")
    with open(path) as f:
        raw = json.load(f)

    col = get_collection("roles")
    col.drop()  # fresh seed every run

    docs = []
    for role_id, data in raw["roles"].items():
        docs.append({"role_id": role_id, **data})

    col.insert_many(docs)
    print(f"✓ Seeded {len(docs)} roles into skill_gap_db.roles")


if __name__ == "__main__":
    seed()