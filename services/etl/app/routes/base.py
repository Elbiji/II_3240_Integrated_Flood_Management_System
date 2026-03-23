from fastapi import APIRouter, HTTPException
from config import settings
import httpx

router = APIRouter()

@router.get("/weather")
async def weather():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"https://weather.googleapis.com/v1/currentConditions:lookup?key={settings.GOOGLE_API_WEATHER_KEY}&location.latitude=-6.923955&location.longitude=107.601807")
            response.raise_for_status()
            return response.json()
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

