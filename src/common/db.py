import contextlib
from functools import lru_cache
from typing import Annotated, AsyncIterator, Any

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, AsyncConnection, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker, Session

from common.settings import get_settings

settings = get_settings()


@lru_cache
def get_engine():
    return create_engine(str(settings.DATABASE_URL), isolation_level="AUTOCOMMIT")


class DatabaseSessionManager:
    def __init__(self, host: str, engine_kwargs=None):
        if engine_kwargs is None:
            engine_kwargs = {}
        self._engine = create_async_engine(host, **engine_kwargs)
        self._sessionmaker = async_sessionmaker(autocommit=False, bind=self._engine)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")

        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@lru_cache
def get_async_session_maker():
    return DatabaseSessionManager(str(settings.DATABASE_URL), {"echo": True})


async def get_db_session():
    sessionmanager = get_async_session_maker()
    async with sessionmanager.session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_db_session)]
