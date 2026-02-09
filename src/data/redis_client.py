import redis
import os
from urllib.parse import urlparse

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

parsed = urlparse(REDIS_URL)

redis_client = redis.Redis(
    host=parsed.hostname or "localhost",
    port=parsed.port or 6379,
    db=int(parsed.path[1:]) if parsed.path and parsed.path != "/" else 0,
)
