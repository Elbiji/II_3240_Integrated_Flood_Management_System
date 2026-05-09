from fastapi import HTTPException
from app.config import RedisClient

async def check_rate_limit(device_id: str):
    r = RedisClient.get()
    key = f"rate:{device_id}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 60)
    if count > 100:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")