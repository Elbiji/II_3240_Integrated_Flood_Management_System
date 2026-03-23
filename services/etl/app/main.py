from fastapi import FastAPI
from routes import base
import os
import uvicorn

app = FastAPI(
    title="ETL Service",
    description="API for ETL system"
)

app.include_router(base.router)

@app.get("/")
async def root():
    return {"message": "Hello from ETL service"}

@app.get("/health")
async def health():
    return {"stats": "ok"}

APP_MODULE = "main:app"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8003))
    reload = os.environ.get("ENV", "development") == "development"
    uvicorn.run(
        APP_MODULE,
        host="0.0.0.0",
        port=port,
        reload=reload
    )
