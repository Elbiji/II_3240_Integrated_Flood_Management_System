# TODO Connect the mqtt from config and route them to insert the database
import httpx
import json

from app.model.schemas import SensorReading, Classification
from app.services.inference_engine import InferenceEngine
from app.config import MQTTClient, DatabaseClient

class MQTTHandler():
    @classmethod
    async def read_topic_sensor(cls, topic:str, payload:bytes):
        # Debugger
        print("test from MQTT Handler")
        print(f"Message from {topic}: {payload.decode()}")

        device_id = topic.split('/')[0]
        # raw_data = json.loads(payload.decode())

        # Get Openmeteo Open Source Weather API
        async with httpx.AsyncClient() as client:
            response = await client.get("http://server:8000/api/v1/services/weather")

        readings = await cls.extract_esp32_data(weather_data=response.json(), sensor_data=payload.decode(), device_id=device_id)

        pool = DatabaseClient.get_pool()

        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO sensors (sensor_id, location) VALUES ($1, $2)
                   ON CONFLICT (sensor_id) DO NOTHING""",
                device_id, "Reservoir Air Kampus Jatinangor"
            )
        
            await conn.execute(
                """INSERT INTO sensor_readings (timestamp, sensor_id, precipitation, temperature, humidity, water_height, water_height_change, classification)
                   VALUES (NOW(), $1, $2, $3, $4, $5, $6, $7)""",
                readings.device_id, readings.precipitation, readings.temperature, readings.humidity, readings.water_height, readings.water_height_change, readings.classification
            )

        if readings.classification == Classification.DANGER:
            message = json.dumps({"pump": True})
            cls.publish_topic(topic="water_pump", message=message, device_id=device_id)
        else:
            message = json.dumps({"pump": False})
            cls.publish_topic(topic="water_pump", message=message, device_id=device_id)

    @classmethod
    def publish_topic(cls, topic: str, message: str, device_id: str):
        client = MQTTClient.get_client()
        print(f"Publishing topic to - {device_id}/{topic}")
        client.publish(f"{device_id}/{topic}", message)


    @classmethod
    async def extract_esp32_data(cls, weather_data: dict, device_id: str, sensor_data: str) -> SensorReading:
        classification, velocity = await InferenceEngine.calculate_inference(weather_data, json.loads(sensor_data), device_id)
        
        return SensorReading(
            device_id=device_id,
            precipitation=weather_data.get('precipitation'),
            temperature=weather_data.get('temperature_2m'),
            humidity=float(weather_data.get('relative_humidity_2m')),
            water_height=1.0, # Placeholder
            water_height_change=velocity,
            classification=classification,
        )
