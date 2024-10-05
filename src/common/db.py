import os
from typing import Annotated

from fastapi import Depends
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession, AsyncEngine

from sqlalchemy.orm import sessionmaker

from common.settings import get_settings

settings = get_settings()

engine = AsyncEngine(create_engine(settings.DATABASE_URL, echo=True, future=True))


async def get_session() -> AsyncSession:
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]