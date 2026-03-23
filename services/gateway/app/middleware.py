from fastapi import HTTPException, Header
import httpx
import redis.asyncio as redis

AUTH_SERVICE = "http://localhost:8001"
MODEL_SERVICE = "http://localhost:8082"

async def check_rate_limit(device_id: str, r: redis.Redis):
    key = f"rate:{device_id}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 60)
    if count > 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
async def check_auth(device_id: str, token: str):
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(f"{AUTH_SERVICE}/auth/validate", json={
                "device_id": device_id,
                "token": token
            })
            if res.status_code != 200:
                raise HTTPException(status_code=401, detail="Unauthorized")
        except httpx.ConnectError:
            raise HTTPException(status_code=503, detail="Auth service unavailable")