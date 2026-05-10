from pydantic import BaseModel
from enum import Enum

class Classification(str, Enum):
    SAFE = "SAFE"
    CAUTION = "CAUTION"
    DANGER = "DANGER"

class SensorReading(BaseModel):
    device_id: str
    precipitation: float
    temperature: float
    humidity: float
    water_height: float
    water_height_change: float
    classification: Classification

    