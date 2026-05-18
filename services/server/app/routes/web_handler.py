from fastapi import APIRouter, HTTPException, Query, Depends
from app.config import HTTPClient, DatabaseClient
from app.middleware import check_rate_limit
from datetime import timedelta

router = APIRouter()


@router.get("/api/v1/sensors/{device_id}/history")
async def get_sensor_history(device_id: str, 
                             window: str = Query("1 hour", regex="^(1 hour|24 hours|7 days|30 days)$"),
                             _ = Depends(check_rate_limit)):
    bucket_map = {
        "1 hour": timedelta(seconds=10),
        "24 hours": timedelta(minutes=5),
        "7 days": timedelta(hours=1),
        "30 days": timedelta(hours=6)
    }
    bucket_size = bucket_map.get(window)

    pool = DatabaseClient.get_pool()
    # Limit data yang diliat -> Buat bucket per time window -> Order by dari oldest to newest data
    query = f"""
        SELECT
            time_bucket($2, timestamp) AS bucket,
            avg(water_height) as avg_height,
            avg(water_height_change) as avg_velocity
        FROM sensor_readings
        WHERE sensor_id = $1
            AND timestamp > NOW() - INTERVAL '{window}'
        GROUP BY bucket
        ORDER BY bucket ASC;
    """
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, device_id, bucket_size)

            return [
                {
                    "timestamp": row["bucket"].isoformat(),
                    "water_height": round(row["avg_height"], 2),
                    "water_height_change": round(row["avg_velocity"], 2)
                }
                for row in rows
            ]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/v1/sensors/{device_id}/weather_history")
async def get_sensor_weather_history(device_id: str,
                                     window: str = Query("1 hour", regex="^(1 hour|24 hours|7 days|30 days)$"),
                                     _ = Depends(check_rate_limit)):
    bucket_map = {
        "1 hour": timedelta(seconds=10),
        "24 hours": timedelta(minutes=5),
        "7 days": timedelta(hours=1),
        "30 days": timedelta(hours=6)
    }
    bucket_size = bucket_map.get(window)

    pool = DatabaseClient.get_pool()
    query = f"""
        SELECT
            time_bucket($2, timestamp) AS bucket,
            avg(precipitation) as avg_preciptation,
            avg(temperature) as avg_temperature,
            avg(humidity) as avg_humidity
        FROM sensor_readings 
        WHERE sensor_id = $1
            AND timestamp > NOW() - INTERVAL '{window}'
        GROUP BY bucket
        ORDER BY bucket ASC;
    """
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch(query, device_id, bucket_size)

            return [
                {
                    "timestamp": row["bucket"].isoformat(),
                    "precipitation": round(row["avg_preciptation"], 2),
                    "temperature": round(row['avg_temperature'], 2),
                    "humidity": round(row["avg_humidity"], 2)
                }
                for row in rows
            ]
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/v1/sensors/{device_id}/information")
async def get_sensor_information(device_id: str, _ = Depends(check_rate_limit)):

    pool = DatabaseClient.get_pool()
    query = """
        SELECT sensor_id, location
        FROM sensors
        WHERE sensor_id = $1;
    """

    try:
        async with pool.acquire() as conn:
            row = await conn.fetch(query, device_id)
            return row
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/api/v1/services/{device_id}/inference")
async def get_sensor_inference(device_id: str):
    pool = DatabaseClient.get_pool()
    query = """
        SELECT classification, timestamp
        FROM sensor_readings
        WHERE sensor_id = $1
        ORDER BY timestamp DESC
        LIMIT 1;
    """

    try:
        async with pool.acquire() as conn:
            row = await conn.fetch(query, device_id)
            return row
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/api/v1/services/weather")
async def weather():
    client = HTTPClient.get()
    url = "https://api.open-meteo.com/v1/forecast?latitude=-6.923955&longitude=107.601807&current=temperature_2m,precipitation,rain,relative_humidity_2m,wind_speed_10m,pressure_msl,cloud_cover&timezone=auto"

    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()

        # Debugger
        print(data)

        return data.get("current", {})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))