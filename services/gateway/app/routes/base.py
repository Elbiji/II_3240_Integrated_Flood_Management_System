from fastapi import APIRouter, Header, HTTPException
from app.model.schemas import SensorReading
from app.config import settings, RedisClient
from app.middleware import check_device_auth, check_rate_limit, check_user_auth
import httpx
import json

# Container ports
ETL_SERVICE = settings.ETL_SERVICE 

router = APIRouter()

@router.post("/sensor/reading")
async def ingest_reading(
    payload: SensorReading,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "")

    await check_rate_limit(payload.device_id)

    await check_device_auth(payload.device_id, token)

    return { "status": "queued", "device_id": payload.device_id }

@router.get("/sensor/latest/{device_id}")
async def get_latest_prediction(
    device_id: str,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ","")

    await check_device_auth(device_id, token)

    cached = await RedisClient.get().get(f"pred:{device_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="No prediction yet")
    
    return { "device_id": device_id, **json.loads(cached) }

@router.get("/data/weather")
async def get_latest_data():

    await check_user_auth()

    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(ETL_SERVICE + "/weather")
            res.raise_for_status()
            return res.json()
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=f"Error from external API: {exc.response.status_code}"
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"Could not connect to external API: {exc.request.url}"
            )