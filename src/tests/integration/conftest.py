import pytest

from src.data.database import connect_to_mongo,close_mongo
from src.data.redis_client import redis_client

@pytest.fixture(scope="session",autouse=True)
async def