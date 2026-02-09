from src.data.redis_client import redis_client

def test_redis_set_get():
    redis_client.set("test:key","value")
    val=redis_client.get("test:key")

    assert val.decode("utf-8")=="value"

