from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import RedirectResponse
from app.config import settings
from app.model.schema import DeviceRegister, DeviceValidate
from jose import jwt
from urllib.parse import urlencode
import bcrypt
import os
import httpx

# TODO Kelarin callback, google token exchange, token session creation, setup database pengguna, 
# Pembuatan dependency buat di gateway buat cek token, gateway reverse proxy

router = APIRouter(prefix="/auth", tags=['auth'])

DEVICES: dict = {}

@router.post("/register")
async def register(payload: DeviceRegister):
    if payload.device_id in DEVICES:
        raise HTTPException(status_code=400, detail="Device already registered")
    
    hashed = bcrypt.hashpw(payload.secret.encode(), bcrypt.gensalt())
    DEVICES[payload.device_id] = hashed

    return { "status": "registered", "device_id": payload.device_id}

@router.post("/validate")
async def validate(payload: DeviceValidate):
    hashed = DEVICES.get(payload.device_id)

    if not hashed:
        raise HTTPException(status_code=401, detail="Device not found")
    
    if not bcrypt.checkpw(payload.token.encode(), hashed):
        raise HTTPException(status_code=401, detail="Invalid token")
    
    return { "valid": True, "device_id": payload.device_id}

@router.get("/login")
async def login():
    query_params = {
        "client_id": settings.GOOGLE_CLIENT,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"{settings.GOOGLE_AUTH_URL}?{urlencode(query_params)}"
    return RedirectResponse(url)

# @router.get("/auth/callback")
# async def auth_callback(request: Request):
#     code = request.query_params.get("code")
#     if not code:
#         raise HTTPException(status_code=400, detail="Authorization code not found")

#     data = {
#         "code": code,
#         "client_id": settings.GOOGLE_CLIENT,
#         "client_secret": settings.GOOGLE_SECRET,
#         "redirect_uri": settings.GOOGLE_REDIRECT_URI,
#         "grant_type": "authorization_code"
#     }

#     async with httpx.AsyncClient() as client:
#         try:
#             res = await client.post()