from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    GOOGLE_CLIENT: str
    GOOGLE_REDIRECT_URI: str
    GOOGLE_SECRET: str
    GOOGLE_AUTH_URL: str
    GOOGLE_TOKEN_URL: str
    TOKEN_EXPIRE: int

settings = Settings()