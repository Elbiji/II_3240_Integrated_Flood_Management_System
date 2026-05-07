# TODO Connect the mqtt from config and route them to insert the database
import httpx

from app.model.schemas import SensorReading
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.config import DatabaseClient

class MQTTHandler():
    @staticmethod
    async def read_topic_sensor(db_client: "DatabaseClient", topic:str, payload:bytes):
        # Debugger
        print("test from MQTT Handler")
        print(f"Message from {topic}: {payload.decode()}")

        pool = db_client.get_pool()
        device_id = topic.split('/')[0]

        async with pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO sensors (sensor_id, location) VALUES ($1, $2) "
                "ON CONFLICT (sensor_id) DO NOTHING",
                device_id, "Reservoir Air Kampus Jatinangor"
            )
        
        # Get Google API Data weather
        async with httpx.AsyncClient() as client:
            response = await client.get("http://server:8000/service/weather")
            print(response.json())

        # async with pool.acquire() as conn:
        #     await conn.execute(
        #         "INSERT INTO sensor_readings "
        #     )

    @staticmethod
    def publish_topic():
        pass