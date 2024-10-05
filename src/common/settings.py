from functools import lru_cache
from typing import Annotated

import pydantic_settings
from fastapi import Depends
from pydantic import PostgresDsn


class Settings(pydantic_settings.BaseSettings):
    DATABASE_URL: str = "postgresql+psycopg://localhost:5432/rated"
    LOGS_SOURCE_DIR: str = "/tmp/logs"


@lru_cache()
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
