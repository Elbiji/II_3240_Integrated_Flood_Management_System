from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import base
from app.config import RedisClient
import redis.asyncio as aioredis
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    r = aioredis.from_url(
        os.environ.get("REDIS_URL","redis://localhost:6379")
    )
    RedisClient.set_redis(r)
    print("Connected to Redis")
    yield
    await RedisClient.close()
    print("Redis connection closed")

app = FastAPI(
    title="Integrated Flood System Gateway",
    description="API Gateway for Integrated Flood System",
    lifespan=lifespan
)

app.include_router(base.router)

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