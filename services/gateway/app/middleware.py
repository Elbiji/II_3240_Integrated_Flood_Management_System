from fastapi import HTTPException
from app.config import settings, RedisClient
import httpx

# Container ports
AUTH_SERVICE = settings.AUTH_SERVICE
MODEL_SERVICE = settings.MODEL_SERVICE

async def check_rate_limit(device_id: str):
    r = RedisClient.get()
    key = f"rate:{device_id}"
    count = await r.incr(key)
    if count == 1:
        await r.expire(key, 60)
    if count > 10:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
async def check_device_auth(device_id: str, token: str):
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
        
async def check_user_auth():
    #TODO Servis autentikasi pengguna sama device belom
    pass