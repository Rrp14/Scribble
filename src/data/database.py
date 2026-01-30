from pymongo import AsyncMongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv
import os

load_dotenv()

client = None
db = None


async def connect_to_mongo():
    global client, db

    uri = os.getenv("MONGO_URI")
    db_name = os.getenv("MONGO_DB_NAME")

    if not uri or not db_name:
        raise RuntimeError("MongoDB env vars not set")

    client = AsyncMongoClient(
        uri,
        server_api=ServerApi("1", strict=True, deprecation_errors=True)
    )

    await client.admin.command({"ping": 1})

    db = client[db_name]


async def close_mongo():
    if client:
        client.close()
