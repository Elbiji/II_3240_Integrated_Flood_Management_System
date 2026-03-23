from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=os.path.join(os.path.dirname(__file__), '../../..', '.env'))

    GOOGLE_API_WEATHER_KEY: str

settings = Settings()

