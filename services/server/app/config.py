import redis.asyncio as aioredis
import asyncpg
import asyncio
import httpx

from fastapi_mqtt.config import MQTTConfig
from fastapi_mqtt.fastmqtt import FastMQTT
from app.routes.mqtt_handler import MQTTHandler
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    DATABASE_SERVICE: str
    DATABASE_URL: str
    REDIS_URL: str
    MQTT_BROKER_SERVICE: str
    MQTT_HOST: str
    MQTT_PORT: str
    GOOGLE_API_WEATHER_KEY: str

settings = Settings()

class RedisClient:
    _redis_client: aioredis.Redis = None

    @classmethod
    def set_redis(cls, r: aioredis.Redis):
        cls._redis_client = r

    @classmethod
    def get(cls):
        if cls._redis_client is None:
            raise RuntimeError("Redis not initialized")
        return cls._redis_client
    
    @classmethod
    async def close(cls):
        if cls._redis_client:
            await cls._redis_client.aclose()
            cls._redis_client = None

class DatabaseClient:
    _pool: Optional[asyncpg.Pool] = None

    @classmethod
    async def initialize(cls, dsn: str):
        if cls._pool is None:
            try:
                cls._pool = await asyncio.wait_for(asyncpg.create_pool(
                        dsn,
                        min_size=5,
                        max_size=20,
                        command_timeout=5
                    ),
                    timeout=5.0
                )
            except Exception as e:
                print(f"FAILED TO CONNECT TO DB: {e}")
                raise e

    @classmethod
    def get_pool(cls) -> asyncpg.Pool:
        if cls._pool is None:
            raise RuntimeError("Database pool not initialized. Call initialize() first.")
        return cls._pool
    
    @classmethod
    async def close(cls):
        if cls._pool:
            await cls._pool.close()
            cls._pool = None

class MQTTClient:
    _mqtt: Optional[FastMQTT] = None
    _database_client: Optional[DatabaseClient] = None

    @classmethod
    async def initialize(cls, db_client: DatabaseClient):
        if cls._mqtt is None:
            config = MQTTConfig(
                host=settings.MQTT_HOST,
                port=settings.MQTT_PORT,
                keepalive=60
            )

            cls._database_client = db_client
            cls._mqtt = FastMQTT(config=config)

            @cls._mqtt.on_connect()
            def connect_handler(client, flags, rc, properties):
                client.subscribe("#")
                print("Connected to broken and subscribed to all topics (#)")

            @cls._mqtt.on_message()
            async def message_handler(client, topic, payload, qos, properties):
                print(f"Accepted message from {client}")
                await cls._on_message_received(topic, payload)

            await cls._mqtt.mqtt_startup()

    @classmethod
    async def _on_message_received(cls, topic: str, payload: bytes):
        parts = topic.split('/')
        topic_objective = parts[1]

        # Debugger
        print(topic)
        print(topic_objective)
        if (topic_objective == 'test'):
            await MQTTHandler.read_topic_sensor(db_client=cls._database_client , topic=topic, payload=payload)

    @classmethod 
    async def close(cls):
        cls._mqtt.mqtt_shutdown()
        cls._mqtt = None

    @classmethod 
    def get_client(cls) -> FastMQTT:
        if cls._mqtt is None:
            raise RuntimeError("MQTTClient is not initialized. Call initialize() first.")
        return cls._mqtt
    
class HTTPClient:
    _client: httpx.AsyncClient = None

    @classmethod
    async def initialize(cls):
        cls._client = httpx.AsyncClient()

    @classmethod
    def get(cls) -> httpx.AsyncClient:
        return cls._client
    
    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.aclose()