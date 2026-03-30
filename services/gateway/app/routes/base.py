from fastapi import APIRouter, Header, HTTPException
from app.model.schemas import SensorReading
from app.middleware import check_auth, check_rate_limit
import redis.asyncio as aioredis
import json

router = APIRouter()

redis_client: aioredis.Redis = None

def set_redis(r: aioredis.Redis):
    global redis_client
    redis_client = r

@router.post("/sensor/reading")
async def ingest_reading(
    payload: SensorReading,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "")

    await check_rate_limit(payload.device_id, redis_client)

    await check_auth(payload.device_id, token)

    return { "status": "queued", "device_id": payload.device_id }

@router.get("/sensor/latest/{device_id}")
async def get_latest_prediction(
    device_id: str,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ","")

    await check_auth(device_id, token)

    cached = await redis_client.get(f"pred:{device_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="No prediction yet")
    
    return { "device_id": device_id, **json.loads(cached) }