import time,uuid

import redis
from fastapi import  Request,HTTPException,Depends
from redis.utils import pipeline
from src.core.rate_limit_config import RATE_LIMITS
from src.data.redis import redis_client

class SlidingWindowRateLimiter:
    def __init__(self,
                 key_prefix:str,
                 limit:int,
                 window_seconds:int,
                 use_user:bool=False
                 ):
        self.key_prefix=key_prefix
        self.limit=limit
        self.window=window_seconds
        self.use_user=use_user


    @classmethod
    def from_config(cls,config_key:str):
        if config_key not in RATE_LIMITS:
            raise RuntimeError(
                f"Sliding rate limit config '{config_key}' not found"
            )

        cfg = RATE_LIMITS[config_key]

        return cls(
            key_prefix=config_key.lower(),
            limit=cfg["limit"],
            window_seconds=cfg["window"],
            use_user=cfg["use_user"],
        )



    async def __call__(self, request:Request,current_user=Depends(lambda:None)):
        now=int(time.time())
        window_start=now-self.window

        if self.use_user and current_user:
            identifier=str(current_user["_id"])
        else:
            identifier=request.client.host

        key=f"rate:{self.key_prefix}:{identifier}"


        """remove old request"""
        pipeline=redis_client.pipeline()

        pipeline.zremrangebyscore(key,0,window_start)

        """add current request"""
        member=f"{now}-{uuid.uuid4()}"
        pipeline.zadd(key,{member:now})


        """count request in window"""
        pipeline.zcard(key)

        """set expiry"""
        pipeline.expire(key,self.window)

        _,_,request_count,_=pipeline.execute()

        if request_count>self.limit:
            retry_after=redis_client.zrange(key,0,0,withscores=True)
            if retry_after:
                oldest_ts=int(retry_after[0][1])
                retry_after=self.window-(now-oldest_ts)
            else:
                retry_after=self.window

            raise HTTPException(
                status_code=429,
                detail=f"Too many requests. Retry in {retry_after}s",
                headers={"Retry-After": str(retry_after)},
            )