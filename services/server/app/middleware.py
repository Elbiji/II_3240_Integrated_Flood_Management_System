from fastapi import HTTPException, Request
from app.config import RedisClient

async def check_rate_limit(request: Request):
    r = RedisClient.get()

    client_ip = request.client.host
    key = f"rate:{client_ip}"

    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 60)
        
    if count > 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")