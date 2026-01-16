from functools import lru_cache
from typing import List, Optional

from pydantic import HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    secret_key: str
    lichess_client_id: str
    lichess_redirect_uri: HttpUrl
    database_url: str
    redis_url: str
    
    redirect_url: str

    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    return Settings()
