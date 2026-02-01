from pymongo import MongoClient
from dotenv import load_dotenv
import os
from typing import List, Dict

load_dotenv()

mongo_url = os.getenv("MONGO_URL")

mongo_client = MongoClient(mongo_url)

mongo_db = mongo_client.get_database("ybigta_db")

def get_collection(site_name: str):
    return mongo_db[site_name]


def get_reviews(site_name: str) -> List[Dict]:
    collection = get_collection(site_name)
    return list(collection.find({}, {"_id": 0}))


def replace_reviews(site_name: str, reviews: List[Dict]):
    collection = get_collection(site_name)
    collection.delete_many({})
    collection.insert_many(reviews)


def save_preprocessed_reviews(site_name: str, reviews: List[Dict]):
    preprocessed_collection_name = f"{site_name}_preprocessed"
    collection = mongo_db[preprocessed_collection_name]
    collection.delete_many({})  # 기존 전처리 데이터 삭제
    collection.insert_many(reviews)
    return preprocessed_collection_name


def get_preprocessed_reviews(site_name: str) -> List[Dict]:
    preprocessed_collection_name = f"{site_name}_preprocessed"
    collection = mongo_db[preprocessed_collection_name]
    return list(collection.find({}, {"_id": 0}))