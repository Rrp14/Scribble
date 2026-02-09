import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from main import app
from src.data import database
from src.data.database import connect_to_mongo, close_mongo
from src.data.redis_client import redis_client


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_integration_env():
    await connect_to_mongo()
    await database.db.users.delete_many({})
    await database.db.notes.delete_many({})
    redis_client.flushdb()

    yield

    redis_client.flushdb()
    await database.db.users.delete_many({})
    await database.db.notes.delete_many({})
    await close_mongo()


@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
