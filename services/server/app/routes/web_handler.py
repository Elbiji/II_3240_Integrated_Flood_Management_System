from fastapi import APIRouter, Header, HTTPException
from app.model.schemas import SensorReading
from app.config import RedisClient, HTTPClient
from app.middleware import check_rate_limit
import httpx
import json

router = APIRouter()

@router.get("/service/weather")
async def weather():
    client = HTTPClient.get()
    url = "https://api.open-meteo.com/v1/forecast?latitude=-6.923955&longitude=107.601807&current=temperature_2m,precipitation,rain,relative_humidity_2m,wind_speed_10m,pressure_msl,cloud_cover&timezone=Asia%2FSingapore&forecast_days=1"

    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        # Debugger
        print(data)

        return data.get("current", {})
    except Exception as e:
        print(f"Open-Meteo Error: {e}")
        return None

# @router.get("/service/data")