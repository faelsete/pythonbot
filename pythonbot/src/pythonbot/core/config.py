import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base paths
BASE_DIR = Path.home() / ".pythonbot"
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"


class Settings(BaseSettings):
    # App config
    debug: bool = Field(default=False)

    # LLM Provider config
    llm_provider: str = Field(default="openrouter")
    llm_model: str = Field(default="openai/gpt-4o-mini")
    llm_api_key: str = Field(default="")
    llm_base_url: str = Field(default="https://openrouter.ai/api/v1")

    # Vision config
    vision_model: str = Field(default="")

    # Dashboard / API config
    api_host: str = Field(default="127.0.0.1")
    api_port: int = Field(default=8420)
    api_password: str = Field(default="pythonbot2026")

    # Telegram config
    telegram_bot_token: str = Field(default="")
    telegram_allowed_users: list[int] = Field(default_factory=list)

    # Feature toggles
    enable_voice: bool = Field(default=False)
    enable_stt: bool = Field(default=False)

    model_config = SettingsConfigDict(
        env_file=str(CONFIG_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


def get_settings() -> Settings:
    """Initialize settings and ensure base directories exist."""
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Create empty .env if not exists
    env_file = CONFIG_DIR / ".env"
    if not env_file.exists():
        env_file.touch()

    return Settings()


settings = get_settings()
