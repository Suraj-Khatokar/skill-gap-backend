from pymongo import MongoClient
from pymongo.database import Database

_client: MongoClient = None


def get_client() -> MongoClient:
    global _client
    if _client is None:
        _client = MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=5000)
    return _client


def get_db() -> Database:
    return get_client()["skill_gap_db"]


def get_collection(name: str):
    return get_db()[name]