# net/api/settings.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "OHSUpath API"
    # Shared with the gateway; used for internal auth
    INTERNAL_SHARED_KEY: str = "dev-internal-key"

    # Read directly from environment variables
    # (uvicorn loads net/.env.api via --env-file)
    model_config = SettingsConfigDict(env_prefix="", extra="ignore")

settings = Settings()
