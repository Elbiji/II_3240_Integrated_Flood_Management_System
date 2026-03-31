from pydantic import BaseModel

class DeviceRegister(BaseModel):
    device_id: str
    secret: str

class DeviceValidate(BaseModel):
    device_id: str
    token: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str | None = None

class User(BaseModel):
    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool | None = None
    