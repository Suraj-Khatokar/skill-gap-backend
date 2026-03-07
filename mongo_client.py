import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017")

print(f"[mongo_client] Connecting to: {MONGO_URI[:30]}...")

_client: MongoClient = None

def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=20000)
    return _client

def get_db():
    return get_client()["skill_gap_db"]

def get_collection(name: str):
    return get_db()[name]