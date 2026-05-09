from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import web_handler
from app.config import RedisClient, DatabaseClient, MQTTClient, HTTPClient, settings
import redis.asyncio as aioredis
import logging

logger = logging.getLogger("uvicorn")

@asynccontextmanager
async def lifespan(app: FastAPI):
    r = aioredis.from_url(settings.REDIS_URL)
    RedisClient.set_redis(r)
    logger.info("Connected to Redis")

    await DatabaseClient.initialize(settings.DATABASE_URL)
    logger.info("Connected to TimescaleDB")

    await MQTTClient.initialize()
    logger.info("Connected to Mosquitto broker")

    await HTTPClient.initialize()
    logger.info("Internal HTTPClient created.")

    yield
    await RedisClient.close()
    print("Redis connection closed")
    await DatabaseClient.close()
    print("TimescaldeDB connection closed")
    await MQTTClient.close()
    print("Mosquitto connection closed")
    await HTTPClient.close()
    print("HTTPClient closed")


app = FastAPI(
    title="Integrated Flood System Gateway",
    description="API Gateway for Integrated Flood System",
    lifespan=lifespan
)

app.include_router(web_handler.router)

@app.get("/")
async def root():
    return { "message": "Integrated Flood System Gateway" }

@app.get("/health")
async def health():
    return { "status": "ok" }

# APP_MODULE = "main:app"

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8000))
#     reload = os.environ.get("ENV", "development") == "development"
#     uvicorn.run(APP_MODULE, host="0.0.0.0", port=port, reload=reload)