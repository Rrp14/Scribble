from fastapi import Request, HTTPException, Depends
from src.core.rate_limit_config import RATE_LIMITS
from src.data.redis import redis_client


class RateLimiter:
    def __init__(self,key_prefix:str,limit:int,window_seconds:int,use_user:bool=False):
        self.key_prefix=key_prefix
        self.limit=limit
        self.window=window_seconds
        self.use_user=use_user


    @classmethod
    def from_config(cls,config_key:str):
        if config_key not in RATE_LIMITS:
            raise RuntimeError(f"Rate limit config '{config_key}' not found")

        cfg=RATE_LIMITS[config_key]

        return cls(
            key_prefix=config_key.lower(),
            limit=cfg["limit"],
            window_seconds=cfg["window"],
            use_user=cfg["use_user"]
        )

    async def __call__(self, request:Request,current_user=Depends(lambda:None)):
        """this function runs before the endpoint"""

        if self.use_user and current_user:
            identifier=str(current_user["_id"])
        else:
         identifier=request.client.host


        key=f"rate:{self.key_prefix}:{identifier}"

        current=redis_client.incr(key)

        if current==1:
            redis_client.expire(key,self.window)


        if current > self.limit:
            ttl=redis_client.ttl(key)
            raise HTTPException(
                status_code=429,
                detail=f"Too many request Try again in {ttl} seconds",
                headers={"Retry after":str(ttl)}
            )

