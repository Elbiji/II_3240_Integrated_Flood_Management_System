from pydantic_settings import BaseSettings, SettingsConfigDict
import redis.asyncio as aioredis

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    AUTH_SERVICE: str
    MODEL_SERVICE: str
    ETL_SERVICE: str

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
            cls._client = None
    