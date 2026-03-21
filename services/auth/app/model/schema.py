from pydantic import BaseModel

class DeviceRegister(BaseModel):
    device_id: str
    secret: str

class DeviceValidate(BaseModel):
    device_id: str
    token: str