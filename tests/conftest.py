import pytest
import pytest_asyncio

from src.data.database import connect_to_mongo,close_mongo
from src.data.redis_client import redis_client

@pytest_asyncio.fixture(scope="function",autouse=True)
async def setup_integration_env():
    await connect_to_mongo()


    redis_client.flushdb()

    yield
    redis_client.flushdb()
    await close_mongo()