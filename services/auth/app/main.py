from fastapi import FastAPI
from routes import base
import os
import uvicorn

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

APP_MODULE = "main:app"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8001))
    reload = os.environ.get("ENV", "development") == "development"
    uvicorn.run(
        APP_MODULE,
        host="0.0.0.0",
        port=port,
        reload=reload
    )