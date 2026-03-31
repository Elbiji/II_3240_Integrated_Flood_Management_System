from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routes import base
from app.config import settings, RedisClient
import redis.asyncio as aioredis

@asynccontextmanager
async def lifespan(app: FastAPI):
    r = aioredis.from_url(settings.REDIS_URL)
    RedisClient.set_redis(r)
    print("Connected to Redis")
    yield
    await RedisClient.close()
    print("Redis connection closed")

app = FastAPI(
    title="Authentication Service",
    description="API for authentication system"
)

app.include_router(base.router)

@app.get("/")
async def root():
    return {"message": "Hello from Authentication service"}

@app.get("/health")
async def health():
    return {"status": "ok"}

# APP_MODULE = "main:app"

# if __name__ == "__main__":
#     port = int(os.environ.get("PORT", 8001))
#     reload = os.environ.get("ENV", "development") == "development"
#     uvicorn.run(
#         APP_MODULE,
#         host="0.0.0.0",
#         port=port,
#         reload=reload
#     )