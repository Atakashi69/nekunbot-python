import os

from motor.motor_asyncio import AsyncIOMotorClient
"""
db_name = 'myFirstDatabase'
collection_name = 'articles'

db = DBHelper[db_name]
collection = db[collection_name]

async def insert_article(article_id: str):
    document = {
        'article_id': article_id
    }
    result = await collection.insert_one(document)
    print(f"New article added with id: {result.inserted_id}")

def find_article(article_id:str):
    query = {
        'article_id': article_id
    }

    entries = collection.find(query)
    if entries.collection.count_documents({}) <= 0:
        print(f'There is no article with id: {article_id}')
        return False

    for entry in entries:
        print(entry)
    return True

async def is_article_exists(article_id: str):
    query = {
        'article_id': article_id
    }

    print(f'looking for {query}')
    return collection.estimated_document_count(query) > 0
"""
