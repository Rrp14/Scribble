import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException
from src.core.rate_limiter import RateLimiter


# Mocking the Request and Client
class FakeRequest:
    def __init__(self):
        self.client = MagicMock()
        self.client.host = "127.0.0.1"


@pytest.mark.asyncio
async def test_rate_limiter_sliding_window(monkeypatch):
    # 1. Setup the Limiter
    limiter = RateLimiter(key_prefix="test", limit=2, window_seconds=60, use_user=False)

    # 2. Mock Redis and the Pipeline
    mock_redis = AsyncMock()
    mock_pipe = AsyncMock()

    # Configure the pipeline to return a list of results
    # The 3rd item (index 2) is usually the result of ZCARD (the count)
    mock_pipe.execute.side_effect = [
        [None, None, 1],  # First call: 1 request in window
        [None, None, 2],  # Second call: 2 requests in window
        [None, None, 3],  # Third call: 3 requests (should fail)
    ]

    # Ensure .pipeline() returns our mock_pipe
    mock_redis.pipeline.return_value = mock_pipe
    # If using 'async with', we need the context manager mock:
    mock_pipe.__aenter__.return_value = mock_pipe

    # 3. Patch the redis_client in your actual code
    monkeypatch.setattr("src.data.redis_client.redis_client", mock_redis)

    req = FakeRequest()

    # 4. First and Second requests should pass
    await limiter(req)
    await limiter(req)

    # 5. Third request should raise 429
    with pytest.raises(HTTPException) as exc:
        await limiter(req)

    assert exc.value.status_code == 429
