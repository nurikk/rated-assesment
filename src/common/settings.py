from functools import lru_cache
from typing import Annotated

import pydantic_settings
from fastapi import Depends
from pydantic import PostgresDsn


class Settings(pydantic_settings.BaseSettings):
    DATABASE_URL: PostgresDsn


@lru_cache()
def get_settings():
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
