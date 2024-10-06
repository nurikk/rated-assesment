import os
import pathlib
from functools import lru_cache
from typing import Annotated

import pydantic_settings
from fastapi import Depends
from pydantic import PostgresDsn
DOTENV = os.path.join(os.path.dirname(__file__), "../../.env")


class Settings(pydantic_settings.BaseSettings):
    model_config = pydantic_settings.SettingsConfigDict(env_file=DOTENV)

    DATABASE_URL: PostgresDsn = "postgresql+psycopg://localhost:5432/rated"
    LOGS_SOURCE_DIR: pathlib.Path = "/tmp/logs"


@lru_cache()
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
