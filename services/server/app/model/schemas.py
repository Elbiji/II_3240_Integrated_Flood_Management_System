from pydantic import BaseModel

class SensorReading(BaseModel):
    device_id: str
    water_level: float
    rainfall_rate: float
    timestamp: str