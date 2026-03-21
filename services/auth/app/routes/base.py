from fastapi import APIRouter, HTTPException
from model.schema import DeviceRegister, DeviceValidate
import bcrypt

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

