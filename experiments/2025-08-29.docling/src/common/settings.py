from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings to be initialized with the app."""

    CLIENT_ID: str
    CLIENT_SECRET: str
    DATA_DIR: str
    TDCLI_EXEC: str
    LOG_LEVEL: str = Field("INFO", pattern=r"^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )
