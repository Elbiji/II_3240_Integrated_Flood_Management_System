from fastapi import APIRouter, Header, HTTPException
from app.model.schemas import SensorReading
from app.config import settings, RedisClient, HTTPClient
from app.middleware import check_rate_limit
import httpx
import json
import openmeteo_requests

router = APIRouter()

@router.post("/sensor/reading")
async def ingest_reading(
    payload: SensorReading,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ", "")

    await check_rate_limit(payload.device_id)

    return { "status": "queued", "device_id": payload.device_id }

@router.get("/sensor/latest/{device_id}")
async def get_latest_prediction(
    device_id: str,
    authorization: str = Header(...)
):
    token = authorization.replace("Bearer ","")

    cached = await RedisClient.get().get(f"pred:{device_id}")
    if not cached:
        raise HTTPException(status_code=404, detail="No prediction yet")
    
    return { "device_id": device_id, **json.loads(cached) }

@router.get("/service/weather")
async def weather():
    # client = HTTPClient.get()

    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(f"https://weather.googleapis.com/v1/currentConditions:lookup?key={settings.GOOGLE_API_WEATHER_KEY}&location.latitude=-6.923955&location.longitude=107.601807")
    #         response.raise_for_status()
    #         return response.json()
    # except httpx.HTTPStatusError as exc:
    #     raise HTTPException(
    #         status_code=exc.response.status_code,
    #         detail=f"Error from external API: {exc.response.status_code}"
    #     ) 
    # except httpx.RequestError as exc:
    #     raise HTTPException(
    #         status_code=503,
    #         detail=f"Could not connect to external API: {exc.request.url}"
    #     )

    # url = "https://api-open-meteo.com/v1/forecast"

    # responses = openmetero

    client = HTTPClient.get()
    url = "https://api.open-meteo.com/v1/forecast?latitude=-6.923955&longitude=107.601807&current=temperature_2m,precipitation,rain,relative_humidity_2m,wind_speed_10m,pressure_msl,cloud_cover&timezone=Asia%2FSingapore&forecast_days=1"

    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        print(data)

        return data.get("current", {})
    except Exception as e:
        print(f"Open-Meteo Error: {e}")
        return None
