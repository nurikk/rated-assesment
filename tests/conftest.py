import datetime
from contextlib import ExitStack
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from bytewax.testing import TestingSource
from sqlalchemy import StaticPool, create_engine
from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

from api.server import get_application
from common import db
from models import Base, ResourceStatisticsByDay


@pytest.fixture
def sync_engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def test_source():
    return TestingSource([
        '2024-09-01 02:59:35 cust_1 /api/v1/resource4 404 1.551',
        '2024-09-01 18:23:20 cust_2 /api/v1/resource2 201 0.869',
        '2024-09-02 14:17:43 cust_2 /api/v1/resource2 404 1.530',
        '2024-09-05 20:58:45 cust_1 /api/v1/resource1 201 0.293',
        'abc 20:58:45 corrupted /api/v1/resource1 200 0.293',
        '2024-09-05 20:58:45 corrupted /api/v1/resource1 abc 0.293',
        '2024-09-05 20:58:45 corrupted /api/v1/resource1 100 abc',
        'corrupted line',
        '',
        None,
        '2024-09-05 16:10:17 cust_1 /api/v1/resource1 200 0.651',
        '2024-09-05 18:15:32 cust_1 /api/v1/resource3 403 0.968',
        '2024-09-01 12:31:26 cust_1 /api/v1/resource3 500 0.899',
        '2024-09-10 07:37:24 cust_2 /api/v1/resource4 403 0.296',
        '2024-09-10 06:37:54 cust_2 /api/v1/resource4 500 0.284'
    ])


@pytest.fixture(autouse=True)
def app():
    with ExitStack():
        yield get_application()


@pytest_asyncio.fixture
async def session_fixture() -> AsyncGenerator[AsyncSession, None]:
    async_engine = create_async_engine(
        "sqlite+aiosqlite://",
        echo=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = async_sessionmaker(
        bind=async_engine, expire_on_commit=False
    )
    async with async_session_maker() as session:
        yield session


@pytest.fixture
def client(app, session_fixture):
    async def _get_test_db():
        try:
            yield session_fixture
        finally:
            pass

    app.dependency_overrides[db.get_db_session] = _get_test_db
    with TestClient(app) as c:
        yield c


@pytest_asyncio.fixture
async def sample_stats(session_fixture):
    await session_fixture.execute(
        insert(ResourceStatisticsByDay).values([
            {
                'customer_id': 'cust_1',
                'date': datetime.date(2024, 9, 1),
                'success_requests': 1,
                'failed_requests': 1,
                'duration_mean': 0.1,
                'duration_p50': 0.1,
                'duration_p99': 0.1,
            },
            {
                'customer_id': 'cust_1',
                'date': datetime.date(2024, 9, 2),
                'success_requests': 2,
                'failed_requests': 2,
                'duration_mean': 0.2,
                'duration_p50': 0.2,
                'duration_p99': 0.2,
            },
            {
                'customer_id': 'cust_1',
                'date': datetime.date(2024, 9, 3),
                'success_requests': 3,
                'failed_requests': 3,
                'duration_mean': 0.3,
                'duration_p50': 0.3,
                'duration_p99': 0.3,
            }
        ])
    )
