# TODO Connect the mqtt from config and route them to insert the database
import httpx
import json

from app.model.schemas import SensorReading
from app.services.inference_engine import InferenceEngine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.config import DatabaseClient

class MQTTHandler():
    @classmethod
    async def read_topic_sensor(cls, db_client: "DatabaseClient", topic:str, payload:bytes):
        # Debugger
        print("test from MQTT Handler")
        print(f"Message from {topic}: {payload.decode()}")

        device_id = topic.split('/')[0]
        # raw_data = json.loads(payload.decode())

        # Get Openmeteo Open Source Weather API
        async with httpx.AsyncClient() as client:
            response = await client.get("http://server:8000/service/weather")

        readings = await cls.extract_esp32_data(db_client, weather_data=response.json(), device_id=device_id)

        pool = db_client.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO sensors (sensor_id, location) VALUES ($1, $2) "
                "ON CONFLICT (sensor_id) DO NOTHING",
                device_id, "Reservoir Air Kampus Jatinangor"
            )
        
            await conn.execute(
                "INSERT INTO sensor_readings (timestamp, sensor_id, precipitation, temperature, humidity, water_height, classification) VALUES (NOW(), $1, $2, $3, $4, $5, $6)",
                readings.device_id, readings.precipitation, readings.temperature, readings.humidity, readings.water_height, readings.classification
            )

    @classmethod
    def publish_topic(cls):
        pass

    @classmethod
    async def extract_esp32_data(cls, db_client: "DatabaseClient", weather_data: dict, device_id: str, sensor_data: dict = None) -> SensorReading:
        classification = await InferenceEngine.calculate_flood_probability(db_client, weather_data, sensor_data, device_id)
        
        return SensorReading(
            device_id=device_id,
            precipitation=weather_data.get('precipitation'),
            temperature=weather_data.get('temperature_2m'),
            humidity=float(weather_data.get('relative_humidity_2m')),
            water_height=1.0, # Placeholder
            classification=classification,
        )
